# CKB/CKB-VM 宏指令融合技术(MOP)

宏指令融合技术是一种在计算机体系结构和编程领域使用的技术, 旨在提高计算机程序的执行效率和性能. 在传统的计算机体系结构中, 计算机程序由一系列指令组成, 每条指令都需要按照特定的顺序执行. 然而, 某些程序中可能存在一些常见的操作序列, 这些序列在不同的上下文中被重复执行. 宏指令融合技术的目标是将这些常见的操作序列识别出来, 并将它们替换为更高效的宏指令.

通过将常见的操作序列替换为宏指令, 可以减少程序执行时所需的指令数量和内存访问次数, 从而提高程序的执行效率. 宏指令融合技术可以通过编译器或硬件支持来实现. 在编译器层面, 可以通过静态分析程序代码来识别常见的操作序列, 并生成相应的宏指令来替换它们. 在硬件层面, 可以设计专门的指令集体系结构, 支持宏指令的执行和融合.

CKB-VM 在 ckb2021 中引入了宏指令融合技术. 本文将介绍其中一个宏指令融合模式.

思考我们准备做一个除法, 例如 100 / 42, 然后分别获得这个算式的商和余数. 相应的 RISC-V 汇编代码可表示为:

```text
addi t0, t0, 100
addi t1, t1, 42

div a0, t0, t1
rem a1, t0, t1
```

在传统模式下, CKB-VM 会分别执行 div 和 rem 两个指令. 注意到由于我们的 CKB-VM 可以运行在 x86-64 的机器上, x86-64 在计算除法的时候, 商和余数是一起被计算的.

[https://c9x.me/x86/html/file_module_x86_id_72.html](https://c9x.me/x86/html/file_module_x86_id_72.html)

因此, 这里有一个改进空间, 就是当 div 与 rem 指令相邻出现并且它们的两个操作数都相同的时候, 可以使用一条 x86-64 指令替代该 2 条 RISC-V 指令.

CKB-VM 在解码相邻的 div 和 rem 的时候, 会判断它们是否符合融合条件, 然后使用一条内部指令来表示融合前的两条指令. 这条内部指令只对应了一条 x86 指令, 而不是融合前的两条.
