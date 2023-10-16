# CKB/CKB-VM Zero Cost Abstractions

Rust 的零成本抽象是许多 Rust 使用者津津乐道的话题, 借助 Rust 提供的各种工具, 例如生命周期, 引用, 借用或者 Trait 工具, 它让我们可以不用费太多的努力就可以写出优秀的代码. 零成本抽象这个概念最早来自 C++, 是由 C++ 创始人 Bjarne Stroustrup 定义:

0. 你不使用的, 你不负担成本
0. 你使用的, 你也没法更优化

我们主要来探讨一下第二点. 第二点的含义我们展开来说, 一个零成本抽象的代码编译成的机器码应当是性能最优的, 我们无法通过手写机器码的方式来进一步优化它的性能(为什么这么解释? 因为任何高级语言都是对机器码的抽象). 在这里, 我想提出一个思考: Rust 是否已经做到它所宣称的零成本抽象?

别着急, 在之后的时间里, 我会回答这个问题.

## 介绍: 什么是 RISC-V

我们现在引入一些本次主题会用到的背景知识. 本次的主题和 RISC-V 相关, RISC-V 是 2010 年首次概念化的开放式 ISA, 最初的目标是研究和教育, 后续则开始逐渐进入消费领域. 与广泛使用的 x86–64 ISA 相比, 它采用 RISC(精简指令集) 方案通过提供更少的功能指令和内存寻址模式来简化微架构的设计.

RISC-V 目前吸引了许多厂家和机构, 整体发展势头也比较好, 最近的一个大新闻是这个月的月初时候, 世界第一款 RISC-V 架构的笔记本问世.

## 介绍: CKB-VM

接下来的主角是 CKB-VM. CKB-VM 是 RISC-V 指令集的纯软件实现, 它现在已经完整支持 32 位和 64 位寄存器大小的 RISC-V 指令集. 我们在编写 CKB-VM 的时候, 为其提供了三种不同的执行模式:

0. Rust 实现的解释器, 我们称它为解释器模式
0. Rust 实现的解释器主循环 + 基于手工汇编实现的解释器, 我们称它为 ASM 模式
0. AOT 模式, 在执行 RISC-V 代码之前会先对其进行编译.

本次的主题只会关注到前两种模式. 在第二种模式下, 你可以发现我们用一部分手工汇编代码替换了 Rust 代码, 这部分代码主要承担解释执行的功能. 你可能会好奇, 用一部分汇编代码替代 Rust 代码, 它能带来多大的影响? 为了更好回答这个问题, 我编写了一个测试, 测试内容是 secp256k1 算法(secp256k1 指的是比特币公钥密码学中使用到的椭圆曲线参数). 在这个测试中, 解释器模式耗时 22 ms, 而 ASM 模式的耗时只有 5 ms.

很多情况下, 我们都认为 Rust 很快, 它能提供近似 C 和 C++ 的效率. 但有些时候它可以变得更快. 所以, 我们的手工汇编代码是如何战胜了 Rust 的零成本抽象?

## 方法: 将 Rust 翻译为等价的汇编代码

最直观的方法就是我们直接将 Rust 代码翻译为等效的汇编代码. 使用 Rust 编写一个解释器是最直观的, 我们只需要一条一条地获取指令, 然后在本机上执行. 但是这种最简单的方法受限于 Rust 语言本身的性能, 同时我们必须遵守 Rust 的安全规范(例如内存和指针). 不得不说的一点, Rust 的安全规范虽然可以解放开发者的大脑负担, 但是它本身也引入了额外的开销, 这也是 Rust 的标准库大量使用 unsafe 代码的原因之一. 举一个最简单的例子, Rust 数组的越界检查, 它就在运行时引入了额外的开销--即使开发者 100% 确定自己的代码不会出现越界错误, 却依然要为这个安全检查付费.

这里有两份代码, 左边的代码是 Rust 解释执行 RISC-V ADD 指令的实现, 右边的代码则是使用等效的汇编进行解释执行 RISC-V ADD 指令的代码. 两份代码所使用的行数大致相等, 这也表明在一些特定场景下, 使用汇编不会导致代码可读性的大幅度降低. 另外一点可能是大多数人担心的: 编写汇编代码容易吗? 事实上, 编写汇编代码不是一件容易的事情, 它在难以理解的同时也难以调式, 要学会编写汇编代码, 比我们要学会 Rust 还要难得多.

```text
insts::OP_ADD => {
    let i = Rtype(inst);
    let rs1_value = &machine.registers()[rs1 as usize];
    let rs2_value = &machine.registers()[rs2 as usize];
    let value = rs1_value.overflowing_add(rs2_value);
    update_register(machine, rd, value);
}
```

```text
.CKB_VM_ASM_LABEL_OP_ADD:
  DECODE_R
  movq REGISTER_ADDRESS(RS1), RS1
  addq REGISTER_ADDRESS(RS2r), RS1
  WRITE_RD(RS1)
  NEXT_INST
```

## 方法: 手工寄存器分配

在许多编程语言中, 程序员可以使用任意数量的变量. 这些变量大多数情况下存储在内存中, 只有当需要时, 才会将它们从内存载入到寄存器中. 计算机可以快速读写 CPU 中的寄存器, 访问一次寄存器通常需要很少的时钟周期(可能只有 1 个), 但一旦访问内存, 事情就会变得更加复杂, 并且会涉及到缓存控制器/内存总线等结构, 从而花费更多的时间. 因此手工汇编代码进行优化的一个重要原则就是将频繁使用的变量更多的放在寄存器中, 以使得程序运行的更快.

