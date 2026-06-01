# CKB/CKB-VM Snapshot V1

## 背景

CKB 节点在收到一笔新交易后需要执行其中的脚本来完成验证. 脚本是用户提供的图灵完备程序, 单次执行所消耗的算力可大可小: 一个简单的签名校验可能只需要几百万 cycles, 而一个复杂的零知识证明验证则可能消耗数十亿 cycles. 如果节点用同一个线程不加区分地处理所有交易, 一笔"大脚本"就足以把这个线程长时间占满, 让随后到达的新区块得不到及时验证.

为此, CKB 节点在交易池层面设计了两条执行队列: 普通脚本队列和大脚本队列. 新交易首先进入普通队列, 由若干工作线程并发执行; 一旦某笔交易在普通队列中累计消耗的 cycles 超过预设阈值, 节点就把它从普通队列中摘下, 转移到专门的大脚本队列中继续跑. 这样设计的好处是普通队列里的线程不会被个别"长任务"长期占据, 节点始终保留足够的算力来响应新区块.

这套机制能跑通的关键, 是脚本在被**移动**的瞬间必须能完整地把执行状态带走, 之后在另一条队列里无缝接续, 既不能从头重算, 也不能丢失任何中间结果. Snapshot 正是为此而生的: 当虚拟机即将达到当前队列允许的 cycles 上限时, 将其完整执行状态序列化下来; 之后在大脚本队列里用新的预算从这份快照恢复出一个等价的虚拟机, 继续未完成的工作. 整个过程对脚本而言是透明的, 脚本不需要感知自己被挂起和恢复.

