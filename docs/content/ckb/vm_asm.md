# CKB/CKB-VM: 深入了解汇编执行器的实现

2026 年初, 我们为 CKB-VM 引入了第三个汇编执行后端: [riscv64](https://github.com/nervosnetwork/ckb-vm/pull/502). 加上此前的 [x64](https://github.com/nervosnetwork/ckb-vm/blob/develop/src/machine/asm/execute_x64.S) 和 [aarch64](https://github.com/nervosnetwork/ckb-vm/blob/develop/src/machine/asm/execute_aarch64.S), CKB-VM 现在可以在三种主流 CPU 架构上以手工汇编的方式执行 RISC-V 程序. 三条不同的系统架构路线走下来之后, 这套设计的核心思想已经非常清晰, 值得完整地梳理一次.

本文从 CKB-VM 汇编执行器的设计动机出发, 依次覆盖 trace 机制, 寄存器分配, 内存模型等技术细节. 希望读完后, 你能对 CKB-VM 的汇编执行器形成一个完整认知.

## 为什么还需要汇编执行器

CKB-VM 是一个 RISC-V 虚拟机. 最直观的实现当然是解释器: 取指, 解码, 执行, 更新 PC, 循环. 这个模型足够简单, 天然适合作为正确性的黄金参考.

但问题是: 对链上脚本来说, 单条 RISC-V 指令的工作量太小了. 例如一条 `add` 只是把寄存器加上另一个寄存器再写回, 宿主 CPU 一两条指令就能完成的计算, 解释器却要穿越 Rust 的 loop 和 match 分支, 读寄存器数组, 判断 `x0` 是否为写入目标, 累加 cycles 计数, 再跳回循环顶部. 几千万次这样的往返之后, 固定开销累积到了不可忽视的量级.

解释器优化的经典主题之一是**减少分发**. 把最热的循环路径从高级语言下沉到汇编, 省掉每一层不必要的抽象. 这就是 ASM 后端的根本动机.

> 减少分发是经典的解释器优化方案, 您可以在 LuaJIT, Python 等解释器语言中大量见到. 常见策略包括自适应求值(Adaptive/Tiered Interpreters), 字节码合并(Superinstructions/Macro OP), 直接线程化代码(Direct Threaded Code)等.

不过要先澄清一个容易产生的误解: CKB-VM 的 ASM 后端不是 JIT. 它永远不会把用户的 RISC-V 程序翻译成新的宿主机器码. 它仍然是解释器, 只不过把调度循环, 寄存器读写, 内存权限检查等热点路径交给了手工汇编代码.

## Trace: 一次解码, 多次执行

传统解释器的骨架长这样:

```rust
loop {
    let inst = fetch_instruction();
    match inst.opcode() {
        OP_ADD => { /* ... */ }
        OP_SUB => { /* ... */ }
        OP_MUL => { /* ... */ }
        // ... 数百多个分支
    }
}
```

它本质上是一个巨大的循环包裹着一个巨大的 match. 问题不只在于 match 的分支数量, 更在于 CPU 的分支预测器几乎无法在这样一张跳转表上做有效预测. 每一次从 `OP_ADD` 执行完毕再跳回循环顶部的 `match`, 都是一次潜在的流水线冲刷.

> 站在专业角度来讲, 解释器的中央分发机制会产生多对一的控制流汇聚(Many-to-One Jump), 从而打破了底层硬件分支预测器所依赖的模式规律. 它有两个主要问题:
>
> 单点出口的灾难(Single Exit Disaster): 在解释器的执行循环中, 所有的字节码指令最终都通过同一个 match 分支或 switch-case 语句进行状态分发. 从 CPU 分支预测器的视角来看, 这个跳转指令的来源地址始终只有一个, 但它的目标地址却可能是代码中的任何一个字节码处理逻辑.
>
> 多态分支混淆(Aliasing): 现代 CPU 的预测器(如 TAGE 或 Perceptron)依赖分支历史表(BHT)和分支目标缓冲(BTB)来预测走向. 当同一个跳转指令不断在数十甚至数百种不同的状态间随机切换时, 预测器无法提取出稳定的历史模式(如交替或循环模式), 导致预测准确率断崖式下跌. 每次预测失败都会导致长达 10 到 20 个周期的流水线冲刷(Pipeline Flush).

LuaJIT 的作者 Mike Pall 提出了一个朴素的思路: 与其每次执行都重新匹配 opcode, 不如把经常顺序执行的指令序列**录制**下来. 这段预先解码好的线性序列叫做 trace. 有了 trace 之后, 执行路径就不再是 loop -> match -> opcode_handler -> loop, 而是沿着预先排好的标签链条直接往前跳.

用伪代码描述这个过程:

```text
OP_CUSTOM_TRACE_END:
    trace = fetch_trace(pc)          // 例如 [OP_ADD, OP_SUB, OP_MUL, OP_CUSTOM_TRACE_END]
    index = 0
    goto trace[index].label          // 跳到 OP_ADD

OP_ADD:
    index += 1
    handle_add(trace[index].args)    // 执行 OP_ADD
    goto trace[index].label          // 跳到 OP_SUB

OP_SUB:
    index += 1
    handle_sub(trace[index].args)    // 执行 OP_SUB
    goto trace[index].label          // 跳到 OP_MUL

OP_MUL:
    index += 1
    handle_mul(trace[index].args)    // 执行 OP_MUL
    goto trace[index].label          // 跳回 OP_CUSTOM_TRACE_END, 开始取下一段 trace
```

LuaJIT 在拿到 trace 后会进一步编译成机器码. CKB-VM 不编译, 但它借用了同样的前置步骤: 在 Rust 侧把一段指令预先解码, 构建 trace. 每条 trace 条目包含两个 `u64`, 在 CKB-VM 里这两个数字叫做 thread:

|      偏移      |        内容         |                          含义                           |
| -------------- | ------------------- | ------------------------------------------------------- |
| `thread[2n]`   | label address       | 宿主汇编标签的绝对地址, 例如 `.CKB_VM_ASM_LABEL_OP_ADD` |
| `thread[2n+1]` | decoded instruction | 已解码的指令参数, 寄存器编号和立即数都已经萃取完毕      |

在汇编执行器内部, 这份数据结构被两个指针驱动:

- `INST_PC`: 指向当前 thread 的 label address.
- `INST_ARGS`: 指向当前 thread 的 decoded instruction.

每执行完一条指令, `NEXT_INST` 宏把两个指针各推进 16 字节(即一个 trace 条目), 然后通过 `jmp *INST_PC` 直接跳向下一条指令的汇编标签. 只需要简单几条指令, 完成了一轮 dispatch. 没有循环, 没有 match, 没有分支预测的压力. 原来每条指令都要付出的解码和分发成本, 被提前折叠进了 trace 构建阶段. 执行阶段只剩下取出地址, 跳转.

**源码阅读**

- <https://github.com/nervosnetwork/ckb-vm/blob/develop/src/machine/asm/traces.rs>
- <https://github.com/nervosnetwork/ckb-vm/blob/develop/src/machine/asm/execute_x64.S>

Trace 的设计是 CKB-VM ASM 执行器的基础, 也是整个项目里比较难理解的一部分.

## Trace: Fixed 与 Dynamic

CKB-VM 的 trace 系统有两个层级.

**Fixed Trace** 是默认实现. 它在内存中维护一张大小为 8192 的哈希表, 通过 `slot = (PC >> 2) & 8191` 定位槽位. 每个槽位是一个 `FixedTrace` 结构, 最多容纳 16 条指令(加上末尾的 `OP_CUSTOM_TRACE_END`, 共 17 个 thread). 当程序在一个基本块内执行时, 这些指令恰好被一起解码, 一起执行, 直到遇到分支或 trace 结束.

Fixed trace 在大多数场景下足够了. 但对于较长的顺序代码块, 16 条指令的容量可能不够. 这时 trace decoder 有两种应对策略:

1. 如果后面没东西了, 就正常结束, 下次回到 `OP_CUSTOM_TRACE_END` 重新查表.
2. 如果后面还有连续指令(即当前解码到的指令不是基本块结束指令), decoder 会构建一个 **Dynamic Trace**.

Dynamic Trace 是一个使用 [flexible array member](https://en.wikipedia.org/wiki/Flexible_array_member) 的动态长度结构, 可以把整段长顺序代码一口气全部编码进去, 不限 16 条. 它在汇编层看起来和 FixedTrace **一模一样**: 前面是 `address`, `length`, `cycles`, 后面是同样格式的 thread 序列.

两者的衔接方式是: fixed trace 的最后一个 thread 被替换为 `OP_CUSTOM_ASM_TRACE_JUMP`, 其参数就是 dynamic trace 的完整地址. 汇编执行器识别到这个 opcode 后, 直接把 `TRACE` 指针切换到 dynamic trace, 然后复用同一套 `.trace_loaded` 逻辑. Rust 侧构建了两套不同的数据结构, 但汇编侧看到的是一个统一的形状.

> 这个统一性的关键设计在于: DynamicTrace 的前三个字段与 FixedTrace 有着完全相同的内存布局, 汇编代码通过同样的 offset 宏(`CKB_VM_ASM_TRACE_OFFSET_ADDRESS`, `CKB_VM_ASM_TRACE_OFFSET_LENGTH`, `CKB_VM_ASM_TRACE_OFFSET_CYCLES`) 访问它们. 源码中有专门的单元测试验证这一不变性.

## Trace: 如何从 Rust 传入到汇编代码

ASM 执行器入口只有两个参数:

```rust
ckb_vm_asm_execute(machine, invoke_data)
```

其中 `machine` 是 `AsmCoreMachine`, 里面保存了寄存器, PC, cycles, memory 指针, page flags, frame flags 等 VM 状态. `invoke_data` 则是在一次调用中临时传给汇编的参数, 核心成员包括 `pause`, `fixed_traces`, `fixed_trace_mask`.

汇编代码入口处先做一件很传统的事: 保存调用约定里需要保留的寄存器, 然后把几个长期使用的值固定在寄存器里.

```text
ckb_vm_asm_execute:
  push %rbp
  push %rbx
  push %r12
  push %r13
  push %r14
  mov ARG2, INVOKE_DATA     // 第二个参数 -> INVOKE_DATA
  mov ARG1, MACHINE         // 第一个参数 -> MACHINE
  movq CKB_VM_ASM_ASM_CORE_MACHINE_OFFSET_MEMORY_SIZE(MACHINE), MEMORY_SIZE
```

```text
MACHINE     = %rsi
TRACE       = %rbx
MEMORY_SIZE = %r13
INVOKE_DATA = %r14
INST_PC     = %r8
INST_ARGS   = %r9
```

`MACHINE` 保存所有 VM 状态, `TRACE` 指向当前正在执行的 trace. `INST_PC` 和 `INST_ARGS` 不是 RISC-V 的 PC, 而是在 trace 内部移动的两个指针: 一个指向下一条 host 跳转目标, 一个指向下一条已解码好的 guest 指令参数.

x64 的难点也在这里. `%rcx` 要留给移位指令使用 `%cl`, `%rax/%rdx` 会被乘除法占用, Windows 和 System V 的参数寄存器又不一致. 所以文件开头有一大片寄存器别名和 `PUSH_*_IF_*` 这样的宏. 看起来啰嗦, 其实是在给后面两千多行指令实现预留空间.

其实 aarch64 和 riscv64 也有类似的入口, 只是风格不同: aarch64 寄存器更宽裕, 因此我们会把 `REGISTER_BASE`, `MEMORY_PTR` 这类次要但常用的地址也长期放在 `x28`, `x29`. riscv64 则更像在照镜子: host 和 guest 都是 RISC-V, 很多 guest 指令可以直接映射成 host 指令, 但它仍然要遵守 host ABI, 保护 `s0..s6`, 并用 `a0` 返回汇编执行结果.

## Trace: 入口即出口, 出口即入口

进入汇编主循环后, 会先执行 `.CKB_VM_ASM_LABEL_OP_CUSTOM_TRACE_END`. 这是一段稍显复杂的代码块:

```text
.p2align 3
.CKB_VM_ASM_LABEL_OP_CUSTOM_TRACE_END:
  LOAD_PC(%rax, %eax, %rcx, %ecx, TEMP3d)
  shr $2, %eax
  andq CKB_VM_ASM_INVOKE_DATA_OFFSET_FIXED_TRACE_MASK(INVOKE_DATA), %rax
  imul $CKB_VM_ASM_FIXED_TRACE_STRUCT_SIZE, %eax
  movq CKB_VM_ASM_INVOKE_DATA_OFFSET_FIXED_TRACES(INVOKE_DATA), TRACE
  addq %rax, TRACE
  movq CKB_VM_ASM_TRACE_OFFSET_ADDRESS(TRACE), %rdx
  cmp %rcx, %rdx
  jne .exit_trace
.trace_loaded:
  mov CKB_VM_ASM_TRACE_OFFSET_LENGTH(TRACE), %edx
  test %rdx, %rdx
  je .exit_trace
  movq CKB_VM_ASM_ASM_CORE_MACHINE_OFFSET_CYCLES(MACHINE), %rax
  addq CKB_VM_ASM_TRACE_OFFSET_CYCLES(TRACE), %rax
  jc .exit_cycles_overflow
  cmp CKB_VM_ASM_ASM_CORE_MACHINE_OFFSET_MAX_CYCLES(MACHINE), %rax
  ja .exit_max_cycles_exceeded
  movq %rax, CKB_VM_ASM_ASM_CORE_MACHINE_OFFSET_CYCLES(MACHINE)
  addq %rdx, PC_ADDRESS
  /* Prefetch trace info for the consecutive block */
  movq PC_ADDRESS, %rax
  shr $2, %eax
  andq CKB_VM_ASM_INVOKE_DATA_OFFSET_FIXED_TRACE_MASK(INVOKE_DATA), %rax
  imul $CKB_VM_ASM_FIXED_TRACE_STRUCT_SIZE, %eax
  movq CKB_VM_ASM_INVOKE_DATA_OFFSET_FIXED_TRACES(INVOKE_DATA), %rdx
  prefetcht2 0(%rdx, %rax)
  lea CKB_VM_ASM_TRACE_OFFSET_THREADS(TRACE), INST_PC
  mov INST_PC, INST_ARGS
  add $8, INST_ARGS
  NEXT_INST
```

这段代码并不表示程序结束, 而是表示当前 trace 执行到头了, **需要决定下一步去哪**. 这一步既可能跳转到下一段 trace, 也可能返回 Rust 侧重新解码. 首次进入汇编执行器时, 也会先走这段逻辑, 因为它本质上就是"装载下一段 trace 并开始执行"的统一入口.

它的核心流程可以概括为 4 步:

1. 用当前 PC 在 fixed trace 表里定位槽位
2. 校验槽位里 trace 的起始地址与当前 PC 是否一致
3. 检查 trace 长度与 cycles 预算是否允许继续执行
4. 成功则切到新 trace 并 `NEXT_INST`, 失败则走 `.exit_trace` 返回 `CKB_VM_ASM_RET_DECODE_TRACE`. Rust 侧会根据这个返回值重新解码, 构造新的 trace, 再次调用汇编执行器.

这里有两个容易忽略的细节.

第一, 它不是直接用当前 trace 的下一条来串联 fixed trace, 而是每次都用更新后的 PC 重新哈希索引 fixed trace 表, 再校验 `trace.address == pc`. 这保证了即使出现哈希冲突或者槽位失配, 也会安全地回到 Rust 侧解码, 不会跳进错误 trace.

第二, `.CKB_VM_ASM_LABEL_OP_CUSTOM_ASM_TRACE_JUMP` 会把线程参数中的完整 trace 地址读到 `TRACE`, 然后复用同一段 `.trace_loaded` 逻辑. 也就是说, dynamic trace 与 fixed trace 在执行阶段共用同一套长度检查 + cycles 结算 + 设置 `INST_PC/INST_ARGS` 的流程, 只是在 trace 指针来源上不同.

这一段代码的意义在于, 它把是否继续在汇编层快跑的判断集中到了一个点: 地址匹配, 长度有效, cycles 合法就继续 thread dispatch; 任意条件不满足就立刻返回 Rust. 这种设计让汇编执行器既保持了高速路径, 也保住了边界条件下的正确性.

## 零寄存器

RISC-V 的 `x0` 永远等于 0. 这条规则很简单, 但在执行器实现里非常容易变成小陷阱.

在早期版本中, CKB-VM 的 ASM 后端常常在写回 `rd` 之后, 再把寄存器数组里的第 0 项清零. 所以我们会看到类似这样的宏:

```asm
#define WRITE_RD(v) \
  movq v, REGISTER_ADDRESS(RD); \
  movq $0, ZERO_ADDRESS
```

也就是说, 即使某条指令误把结果写到了 `x0`, 下一步也会把它擦掉. 后来一些 MOP 伪指令会在一条 guest 语义中写多个寄存器, 这时如果每写一次都立刻清零 `x0`, 写回顺序本身就可能影响结果. 因此源码里又出现了 `WRITE_RD_V2` 和 `NEXT_INST_V2` 这一组宏: 前者只负责写目标寄存器, 后者在整条伪指令结束时统一清零 `x0`.

## 内存检查

如果只看算术指令, 汇编执行器并不难理解. `add` 就是 load 两个寄存器, 加起来, 写回. 真正让它变复杂的是内存.

CKB-VM 的内存模型既要保证越界访问会被拒绝, 又要维护 W^X 权限, 还要支持按需初始化的 FastMemory. 每次 `lb`, `lw`, `ld`, `sb`, `sw`, `sd` 都可能触发这一整套逻辑. 如果这些检查写得太慢, ASM 后端的大部分收益都会被吃掉; 如果写得太激进, 链上执行的确定性和安全边界就会出问题.

三份汇编执行器都使用了类似的策略: 先记住上一次读过的 memory frame, 或上一次写过的 page. 如果当前访问仍然落在同一个范围内, 就直接走快速路径; 如果跨过边界, 才进入完整检查.

读路径大致分为三步:

- 检查地址加长度是否越界.
- 查看对应 memory frame 是否已经初始化.
- 如果没有初始化, 调用 Rust 侧的 `inited_memory` 完成实际填充.

写路径则多了一层权限判断: 对应页面必须是 writable, 同时要把 dirty bit 置位, 以便快照和后续内存管理知道这一页被修改过.

这里最值得注意的是 `PREPCALL` 和 `POSTCALL`. 汇编执行器大部分时间都不想回到 Rust 世界, 但内存初始化这类工作仍然由 Rust 侧负责. 一旦需要调用 `inited_memory`, 汇编代码就必须保存当前寄存器状态, 按目标平台 ABI 对齐栈, 调用函数, 再恢复现场. 这个细节听起来像一条普通的 ABI 规则, 但在手写执行器里, 这类规则一旦漏掉, bug 往往会以非常诡异的形式出现.

## 如果我们要写下一个 ASM 执行器

假设有一天要为 CKB-VM 加一个新的 host 架构, 我们应该怎么开始?

历史上, CKB-VM 只有过三个 ASM 执行器: x64, aarch64 和 riscv64. 这三条路都走下来之后, 我觉得它们的实现套路已经很清晰了. 下面是我总结的一个大致步骤.

**第一步: 理解数据结构和协议**

先通读三个结构体:

- [`AsmCoreMachine`](https://github.com/nervosnetwork/ckb-vm/blob/develop/definitions/src/asm.rs): VM 状态的 C 布局. 汇编通过 `CKB_VM_ASM_ASM_CORE_MACHINE_OFFSET_*` 宏访问每个字段.
- [`InvokeData`](https://github.com/nervosnetwork/ckb-vm/blob/develop/definitions/src/asm.rs): 传给汇编的三个指针(`pause`, `fixed_traces`, `fixed_trace_mask`).
- [`FixedTrace`](https://github.com/nervosnetwork/ckb-vm/blob/develop/definitions/src/asm.rs): trace 的内存布局. `address`, `length`, `cycles`, 然后是 `2 * (TRACE_ITEM_LENGTH + 1)` 个 `u64` 的 thread 数组.

这些 offset 宏不是手写的, 是由 [`definitions/src/generate_asm_constants.rs`](https://github.com/nervosnetwork/ckb-vm/blob/develop/definitions/src/generate_asm_constants.rs) 在构建时自动生成到 `cdefinitions_generated.h`. **永远不要手工维护这些 offset**, 否则 struct 布局一变就会全线崩溃.

**第二步: 写最小骨架**

我们首先在汇编代码里编写下面这样子的最小骨架:

```asm
ckb_vm_asm_execute:
    保存 callee-saved 寄存器
    把参数固定到 MACHINE / INVOKE_DATA
    加载 MEMORY_SIZE
    跳到 OP_CUSTOM_TRACE_END
```

然后立即实现 `OP_CUSTOM_TRACE_END` 的完整逻辑: 查 fixed trace, 比对地址, 检查 cycles, 设置 `INST_PC`/`INST_ARGS`, `NEXT_INST`.

同时要把 label table 接上. Rust 侧通过 `label_from_fastpath_opcode()` 计算标签地址:

```rust
pub fn label_from_fastpath_opcode(opcode: InstructionOpcode) -> u64 {
    unsafe {
        u64::from(*(ckb_vm_asm_labels as *const u32).offset(opcode as u8 as isize))
            + (ckb_vm_asm_execute as *const u32 as u64)
    }
}
```

`ckb_vm_asm_labels` 是一个在汇编文件中定义的符号, 它实际是一个 `u32` 数组, 每个元素是对应 opcode 标签相对于 `ckb_vm_asm_execute` 起始地址的偏移. 只要骨架跑通, 哪怕只有一条 `OP_CUSTOM_TRACE_END`, 也算迈出了最关键的一步.

**第三步: 寄存器分配**

这是最难的部分, 甚至比实现指令本身更难. 三个后端的寄存器分配逻辑各不相同:

- **x64**: 受 `%cl` 移位和 `%rax`/`%rdx` 乘除限制, `RS2` 被拆成两半, `RD` 和 `RS2` 共享 `%rax`.
- **aarch64**: 寄存器宽裕, 仅 `xzr` 不能用作通用寄存器, 可以大量使用 callee-saved 寄存器.
- **riscv64**: host 和 guest 都遵循 RISC-V ABI, 利用 callee-saved 的 `s0`-`s6` 持有 guest 寄存器, 减少了 `PREPCALL`/`POSTCALL` 的保存范围.

在做寄存器分配时, 有几个通用原则:

1. 长期持有的指针(`MACHINE`, `TRACE`, `INST_PC`, `INST_ARGS`) 放在 callee-saved 寄存器中, 这样在调用 `inited_memory` 后不需要恢复.
2. 指令解码的直接结果(`RD`, `RS1`, `RS2`, `IMMEDIATE`) 放在 caller-saved 或 callee-saved 中均可, 但要注意读写密度.
3. 如果某个寄存器有架构特定的使用限制(比如 x64 的 `%rcx` 必须是 `IMMEDIATE`), 优先满足这些约束.

**第四步: 写内存宏**

内存宏应该在指令之前稳定. 算术指令写错了通常一眼能测出来; 内存边界写错了, 可能只在特定的跨页读写, 特定的 VM version, 或者 chaos mode 的随机内存布局下才会暴露. 这种 bug 的排查成本极高.

建议按这个顺序实现:

1. `_CHECK_READ_FRAMES`: 内部宏, 初始化 memory frame.
2. `CHECK_READ_VERSION0` / `CHECK_READ_VERSION1`: 带越界检查 + `last_read_frame` 缓存.
3. `CHECK_WRITE`: 带 W^X 检查 + dirty 标记 + frame 初始化.
4. `PREPCALL` / `POSTCALL`: 确保 Rust 函数调用 ABI 合规.

**第五步: 按指令族推进**

- 第一梯队: I(整数)基础整数指令, load/store, branch/jump. 这些是程序的主体.
- 第二梯队: M(乘除). 重点盯乘除法边界(`INT64_MIN / -1`, 除以零).
- 第三梯队: B(位操作)和 MOP(宏融合). 重点盯多寄存器写回和 `x0` 清零时机.

**第六步: 测试**

每加一组指令, 都应该能和普通解释器跑同一批 artifact. CKB-VM 目前有完整的测试套件, 对于开发者而言, 只要能跑通 `cargo test --features=asm` 就说明汇编执行器的实现大体上是正确的.

另外, CKB-VM 的模糊测试框架([`fuzz/fuzz_targets/asm.rs`](https://github.com/nervosnetwork/ckb-vm/blob/develop/fuzz/fuzz_targets/asm.rs) 也是验证正确性的重要工具: 它随机生成指令流, 在 ASM 后端和解释器后端分别执行, 然后比对所有寄存器和内存状态.

## 小结

CKB-VM 的汇编执行器是一种很克制的优化. 它没有引入 JIT, 没有改变链上程序的语义, 也没有把安全边界交给宿主机器码生成器. 它做的是更朴素也更辛苦的事: 把解释器最热的路径逐条翻译成手写汇编, 同时保留 CKB-VM 原有的内存模型, 版本语义, 周期计量和异常行为.

从 Rust 解释器到 x64 汇编, 到 aarch64 汇编, 最后到 riscv64 汇编, 这条路线展示了一种很有 CKB-VM 风格的工程取舍: 先有清晰的参考实现, 再在热点路径上做可验证的局部替换. 每新增一个后端, 都不是另起炉灶, 而是在同一套语义之下, 用目标架构自己的语言把那圈循环重新讲一遍.

这也是我最喜欢这个设计的地方. 汇编执行器看起来复杂, 晦涩和难懂, 但它真正服务的目标很简单: 让链上程序在不牺牲确定性和安全性的前提下跑得更快. 对一个区块链虚拟机来说, 这已经是足够朴素, 也足够困难的目标了.
