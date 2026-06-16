# CKB/CKB-VM 内存模型 W^X 的设计与演进

上一篇文章中, 我们学习了关于 CKB-VM 的[快照](./vm_snapshot_v2.md), 快照的核心工作之一是标记和保存"脏页". 那篇文章里反复提到页面的 flag 标记: `FLAG_DIRTY`, `FLAG_EXECUTABLE`, `FLAG_WRITABLE`... 但始终没有深入解释这些 flag 从何而来, 以及它们背后那个更根本的设计: 内存的 W^X 模型.

本文填补这个空白. 我们从 CKB-VM 内存子系统最底层的演进讲起, 到 W^X 的比特级设计, 再到它如何与 ELF 加载, 快照系统配合工作.

## 为什么要关心内存模型

区块链上的智能合约, 从安全角度看, 是一个极其恶劣的运行环境. 合约代码来自匿名用户, 节点必须在没有任何前提信任的情况下执行它, 并且执行结果必须可复现, 可验证. 这里随便列几条攻击面:

- 向代码段写入恶意指令, 然后跳转过去执行(代码注入)
- 利用已有的代码片段拼接出恶意逻辑(ROP/JOP)
- 通过巧妙的栈布局覆盖返回地址, 绕过权限检查

对于前两类攻击, 现代操作系统和浏览器早已给出了标准答案: [W^X](https://en.wikipedia.org/wiki/W%5EX)(Write XOR Execute). 即任何一页内存, 在同一时刻要么可写, 要么可执行, **绝对不可两者兼备**. 这个原则最早由 OpenBSD 在 2003 年引入, 随后被 Windows(DEP), Linux(PaX/NX), macOS 等几乎所有主流平台采纳.

对于 CKB-VM 这样的链上虚拟机而言, W^X 几乎是必选项. 没有它, 任何一个缓冲区溢出都可能被直接转化为远程代码执行.

> CKB-VM 还针对 ROP/JOP 设计了 CFI 扩展指令集, 目前仍在开发中. 可参阅[这篇文章](./vm_cfi.md)了解详情.

## 最简单的开始: FlatMemory

当你不需要考虑权限, 也不需要考虑内存效率时, 最直观的内存实现就是一块大数组. CKB-VM 在设计之初, 就有了一个叫 `FlatMemory` 的实现, 它直接用一个 4 MB 的 `Vec<u8>` 来模拟整个线性地址空间. 这个实现的好处是简单, 直接, 没有任何复杂的数据结构和算法; 坏处是浪费, 因为大多数脚本实际使用的内存远不到 4 MB.

```rs
pub struct FlatMemory<R> {
    data: Vec<u8>,        // 完整的 4 MB 字节数组
    flags: Vec<u8>,       // 每页一个 flag 字节
    memory_size: usize,   // 总大小, 默认 4 MB
    // ...
}
```

`FlatMemory` 在构造时就使用了 `vec![0; memory_size]`, 一次性分配全部 4 MB. 它提供最基础的读写接口, 写操作自动置位 `FLAG_DIRTY`, 除此之外没有做任何权限检查. 它存在的意义是作为一个正确且简单的参考后端, 供解释器模式使用, 也为后续的更复杂实现提供对照基准.

> 在早期的 CKB-VM 版本中, 解释器模式就运行在 FlatMemory 上. 后来为了统一权限模型, 所有后端都切换到了 WXorXMemory 包裹 SparseMemory 的组合.

## 从 Flat 到 Sparse: 按需分配

FlatMemory 简单, 但有一个明显的浪费: 大多数 CKB 脚本实际使用的内存远不到 4 MB. 一个典型的签名验证脚本可能只用到几十 KB. FlatMemory 在构造时就把 4 MB 全部分配, 这意味着每台 CKB 节点上, 每个脚本执行线程都要吞掉 4 MB 物理内存. 当节点并发执行数百个脚本时, 内存压力就上来了.

`SparseMemory` 解决的就是这个问题:

```rs
pub struct SparseMemory<R> {
    indices: Vec<u16>,    // 每页的索引表, 未分配页为 INVALID_PAGE_INDEX(0xFFFF)
    pages: Vec<Page>,     // 实际分配的页列表
    flags: Vec<u8>,       // 每页 flag, 不论是否分配都存在
    // ...
}
```

核心思路是延迟分配: 构造时只创建空的索引表和 flags 表, 不分配任何数据页. 当虚拟机首次访问某页时, `fetch_page` 才会在 `pages` 中追加一个新页, 并将索引记录到 `indices` 中.

```rs
fn fetch_page(&mut self, aligned_addr: u64) -> Result<&mut Page, Error> {
    let page = aligned_addr / RISCV_PAGESIZE as u64;
    let mut index = self.indices[page as usize];
    if index == INVALID_PAGE_INDEX {
        self.pages.push([0; RISCV_PAGESIZE]);
        index = (self.pages.len() - 1) as u16;
        self.indices[page as usize] = index;
    }
    Ok(&mut self.pages[index as usize])
}
```

这个设计的额外开销是 `indices` 表: 每个页占 2 字节(u16), 对于 4 MB 内存(1024 页), 约 2 KB. 考虑到它省下的物理内存, 这笔开销微乎其微.

值得注意的一点是, `flags` 表在 SparseMemory 中仍然是完整分配的, 不论页是否被分配, flag 都立即可查. 这是有意为之: 权限检查发生在内存访问之前, 如果 flag 表本身也要延迟分配, 就会在权限判断和页分配之间引入鸡生蛋的循环依赖.

> `SparseMemory` 同样不包含权限检查逻辑. 和 `FlatMemory` 一样, 它只负责数据存取, 权限交给上层的 WXorXMemory 负责. 这种关注点分离是 CKB-VM 内存子系统最核心的设计原则.

## W^X 登场: WXorXMemory

现在来到本文的主角. `WXorXMemory` 是一个泛型 wrapper, 包裹任意一个 `Memory` 实现(实践中始终是 `SparseMemory`), 在它的读写路径上插入 W^X 权限校验.

```rs
pub struct WXorXMemory<M: Memory> {
    inner: M,
}
```

它是 Rust 中经典的"装饰器模式". 大多数方法(如 `load8`, `load16`, `fetch_flag`)直接透传给 `inner`; 只有写操作和指令取指操作被拦截, 在透传之前先做权限检查.

```rs
fn store8(&mut self, addr: &Self::REG, value: &Self::REG) -> Result<(), Error> {
    check_no_overflow(addr.to_u64(), 1, self.memory_size() as u64)?;
    let page_indices = get_page_indices(addr.to_u64(), 1);
    check_permission(self, &page_indices, FLAG_WRITABLE)?;  // <-- W^X 检查
    self.inner.store8(addr, value)
}

fn execute_load16(&mut self, addr: u64) -> Result<u16, Error> {
    check_no_overflow(addr, 2, self.memory_size() as u64)?;
    let page_indices = get_page_indices(addr, 2);
    check_permission(self, &page_indices, FLAG_EXECUTABLE)?; // <-- W^X 检查
    self.inner.execute_load16(addr)
}
```

注意 `execute_load16` 和 `execute_load32` 是两个**独立于普通 load 的方法**. 普通 load(如 `load8`/`load16`/`load32`/`load64`)用于执行 `lb`/`lw` 等数据访存指令, 它们不检查 `FLAG_EXECUTABLE`; 而 `execute_load16`/`execute_load32` 专门用于取指(instruction fetch), 读取的是"压缩指令"的 16 位或 32 位编码. **取指走可执行检查, 数据访存走可写检查. 两者互斥而互补.**

接下来是我认为整个实现中最精妙的部分. 翻开源码, 四个 flag 常量是这样定义的:

```rs
pub const FLAG_FREEZED:    u8 = 0b01;
pub const FLAG_EXECUTABLE: u8 = 0b10;
pub const FLAG_WXORX_BIT:  u8 = 0b10;  // 与 FLAG_EXECUTABLE 相同
pub const FLAG_WRITABLE:   u8 = (!FLAG_EXECUTABLE) & FLAG_WXORX_BIT;
pub const FLAG_DIRTY:      u8 = 0b100;
```

先看 `FLAG_WRITABLE` 的值. `!FLAG_EXECUTABLE` 对所有位取反, 在 8 位空间中等于 `0b11111101`. 再与 `FLAG_WXORX_BIT`(0b10) 做按位与, 结果是 `0b00000000`, 也就是 0.

这意味着 **FLAG_WRITABLE 等于 0**. 一页"可写"的标志是该页的 bit 1 为 0; "可执行"的标志是 bit 1 为 1. 同一 bit 的两个取值, 恰好穷尽了 W 和 X 两种状态.

有了这层设计, W^X 检查就变得极其简洁:

```rs
pub fn check_permission<M: Memory>(
    memory: &mut M,
    page_indices: &(u64, u64),
    flag: u8,
) -> Result<(), Error> {
    for page in page_indices.0..=page_indices.1 {
        let page_flag = memory.fetch_flag(page)?;
        if (page_flag & FLAG_WXORX_BIT) != (flag & FLAG_WXORX_BIT) {
            return Err(Error::MemWriteOnExecutablePage(page));
        }
    }
    Ok(())
}
```

逐一分析三种场景:

|  操作  |        flag 参数        | `flag & 0b10` | 页为可写(bit1=0) | 页为可执行(bit1=1)  |
| ------ | ----------------------- | ------------- | ---------------- | ------------------- |
| 写操作 | `FLAG_WRITABLE`(0)      | `0`           | `0 == 0` 放行    | `0b10 != 0` 拒绝    |
| 取指   | `FLAG_EXECUTABLE`(0b10) | `0b10`        | `0 != 0b10` 拒绝 | `0b10 == 0b10` 放行 |

不需要两条独立的检查路径, 不需要 if-else 分支判断"是写还是执行", 一个比特比较就搞定了全部四种组合. 这种用一个 bit 编码互斥状态的设计, 在硬件描述语言中很常见, 但在软件实现中却不多见. 它的优点是极简高效, 缺点是可读性稍差(需要理解这个设计背后的逻辑). 不过一旦理解了, 就会觉得它非常 elegant.

## 页的冻结: FLAG_FREEZED

除了 W^X, 还有一个重要的保护机制: `FLAG_FREEZED`. bit 0 如果置为 1, 表示该页已经被冻结, 后续不允许再修改. 冻结发生在 `WXorXMemory::init_pages` 中:

```rs
fn init_pages(&mut self, addr: u64, size: u64, flags: u8, ...) -> Result<(), Error> {
    for page_addr in (addr..addr + size).step_by(RISCV_PAGESIZE) {
        let page = page_addr / RISCV_PAGESIZE as u64;
        if self.fetch_flag(page)? & FLAG_FREEZED != 0 {
            return Err(Error::MemWriteOnFreezedPage(page));
        }
        self.set_flag(page, flags)?;
    }
    self.inner.init_pages(addr, size, flags, source, offset_from_addr)
}
```

冻结是对 W^X 的补充: W^X 保证一页不会同时可写和可执行, 但不保证一页不会在"先写后执行"之间切换. 冻结解决了这个时间维度的漏洞: 代码段和只读数据段在 ELF 加载时就被冻结, 随后任何修改它的尝试都会触发 `MemWriteOnFreezedPage` 错误.

## ELF 加载: flag 从哪来

一个 RISC-V ELF 文件中, 每个段(segment)都有 `p_flags` 字段, 用 `PF_R`, `PF_W`, `PF_X` 三个 bit 表示可读, 可写, 可执行. ELF 加载器将其转换为 CKB-VM 的页面 flag:

```rs
pub fn convert_flags(p_flags: u32, allow_freeze_writable: bool, vaddr: u64) -> Result<u8, Error> {
    let readable = p_flags & PF_R != 0;
    let writable = p_flags & PF_W != 0;
    let executable = p_flags & PF_X != 0;
    if !readable {
        return Err(Error::ElfSegmentUnreadable(vaddr));
    }
    if writable && executable {
        return Err(Error::ElfSegmentWritableAndExecutable(vaddr));
    }
    if executable {
        Ok(FLAG_EXECUTABLE | FLAG_FREEZED)
    } else if writable && !allow_freeze_writable {
        Ok(0)
    } else {
        Ok(FLAG_FREEZED)
    }
}
```

转换规则:

- **不可读的段**: 直接拒绝. 在 CKB-VM 中不存在不可读的内存.
- **同时可写且可执行的段**: 直接拒绝. 这违反了 W^X 原则.
- **代码段(`PF_X`)**: 得到 `FLAG_EXECUTABLE | FLAG_FREEZED`. 冻结后不可修改.
- **数据段(`PF_W`)**: 得到 `0`(即 `FLAG_WRITABLE`). 不冻结, 允许脚本运行时修改.
- **只读数据段(既非 X 也非 W)**: 得到 `FLAG_FREEZED`. 冻结以防止运行时篡改.

注意 `writable && !allow_freeze_writable` 这条路径返回 `0`, 这意味着可写段在初始状态下**不被冻结**. 如果 `allow_freeze_writable` 为 true(某些特定场景), 则可写段也会被冻结, 此时它变成了一个"初始化后可读但不可再写"的区域, 类似于 `.data.rel.ro`.

当 ELF 中出现 `PF_W | PF_X` 的段时, CKB-VM 拒绝加载. 这是从入口处就掐断了 W^X 违规的可能.

## 与快照系统的交互

快照需要保存 dirty 页及其 flag, 恢复时需要完整复原. 快照 V1 的方法是直接保存 dirty 页的 flag 字节, 恢复时 `set_flag` 写回. 快照 V2 在此基础上引入了 DataSource 抽象, 但 flag 的保存和恢复逻辑不变.

W^X 在快照恢复时并不需要额外处理, 因为恢复后的页面 flag 应当与挂起前完全一致. 唯一需要注意的是, `resume` 恢复 dirty 页时调用的是 `memory_mut().store_bytes(...)`, 而这个路径在 WXorXMemory 中会触发 `check_permission`. 如果某页在挂起前是可执行的, 那么这个 store 调用就会因为 W^X 检查而失败. 但实际上快照恢复发生在新的虚拟机刚加载完 ELF 之后(此时代码段已经被正确标记为 executable), V1 恢复的 dirty 页应该全是数据页(标记为 writable), 因此不会触发冲突.

## 内存操作的性能

W^X 检查的性能开销主要来自于每次内存访问前的 flag 读取和 bit 比较. 由于 flag 是按页存储的, 每次访问需要计算对应页的索引, 读取 flag 字节, 再进行 bit 运算. 这个过程相对于实际的数据读写来说是一个额外的步骤. 不过由于 flag 存储在内存中, CPU 的缓存机制会大大减少这个开销. 实际测试表明, W^X 检查的性能影响在可接受范围内, 远小于潜在的安全风险.

CKB-VM 的 x64 ASM 后端在实现上对 W^X 检查做了优化, 相比较 Rust 解释器实现, 大幅减少了热路径上的开销. 如果只看 Rust 代码, 很容易把 W^X 开销理解为一个抽象的 `check_permission` 调用. 但在 x64 ASM 后端里, 它被展开成了真实的指令序列. 以 [src/machine/asm/execute_x64.S](https://github.com/nervosnetwork/ckb-vm/blob/develop/src/machine/asm/execute_x64.S) 中的 `CHECK_WRITE` 宏为例, `sb/sh/sw/sd` 等写内存指令都会先执行这段逻辑.

写入操作一般存在空间局部性, 也就是程序倾向于在同一页内连续写入. x64 后端针对这个场景做了一个小优化: 维护一个 `last_write_page` 寄存器, 记录上一次写操作的页索引. 当下一次写操作发生时, 先比较当前写地址所在页与 `last_write_page` 是否相同, 如果相同且没有跨页, 就直接跳过权限检查. 只有当写入跨页或者首次写该页时, 才执行完整的权限检查流程.

1. 计算当前写地址所在页(`shr PAGE_SHIFTS`)
2. 与 `last_write_page` 比较
3. 再计算 `addr + len` 的结束页, 确认没有跨页
4. 若两次比较都命中, 直接跳过权限检查

这条快路径本质上是页级缓存: 当程序在同一页内连续写入时, 大多数写指令只多了几条整数指令和两个分支判断, 不会重复读取 flag, 也不会重复置 dirty.

再看慢路径(跨页或首次写该页):

1. 读取 `flags[page]`
2. 执行 `and WXORX_BIT` + `cmp WRITABLE`
3. 不匹配则跳转 `.exit_invalid_permission`
4. 匹配则 `or DIRTY` 并写回 flag
5. 检查对应 frame 是否已初始化, 必要时调用 `inited_memory`
6. 若跨页, 对下一页重复一次同样流程

也就是说, W^X 真正的额外成本主要集中在页切换点而不是每一条 store 指令. 连续顺序写的场景会被 `last_write_page` 明显摊薄.

另外一个很关键的观察是: 在 ASM 的执行循环中, 看不到针对 `FLAG_EXECUTABLE` 的逐条取指检查. `NEXT_INST` 直接在已解码 trace 中跳转执行, 因此 x64 后端把可执行权限成本尽量前移到了 trace/解码阶段, 而运行时热点里主要留下的是写路径的 W^X 校验.

综合来看, x64 指令层面的 W^X 开销呈现出两个特征:

- **均摊后低开销**: 同页连续写时, 额外成本接近常数级的小分支开销.
- **边界敏感**: 跨页写和首次触达页会触发完整检查链, 成本显著高于快路径.

如果观察源代码, 我们可以看到内存读写操作所涉及的指令数量要远远超过简单的计算指令(例如 add, sub 等), 那么内存读写的性能具体如何, 我们可以通过基准测试来量化. 下面是一个简单的基准测试示例, 测试连续单页写入和 add 指令的性能差异:

```text
/* Test sd */
.global _start
_start:
    la t0, 1
    li t1, 100000
loop:
    sd zero, 0(t0) /* Repeat 10000 times */

    addi t1, t1, -1
    bnez t1, loop

    li a0, 0
    li a7, 93
    ecall
.section .data
n0:
    .dword 0
```

```sh
$ time ./target/release/examples/ckb_vm_runner --mode asm64 test_sd
asm64 exit=Ok(0) cycles=2000700501 r[a1]=0

real    0m12.827s
user    0m12.549s
sys     0m0.018s
```

```text
/* Test add */
.global _start
_start:
    la t0, 1
    li t1, 100000
loop:
    add t0, t0, t0 /* Repeat 10000 times */

    addi t1, t1, -1
    bnez t1, loop

    li a0, 0
    li a7, 93
    ecall
```

```sh
$ time ./target/release/examples/ckb_vm_runner --mode asm64 test_add
asm64 exit=Ok(0) cycles=1000700501 r[a1]=0

real    0m2.029s
user    0m1.969s
sys     0m0.003s
```

可以看到, 在两者 cycles 相同的情况下, 单页连续内存写入的实际耗时是 add 指令的 3 倍左右, 这在模拟器中是完全可以接受的. 但如果跨页写入, 由于触发了完整的 W^X 检查链, 性能可能会下降到 add 指令的 5 倍甚至更多. 因此在编写 CKB 脚本时, 尽量更多使用连续内存访问, 避免跨页写入, 可以在一定程度上降低 W^X 检查带来的性能开销.

## 总结

CKB-VM 内存模型的核心是三样东西: FlatMemory 的正确性, SparseMemory 的效率, WXorXMemory 的安全性. 三者分层叠加, 各司其职.

W^X 本身不是什么新技术, 它已经保护了我们日常使用的操作系统和浏览器超过二十年. 但在区块链虚拟机的语境下, 它从最佳实践变成了生存必需的底线. 任何人都能把代码部署到链上, 任何人都能尝试攻击你的合约. 在这样的对抗环境下, 内存模型的设计容不得半点妥协.