本文介绍 CKB-VM 中 Snapshot V1 的实现, 源代码位于 [src/snapshot.rs](https://github.com/nervosnetwork/ckb-vm/blob/develop/src/snapshot.rs).

## 需要保存哪些状态

一个 RISC-V 虚拟机的执行状态可以拆解为三部分: 寄存器组, 程序计数器, 以及内存. Snapshot V1 在此基础上还额外保存了原子指令使用的保留地址(load reservation address), 用于支持 A 扩展中的 `lr`/`sc` 指令对(目前并未在主网使用).

寄存器和 PC 的体量很小, 完整保存即可; 真正需要权衡的是内存. CKB-VM 默认提供 4 MB 的线性内存空间, 若每次快照都把全部内存原封不动地序列化, 既浪费空间也浪费时间. 实际上, 一个脚本在执行过程中真正写入过的内存通常只占很小一部分, 我们只需保存这部分"脏页"即可.

CKB-VM 的内存以页(page)为粒度管理, 每页 4 KB. 每一页都附带一个 flag 字节, 其中 `FLAG_DIRTY` 比特用来标记该页是否被写入过. 内存子系统在每次写操作时自动置位该 flag. 在 `machine.load_elf` 加载完 ELF 之后, CKB-VM 会清除所有 dirty 标记, 这样脚本运行期间出现的 dirty 页就恰好对应程序运行过程中修改过的页面, 也就是快照需要保存的页面.

## 数据结构

`Snapshot` 是一个可序列化的结构体, 其定义如下:

```rs
#[derive(Default, Deserialize, Serialize)]
pub struct Snapshot {
    pub version: u32,
    pub registers: [u64; RISCV_GENERAL_REGISTER_NUMBER],
    pub pc: u64,
    pub page_indices: Vec<u64>,
    pub page_flags: Vec<u8>,
    pub pages: Vec<Vec<u8>>,
    pub load_reservation_address: u64,
}
```

各字段含义:

- `version`: 虚拟机版本号, 用于恢复时校验.
- `registers`: 32 个 RISC-V 通用寄存器.
- `pc`: 程序计数器.
- `page_indices`: 脏页的页号列表.
- `page_flags`: 与 `page_indices` 一一对应的页 flag.
- `pages`: 与 `page_indices` 一一对应的页内容, 每页 4 KB.
- `load_reservation_address`: A 扩展使用的保留地址.

三个 `Vec` 字段以平铺数组的形式存储脏页信息, 而不是封装成 `Vec<(u64, u8, Vec<u8>)>`, 这样在 serde 序列化后结构更紧凑.

## 创建快照

`make_snapshot` 函数从一个运行中的虚拟机生成快照, 核心逻辑分为两步: 先复制寄存器与 PC, 再遍历内存页面提取脏页.

```rs
pub fn make_snapshot<T: CoreMachine>(machine: &mut T) -> Result<Snapshot, Error> {
    let mut snap = Snapshot {
        version: machine.version(),
        pc: machine.pc().to_u64(),
        load_reservation_address: machine.memory().lr().to_u64(),
        ..Default::default()
    };
    for (i, v) in machine.registers().iter().enumerate() {
        snap.registers[i] = v.to_u64();
    }

    for i in 0..machine.memory().memory_pages() {
        let flag = machine.memory_mut().fetch_flag(i as u64)?;
        if flag & FLAG_DIRTY != 0 {
            let addr_from = i << RISCV_PAGE_SHIFTS;
            let addr_to = (i + 1) << RISCV_PAGE_SHIFTS;
            let mut page = vec![0; RISCV_PAGESIZE];
            for i in (addr_from..addr_to).step_by(8) {
                let v64 = machine
                    .memory_mut()
                    .load64(&T::REG::from_u64(i as u64))?
                    .to_u64();
                // ... 拆字节写入 page
            }
            snap.page_indices.push(i as u64);
            snap.page_flags.push(flag);
            snap.pages.push(page);
        }
    }
    Ok(snap)
}
```

值得关注的细节有两点:

第一, 遍历内存时不是直接 `memcpy`, 而是以 8 字节为步长调用 `load64`. 这是因为 `CoreMachine` trait 抽象了不同的后端(纯 Rust 解释器, ASM 后端, AOT 后端等), 各后端的内存布局并不相同, 唯一通用的读取入口是 `load*` 系列方法. 通过 `load64` 读取再拆为 8 个字节, 可以保证快照逻辑对所有后端一视同仁.

第二, 这里只关心 `FLAG_DIRTY` 标志位, 但保存的是整个 flag 字节, 这样在恢复时可以一并还原页的其它属性(如可执行, 可写等).

## 恢复快照

函数 `resume` 将快照灌入一个新的虚拟机. 调用者通常会先用相同的 ELF 重新 `load_elf` 一次, 此时所有静态数据页都已就位且 dirty 标记被清零; 随后 `resume` 在此基础上把脏页打补丁上去, 即可还原出与挂起时等价的状态.

```rs
pub fn resume<T: CoreMachine>(machine: &mut T, snapshot: &Snapshot) -> Result<(), Error> {
    if machine.version() != snapshot.version {
        return Err(Error::InvalidVersion);
    }
    for (i, v) in snapshot.registers.iter().enumerate() {
        machine.set_register(i, T::REG::from_u64(*v));
    }
    machine.update_pc(T::REG::from_u64(snapshot.pc));
    machine.commit_pc();
    for i in 0..snapshot.page_indices.len() {
        let page_index = snapshot.page_indices[i];
        let page_flag = snapshot.page_flags[i];
        let page = &snapshot.pages[i];
        let addr_from = page_index << RISCV_PAGE_SHIFTS;
        machine.memory_mut().store_bytes(addr_from, &page[..])?;
        machine.memory_mut().set_flag(page_index, page_flag)?;
    }
    machine
        .memory_mut()
        .set_lr(&T::REG::from_u64(snapshot.load_reservation_address));
    Ok(())
}
```

第一步是版本校验: 如果快照来自一个版本不同的虚拟机, 直接返回 `InvalidVersion` 错误. CKB-VM 不同硬分叉版本的指令解码与执行行为存在差异, 跨版本恢复可能导致难以察觉的语义错误, 因此宁可拒绝.

随后依次回写寄存器, PC 和脏页. `update_pc` + `commit_pc` 是 CKB-VM 中固定的 PC 更新模式: `update_pc` 写入下一条指令地址, `commit_pc` 将其提升为当前 PC, 这样设计是为了配合解释器循环中"先取指再提交"的执行模型.

## 局限

Snapshot V1 的实现简单直接, 但有一个明显的弱点: 它对"什么是脏页"的定义比较粗糙. 任何被写入过的页面都会被完整地保存到快照中, 哪怕其中绝大部分字节其实是从只读数据段或交易 witness 加载过来的, 内容在链上其它地方已经存在.

对于一些数据量大的场景(例如脚本通过 syscall 把整段 witness 加载到内存里), V1 快照会非常臃肿. 为此 CKB-VM 后续引入了 Snapshot V2.

V2 的具体实现留待下一篇详述. 不过即便在 V2 出现之后, V1 仍然作为最基础, 最自包含的快照格式被保留下来, 适用于不依赖外部数据源的场景.
