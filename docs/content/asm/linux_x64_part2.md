# 术语和概念

在第一篇文章中的某些部分可能对初学者来说不太清楚, 这就是为什么我们在本文会对术语和概念的理解开始.

- Syscall: 在计算中, 系统调用(通常缩写为 syscall)是一种编程方式, 处于用户态的计算机程序向操作系统的内核请求服务. 这可能包括与硬件相关的服务(例如, 访问硬盘驱动器), 创建和执行新进程以及与诸如进程调度之类的集成内核服务进行通信. 系统调用提供了进程与操作系统之间的基本接口.
- Stack: 处理器的寄存器数量非常有限, 所以 Stack 是一块可寻址的连续内存区域, 用于暂时存放数据. 我们将在下一部分中对 Stack 进行仔细研究.
- Section: 每个汇编程序都由段组成. 有以下几个类型:
    - data: 该节于声明已初始化的数据或常量
    - bss: 该节用于声明未初始化的变量
    - text: ​​该节用于存储代码
- General-purpose registers: 有 16 个通用寄存器, 分别是 rax, rbx, rcx, rdx, rbp, rsp, rsi, rdi, r8, r9, r10, r11, r12, r13, r14, r15.

# 数据类型

基本数据类型为字节(bytes), 字(words), 双字(doublewords), 四字(quadwords)和双四字(double quadwords). 字节为 8 位, 字为 2 字节, 双字为 4 字节, 四字为 8 字节, 双四字为 16 字节(128 位).

# 段

正如我在上面所写, 每个汇编程序都由段组成, 它可以是数据部分, 文本部分和 bss 部分. 让我们看一下数据部分. 例如:

```nasm
section .data
    num1:   equ 100
    num2:   equ 50
    msg:    db "Sum is correct", 10
```

NASM 支持许多伪指令, equ, db 都是其中之一.

- DB, DW, DD, DQ, DT, DO, DY 和 DZ 用于声明初始化的数据.
- RESB, RESW, RESD, RESQ, REST, RESO, RESY 和 RESZ 用于声明未初始化的变量.
- INCBIN 包含外部二进制文件
- EQU 用于定义常数
- TIMES 用于重复指定次数的指令或数据

# 算数运算

汇编中有一些算数运算指令用于进行算数运算, 例如

- ADD - integer add
- SUB - substract
- MUL - unsigned multiply
- IMUL - signed multiply
- DIV - unsigned divide
- IDIV - signed divide
- INC - increment
- DEC - decrement
- NEG - negate

# 流程控制

通常, 编程语言可以更改程序的执行顺序(如 if 语句, switch-case 语句, goto 等), 汇编语言当然也可以. cmp 指令用于在两个值之间执行比较, 它可与条件跳转指令一起用于流程控制, 例如:

```nasm
;; compare rax with 50
cmp rax, 50
```

cmp 指令仅比较 2 个操作数的值, 但不改变它们, 并且不执行任何操作, 但比较结果会保存在标志寄存器中. 条件跳转指令根据标志寄存器的标志位来判断是否进行跳转操作.

- JE - if equal
- JZ - if zero
- JNE - if not equal
- JNZ - if not zero
- JG - if first operand is greater than second
- JGE - if first operand is greater or equal to second
- JA - the same that JG, but performs unsigned comparison
- JAE - the same that JGE, but performs unsigned comparison

例如, 如果我们在 C 语言中做实现下面的 if/else 的语句:

```c
if (rax != 50) {
    exit();
} else {
    right();
}
```

则其对应的汇编代码为:

```nasm
;; compare rax with 50
cmp rax, 50
;; perform .exit if rax is not equal 50
jne .exit
jmp .right
```
