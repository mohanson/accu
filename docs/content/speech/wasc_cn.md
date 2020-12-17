# WASC: WebAssembly 到 RISC-V 的 AOT 编译器

项目地址: [https://github.com/mohanson/wasc](https://github.com/mohanson/wasc).

第一场

- 时间: 2020-07-26
- 地点: RISC-V 基金会 OSDT Meetup
- 主讲: 自己
- 稿件: [https://github.com/hellogcc/OSDT-Slides/blob/master/20200726-OSDT-Meetup/wasc.pdf](https://github.com/hellogcc/OSDT-Slides/blob/master/20200726-OSDT-Meetup/wasc.pdf)
- 视频: [https://www.bilibili.com/video/av668938952/](https://www.bilibili.com/video/av668938952/)

第二场

- 时间: 2020-08-29
- 地点: W3C WebAssembly 线上研讨会
- 主讲: 自己
- 活动: [https://github.com/w3c/chinese-ig/blob/master/meetings/2020-08-29.md](https://github.com/w3c/chinese-ig/blob/master/meetings/2020-08-29.md)

OSDT 的各位周末快乐, 我是 mohanson, 目前在 nervos 做虚拟机和编译器相关的工作. 今天我要分享的内容是: "WASC: 一个 WebAssembly 到 RISC-V 的 AOT 编译器".

在过去的几个月时间里, 我投入了大量时间在这个项目上. 它已经拥有不错的完成度, 并且很高兴的可以在此时向大家分享这一项目. 我先来介绍一下这个项目成立时的背景.

# 背景介绍

在区块链世界的链上虚拟机中, 流行着几种不同的指令集, 包括 WebAssembly, RISC-V, 与即将完成历史使命退休的 EVM. 它们运行在大致相同的抽象层级上. 每一个指令集都有它们各自的特点, EVM 已经持续运行了 5 年, 它运行的很好, 但其实它本身的设计非常糟糕, 它的设计缺陷太多了, 以至于以太坊决定抛弃它. WebAssembly 是正在备受关注的一个技术, 许多明星项目都采用的它, 比如以太坊2.0, substrate, EOS 等, WebAssembly 目前处在快速演进状态, 但快速的变化可以是一个好事, 也可以是一个坏事, 看你从哪方面看待它. RISC-V 在区块链行业是一个比较新的技术, 我们团队主要是使用的 RISC-V. 也有一些比较冷门的项目在用 JVM 做, 不过这个时候 Oracle 会投来善意的目光, Java API 的版权在 Oracle 手里, 注定无法走的太远.

在以太坊社区计划让 EVM 退休前, 他们做了很多尝试 EVM 到 WebAssembly 的编译器, 这使得这两个指令集可以互相复用对方的很大一部分工具(主要是后者对前者). 比较常见的几个是 evm2wasm, runevm, yevm, 不过不幸的是这些项目基本都已经停止开发了. 目前还保持活跃的一个项目名字叫 solang, 它不是一个 evm 2 wasm 的项目, 而是一个 solidity 2 wasm 项目. solidity 是一门构建在 evm
上的合约编程语言, solang 这个项目做的事情其实是给 solidity 加上了 WebAssembly 后端.

我认识到区块链虚拟机领域的各种指令集的转换是一个切实存在的需求, 同时我注意到, 目前区块链领域缺少好用的从 WebAssembly 到 RISC-V 的编译器的相关工具的研究, 因此我决定填补这一工作. 我相信如果存在这一工具的话, 会对 RISC-V 在区块链上的发展带来很多好处.

# 原理

![img](/img/speech/wasc/wasc.png)

WASC 这个项目的名字来自 WebAssembly 和 RISC-V 的组合. 它可以将 WebAssembly 规范的 WebAssembly 字节码(.wasm)或 S 表达式(.wat)文件编译为 ELF 格式的可执行文件, 目前经过测试的有两个平台, x86 和 RISC-V.

先简单介绍一下 WASC 的原理图. WASC 底层依赖一个名为 WAVM 的项目, 它是一种高性能的转换层, 基准测试表明这是迄今为止 WebAssembly 的最高性能的转换层实现, 它可通过 LLVM 将 WebAssembly 代码直接编译为本机代码. 它最初由 WebAssembly 官方开发维护, 后来独立出来成为一个单独的项目. 但是 WAVM 也存在缺点, 正如大多数 WebAssembly 的 JIT 编译器一样, 它需要一个运行时部分, 用以桥接主机环境与虚拟机环境. 测试下来这个运行时部分大小超过 2M, 这与我们所期望的在空间受限的区块链上执行 WebAssembly 的初衷相违背.

WASC 的核心设计原理, 在于尝试将构建运行时所需的所有信息都包含在单独的几个文件中. 它首先通过 WAVM 这个转换层将 WebAssembly 源代码编译到目标文件, 然后在一个单独的 C 语言文件中发出最少的运行时部分代码(在多数情况下, 仅仅只需要使用不到 50 行 C 代码), 然后再通过 GCC 将之与 WAVM 生成的目标文件链接在一起, 最终生成一个可执行的 ELF 格式的二进制文件.

也可以这么认为, WASC 的工作是使用一个极小的运行时替换了原来 WAVM 臃肿(相对的)的运行时. 之后我会介绍一下为什么 WASC 能做出一个极小的运行时.

现在先来谈一谈为什么会选择使用 WAVM 转换层. 除了性能因素之外, WAVM 很大的一个特点是它生成的目标文件内的符号语义清晰, 可以很容易的为它编写胶水代码. 我截取了两个不同的 WebAssembly JIT 编译器生成的目标代码, 然后用 objdump 打印出了它们的符号表. 左边的 WAVM 生成的, 后边是 wasmtime 生成的.

WAVM 的符号命名比较清晰, 功能明确. 比如函数的元数据, 它保存了无法被直接发射到目标文件的函数的一些数据, 之后是 funcitonImport, 它表示这个函数需要由外部提供, 下面是全局变量, WebAssembly 内存的偏移值, 最后的 typeId 则是函数签名.

我们对比来看 wasmtime 生成的. 它也声明了外部函数, 然后下面就是直接的许多算数运算函数, 像是 i64 udiv, i64 sdiv 等, 它的内存, 函数签名等关键信息都是由自身管理的, 这限制了对它进行二次开发. 综合来看, WAVM 在众多的 JIT 编译器中性能和定制性都是最好的.

WASC 内部有一个示例项目 echo, 它是一个使用 WebAssembly 实现的小工具, 可以接收命令行输入然后打印到标准输出. 使用 WASC 对它进行编译的时候, 会生成如下的构建目录.


```text
.
├── echo                                <--- 可执行二进制文件
├── echo.c                              <--- 入口文件
├── echo_glue.h                         <--- 胶水代码, 提供极小的运行时
├── echo.o                              <--- WAVM 生成的目标文件
├── echo_precompiled.wasm               <--- WAVM 生成的预编译文件, 内含完整目标代码
└── platform
    ├── common
    │   ├── wasi.h                      <--- WASI 数据结构定义
    │   └── wavm.h                      <--- WAVM 数据结构定义
    ├── posix_x86_64_wasi.h             <--- WASI 在 posix 上的部分实现(C 代码)
    └── posix_x86_64_wasi_runtime.S     <--- WASI 在 posix 上的部分实现(汇编代码)
```

主要来看下 WASC 的胶水代码, 也就是 echo_glue.h. 你可以看到, 许多数据, 在胶水代码中只是给他简单的赋值为 0, 比如 `const uint64_t typeId0 = 0;`. 这是因为在 WAVM 的运行时环境中, 某些类型的数据只有它们的地址是有用的. 对于 WAVM 而言, typeId0 是一个结构体, 它保存了一个具体的函数签名, 但在运行时中判断两个函数的函数签名是否一致时, WAVM 只比对了两个函数的签名的地址是否是同一个地址. 因此, 我们不必真的在胶水代码中实现一个复杂的函数签名结构体, 这给了我们巨大的优化空间. WASC 在胶水代码里做了大量的 tricks 工作, 来保证胶水代码提供的运行时是极小的.

WASC 的大体流程就是如此, 但是在实际实现的细节中会比上面介绍的复杂很多, 比如我们不得不采用一些汇编代码和 Linker Script 来完成一部分难以实现的功能.

# AssemblyScript, syscall 与 RISC-V

接下来看看 WASC 在实际项目中的应用. 我们公司的许多项目都使用的 CKB-VM, CKB-VM 是一个 RISC-V 虚拟机, 支持解释执行, JIT 或 AOT 执行 RISC-V 可执行文件, 它本身实现了 RISC-V 中的 IMC 三种指令集合.

我们会探讨一下如何通过 WASC 使得 AssemblyScript 可以跑在 CKB-VM 上. AssemblyScript 是一个在 WebAssembly 社区很重要的编程语言, 它是 TypeScript 语法的一个子集, 可以直接编译到 WebAssembly.

RISC-V 里面有一条叫做 ECALL 的指令负责发起系统调用. 这条指令的名字其实挺奇怪的, 因为我发现有的地方名字叫 ecall, 但是官方代码里面有时候又会叫它 scall. 据说是个历史遗留问题, 曾经改过名字.

系统调用经常被用来从计算机程序向操作系统的内核请求服务, 它的这个特点也被用在了区块链上的合约与区块链核心进行交互上. 像以太坊曾经提出"世界计算机"的口号, 我就想如果他们能用类似系统调用的方式去实现 EVM 而不是在 EVM 里塞入一大坨特定功能的指令, 也许 EVM 也不至于这么糟糕.

横向对比的话, 区块链上运行的程序实际上在用户空间, 而区块链核心则处在内核空间.

因此, 如果我们能在一门编程语言中实现 syscall, 那么就可以保证它可以完美的运行在 CKB-VM 上. 我们首先来看 C 语言是如何实现 syscall 的. 下面的代码片段来自官方的一个项目, 它其实是直接拿汇编写的, 把数据塞到对应的寄存器, 然后再读取 a0 寄存器作为返回值.

所以可以很自然的想到我们可以在胶水代码中加入上述的代码片段, 然后在 AssemblyScript 中声明一个外部函数.

但事实上它是不工作的. 比如我们要在 syscall 中传递一个字符串, 在 C 语言的实现中, 可以传递字符串的地址和字符串的长度, 然后便可以重新从内存还原出原字符串. 当我在 AssemblyScript 也这样做的时候, 我发现一个问题, 那就是在 AssemblyScript 中取得的地址并非程序运行地址, 而是 WebAssembly 内存地址的偏移值. 正确的做法是在偏移地址前加上 WebAssembly 内存的首地址.

# 吐槽

有许多区块链直接采用 WebAssembly, 比如 Substrate, EOS, 以及未来的以太坊 2.0. 但它们的使用方式存在问题: 比如 EOS, 它只支持使用 C++ 来编写合约代码; Substrate 只支持使用 Rust + 宏的方式来编写合约代码, 以太坊 2.0 则使用预编译的合约来扩展 WebAssembly. 它们的实现是互不兼容的, 抛弃了 WebAssembly 最大的优点即通用性. WASC 设计的 WebAssembly on RISC-V 方案由于与宿主环境只有 syscall 一种交互方式, 使得可以在 CKB-VM 上运行任何支持 WebAssembly 后端的语言. 另外相比起 C/C++ 与 Rust, AssemblyScript 等语言更加易学和使用.


另外 WebAssembly 的测试用例真的是一言难尽...

- 在一个 case 里面测试复数条指令
- 后一个 case 依赖前面 case 的执行结果