但寄存器是十分有限的, 在大多数架构中, 只有 16 或 32 个通用寄存器. 相比而言, 内存通常可以认为是"无限"的. 我们会去分析哪些变量更加常用, 因此将这些变量更长久的存储在寄存器中. 把这种做法推广到极致就是, 如果某些变量在程序的整个生命周期中都永久存在并被频繁使用, 我们可以将该变量绑定到某一个寄存器中, 也就是寄存器静态分配.

在一些特定的场景下, 寄存器静态分配十分有用, 例如在编写解释器的时候. 解释器一般有一个无限循环的解释器主循环, 以及内部的指令获取, 指令解码, 指令执行, 内存访问, 寄存器回写等组成. 在这个过程中, 一些变量的生命周期几乎等于整个程序的生命周期, 将它静态分配到寄存器中可以有效减少函数传参, 出栈或入栈造成的不必要的性能损失.

下面是介绍寄存器静态分配理念的两份伪代码, 要注意的是第二份代码本身是使用汇编编写的, 但是为了方便介绍我采用了 Rust 语法.

```text
struct Machine {}

fn instruction_fetch(m: &Machine) {}

fn instruction_decode(m: &Machine) {}

fn execute(m: &Machine) {}

fn memory_access(m: &Machine) {}

fn register_write_back(m: &Machine) {}

fn main() {
    let machine = &Machine{};

    for {
        instruction_fetch(machine);
        instruction_decode(machine);
        execute(machine);
        memory_access(machine);
        register_write_back(machine);
    }
}
```

```text
struct Machine {}

fn instruction_fetch() {
    // Treat register x as machine
    let machine = register(x);
}

fn main() {
    let machine = &Machine{};

    save_the_machine_address_to_register_x(machine);

    for {
        instruction_fetch();
        instruction_decode();
        execute();
        memory_access();
        register_write_back();
    }
}
```

但是要小心一点, 使用寄存器静态分配意味着你可用的寄存器会减少.

## 方法: 尾递归

在我们使用汇编编写 CKB-VM 的时候, 我们使用了尾递归的方式来减少函数调用的开销. 在此之前我们来了解一下解释器中经常出现的一个概念: 基本块(Basic block). 一个基本块只有一个入口和出口, 按顺序执行块中的指令. 任何可以导致执行流程改变的指令(跳转, 调用, 返回和系统调用)都会导致一个基本块结束. 在另一些论文或者文章中, 基本块也常常被叫做 Trace. 它们表达的通常是一个概念.

我们来做一个小测试: 你能把下面的代码分割成一个一个基本块吗? 提示: RISC-V 指令中的 beqz, jr, ret 指令会造成执行流的改变.

```
100c6:       67c9                    lui     a5,0x12
100c8:       6549                    lui     a0,0x12
100ca:       c8878593                addi    a1,a5,-888 # 11c88 <__TMC_END__>
100ce:       c8850793                addi    a5,a0,-888 # 11c88 <__TMC_END__>
100d2:       8d9d                    sub     a1,a1,a5
100d4:       8589                    srai    a1,a1,0x2
100d6:       4789                    li      a5,2
100d8:       02f5c5b3                div     a1,a1,a5
100dc:       c991                    beqz    a1,100f0 <register_tm_clones+0x2a>
100de:       00000337                lui     t1,0x0
100e2:       00030313                mv      t1,t1
100e6:       00030563                beqz    t1,100f0 <register_tm_clones+0x2a>
100ea:       c8850513                addi    a0,a0,-888
100ee:       8302                    jr      t1
100f0:       8082                    ret
```

把代码划分成一个又一个基本块有许多好处, 其中最主要的好处是基本块可以作为我们的最小执行单元和最小优化单元.

正如我之前所说, CKB-VM 的 ASM 模式采用的是 Rust 实现的解释器主循环 + 基于手工汇编实现的解释器, 在引入基本块模型后, 那么实际上它的伪代码应该是

```text
fn main() {
    let machine = &Machine {};
    for {
        trace = prepare_trace();
        execute(trace);
    }
}
```

要注意, 上述代码的 execute() 函数由汇编编写, 其中包含了指令获取, 指令解码, 指令执行, 内存访问和寄存器回写 5 个部分. 从 execute 返回到主转码循环会带来很大的性能损失, 我们需要经历两次上下文环境切换和一次的基本块查找. 一种改进方法是使用递归翻译的方法: 当 execute 执行到基本块的末尾时, 递归地开始下一个 trace 的翻译, 这样就无需从汇编代码返回到 Rust 解释器主循环中.

```text
          ┌─────────────────────────┐
          │                         │
    ┌────>|  Main Interpreter loop  │
    │     │                         │
    │     └───────────┬─────────────┘
    │                 |
    │     ┌───────────+─────────────┐
    │     │                         │
    │     │      Prepare trace      │
    │     │                         │
    │     └───────────┬─────────────┘
    │                 |
    │     ┌───────────+─────────────┐
    │     │                         │
  No│     │   Execute trace in ASM  │<─────┐
    │     │                         │      │
    │     └───────────┬─────────────┘      │
    │                 |                    │Yes
    │     ┌───────────+─────────────┐      │
    │     │                         │      │
    │     │Find next trace in Cache?├──────┘
    │     │                         │
    │     └───────────┬─────────────┘
    │                 │
    │                 │
    └─────────────────┘
```

## 结语

最后, 我想回答一下开篇的问题, Rust 真的实现它所宣称的零成本抽象了吗? 很不幸的是, 答案是否定的. 高级语言, 例如 Rust, 它本身是对机器码的一种抽象. 但在真实世界中, 我们既想要这层抽象带来的便捷性, 同时还要求这层抽象不会引起性能的下降, 这是一个美好的愿景, 但在实践中却往往并不容易达到.