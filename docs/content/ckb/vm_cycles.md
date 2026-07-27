# CKB/CKB-VM 计费与成本模型

在 CKB 脚本里, 一条指令不是免费执行的.

脚本每做一次算数加法, 每做一次内存读写, 每加载一段链上数据, 都会消耗 cycles. 当 cycles 累积值超过上限, 虚拟机立刻停下并返回错误.

这件事听起来非常朴素, 但它其实是 CKB-VM 最重要的安全机制之一: 如果没有这道闸门, 一段死循环就足够把验证线程拖死. 但是与以太坊等虚拟机不同, CKB-VM 的 cycles 并非用作计费, 而是用作资源消耗的共识度量. 也就是说, 它不是用来向用户收手续费的, 而是用来判断脚本是否过度消耗资源的.

## 计费的执行流程

在 CKB-VM 的执行过程中, 始终遵循"先计数, 再执行"的原则. 也就是说, 每条指令在执行前都会先计算它的 cycles 成本, 并检查是否超过上限. 如果超过, 就直接返回错误, 不会执行该指令的语义. 这么设计的好处是, 即便脚本里有死循环, 也不会因为无限执行而拖垮验证线程. 只要在循环里每轮都消耗 cycles, 最终都会触发超限错误.

上面这段描述翻到源码里, 就是 [src/machine/mod.rs](https://github.com/nervosnetwork/ckb-vm/blob/develop/src/machine/mod.rs) 里的 `step` 函数:

```rs
pub fn step<D: InstDecoder>(&mut self, decoder: &mut D) -> Result<(), Error> {
    let instruction = {
        let pc = self.pc().to_u64();
        let memory = self.memory_mut();
        decoder.decode(memory, pc)?
    };
    let cycles = self.instruction_cycle_func()(instruction);
    self.add_cycles(cycles)?;
    execute(instruction, self)
}
```

流程是: 指令解码 -> 计算成本 -> 累加成本 -> 执行指令. 其中第二步用的 `instruction_cycle_func` 是一个可替换的函数指针, 后面会细讲; 第三步的 `add_cycles` 则是计费系统的核心闸门.

`add_cycles` 同样在 `mod.rs` 里, 逻辑很直白:

```rs
fn add_cycles(&mut self, cycles: u64) -> Result<(), Error> {
    let new_cycles = self
        .cycles()
        .checked_add(cycles)
        .ok_or(Error::CyclesOverflow)?;
    if new_cycles > self.max_cycles() {
        return Err(Error::CyclesExceeded);
    }
    self.set_cycles(new_cycles);
    Ok(())
}
```

这里区分了两种失败: `CyclesOverflow` 是 `u64` 加法溢出, `CyclesExceeded` 是超出 `max_cycles`. 两者都是确定性的: 任何节点在任何平台上跑同一份脚本, 要么同时成功, 要么在同一个位置以同一种错误退出. 在实际运行中, `CyclesOverflow` 几乎不会发生, 添加了此错误的检查只是为了防御极端情况.

## 成本是怎么定的

CKB-VM 没有把具体指令的成本写死在执行循环里. 它只定义了一个签名:

```rs
pub type InstructionCycleFunc = dyn Fn(Instruction) -> u64;
```

具体成本表在 [src/cost_model.rs](https://github.com/nervosnetwork/ckb-vm/blob/develop/src/cost_model.rs), 目前给了两种实现. 第一种是 `constant_cycles`, 每条指令都记 1, 主要用在测试里. 第二种是 `estimate_cycles`, 按 opcode 给不同的值:

| 指令类别  |        代表指令        | cycles |
| --------- | ---------------------- | ------ |
| 普通整数  | `add`, `xor`, `sll`    | 1      |
| 访存      | `ld`, `lw`, `sd`, `sw` | 2-3    |
| 分支跳转  | `beq`, `jal`           | 3      |
| 乘法      | `mul`, `mulh`          | 5      |
| 除法/余数 | `div`, `rem`           | 32     |
| 系统调用  | `ecall`, `ebreak`      | 500    |

CKB-VM 默认用的就是 `estimate_cycles`. 如果你只是写测试验证逻辑正确性, 用 `constant_cycles` 会更直观: 你看到的 cycles 基本等于执行的指令条数.

> 为什么 add 是 1, div 却是 32?
>
> 很多人第一次看到这份表会问这个问题. 答案不在 CKB-VM 的代码里, 而在物理 CPU 的硅片上.
>
> 整数加法是 CPU 里做得最熟的操作之一. 专门的加法器单元, 成熟的前递网络, 极短的流水线延迟. 一个标量 `add` 在很多架构上的延迟在 1 个周期量级, 而且吞吐极高.
>
> 整数除法则是另一个故事. 它不是一个简单的组合逻辑能搞定的事情. 硬件实现通常用迭代算法或较重的专用除法单元, 本质是一连串步骤才能得到商和余数. 典型结果是延迟远高于加法, 吞吐也更低. 除法单元在芯片上本来就比加法器稀缺.
>
> 所以 `div=32` 不是拍脑袋, 也不是说任何 CPU 上都恰好 32 个时钟周期. 它是在说: 在几乎所有现代处理器上, 除法的硬件成本都显著高于加法, 而 cycles 体系用这个比值把这件事变成了共识层面可复现的规则.
>
> 一个有趣的细节: 在 x86-64 上, `IDIV` 的延迟在 Skylake 上是 26-38 周期, 在 Zen 3 上是 17-25 周期; 而 `ADD` 的延迟是 1 周期. 32 这个数大致落在这个现实区间里.

## ASM 后端的计费差异

ASM 后端与 Rust 解释器这两条路径的计费代码写在不同地方, 但语义是一致的.

Rust 解释器路径在 `step()` 里逐条扣费, 前面已经看过.

ASM 路径的扣费发生在 trace 构建阶段. [src/machine/asm/traces.rs](https://github.com/nervosnetwork/ckb-vm/blob/develop/src/machine/asm/traces.rs) 里, 解码一条指令后:

```rs
trace.cycles += machine.instruction_cycle_func()(instruction);
```

然后这段 trace 被写进汇编执行器, 在装载时一次性加到机器总 cycles 上. 一条 trace 最多包含 16 条指令. ASM 端相当于把最多 16 次的"累加 cycles + 检查溢出 + 检查上限"合并成了一次.

## 小结

CKB-VM 的 cycles 系统做了几件很简单但很对的事情.

它把计费和执行分开, 用先计数再执行堵死了死循环拖垮节点的路径. 它把成本函数做成可替换的, 允许不同场景用不同的计费策略而不用改执行逻辑. 这些设计背后的思路其实是一样的: 在必须达成共识的地方做硬约束, 在可以灵活的地方留余地.
