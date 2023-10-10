# X64 汇编/术语和概念

在第一篇文章中的某些部分可能对初学者来说不太清楚, 这就是为什么我们在本文会对术语和概念的理解开始.

**syscall**: 在计算中, 系统调用(通常缩写为 syscall)是一种编程方式, 处于用户态的计算机程序向操作系统的内核请求服务. 这可能包括与硬件相关的服务(例如, 访问硬盘驱动器), 创建和执行新进程以及与诸如进程调度之类的集成内核服务进行通信. 系统调用提供了进程与操作系统之间的基本接口.

**栈**: 处理器的寄存器数量非常有限, 所以栈是一块可寻址的连续内存区域, 用于暂时存放数据. 我们将在下一部分中对栈进行仔细研究.

**段**: 每个汇编程序都由段组成. 有以下几个类型: data, bss 和 text. data 段用于声明已初始化的数据或常量, bss 段用于声明未初始化的变量, text 段​用于存储代码.

**寄存器**: x64 有 16 个通用寄存器, 分别是 rax, rbx, rcx, rdx, rbp, rsp, rsi, rdi, r8, r9, r10, r11, r12, r13, r14 和 r15. 此外, 其中一些低字节寄存器可以作为 32 位, 16 位或 8 位寄存器独立访问.

| 8-byte register | Bytes 0-3 | Bytes 0-1 | Byte 0 |
| --------------- | --------- | --------- | ------ |
| rax             | eax       | ax        | al     |
| rcx             | ecx       | cx        | cl     |
| rdx             | edx       | dx        | dl     |
| rbx             | ebx       | bx        | bl     |
| rsi             | esi       | si        | sil    |
| rdi             | edi       | di        | dil    |
| rsp             | esp       | sp        | spl    |
| rbp             | ebp       | bp        | bpl    |
| r8              | r8d       | r8w       | r8b    |
| r9              | r9d       | r9w       | r9b    |
| r10             | r10d      | r10w      | r10b   |
| r11             | r11d      | r11w      | r11b   |
| r12             | r12d      | r12w      | r12b   |
| r13             | r13d      | r13w      | r13b   |
| r14             | r14d      | r14w      | r14b   |
| r15             | r15d      | r15w      | r15b   |

## 数据类型

x64 有四种基本数据类型, 分别是:

| 字节数 | 英文名 | 缩写 |
| ------ | ------ | ---- |
| 1      | byte   | b    |
| 2      | word   | w    |
| 4      | dword  | l    |
| 8      | qword  | q    |

通常情况下, 不需要显示指定数据类型, 因为可以从操作数上做出合理猜测. 单另一个操作数未暗示本操作数的数据类型时, 需要显示指定数据类型, 例如如下汇编代码(从 0x1000 地址读取 1 Byte, 0 扩展至 eax 寄存器中).

```text
movzx eax, byte [0x1000]
```

## 段

正如我在上面所写, 每个汇编程序都由段组成, 它可以是数据部分, 代码部分和 bss 部分.

## 伪指令

伪指令虽然不是真正的 x64 机器指令, 但还是在指令领域中使用, 因为这是放置指令最方便的地方. 当前可用的伪指令是 DB, DW, DD, DQ, DT, DDQ, DO 以及它们的未初始化的版本 RESB, RESW, RESD, RESQ, REST, RESDDQ 和 RESO, INCBIN, EQU 和 TIMES 前缀. 下面的伪指令均只在数据段被使用.

**声明已初始化的数据**

```text
db      0x55                ; just the byte 0x55
db      0x55,0x56,0x57      ; three bytes in succession
db      'a',0x55            ; character constants are OK
db      'hello',13,10,'$'   ; so are string constants
dw      0x1234              ; 0x34 0x12
dw      'a'                 ; 0x41 0x00 (it's just a number)
dw      'ab'                ; 0x41 0x42 (character constant)
dw      'abc'               ; 0x41 0x42 0x43 0x00 (string)
dd      0x12345678          ; 0x78 0x56 0x34 0x12
dq      0x1122334455667788  ; 0x88 0x77 0x66 0x55 0x44 0x33 0x22 0x11
ddq     0x112233445566778899aabbccddeeff00
; 0x00 0xff 0xee 0xdd 0xcc 0xbb 0xaa 0x99
; 0x88 0x77 0x66 0x55 0x44 0x33 0x22 0x11
do     0x112233445566778899aabbccddeeff00 ; same as previous
dd      1.234567e20         ; floating-point constant
dq      1.234567e20         ; double-precision float
dt      1.234567e20         ; extended-precision float
```

**声明未初始化的数据**

```text
buffer:         resb    64      ; reserve 64 bytes
wordvar:        resw    1       ; reserve a word
realarray       resq    10      ; array of ten reals
```

**载入外部二进制文件**

```text
incbin "file.dat"          ; include the whole file
incbin "file.dat",1024     ; skip the first 1024 bytes
incbin "file.dat",1024,512 ; skip the first 1024, and actually include at most 512
```

**定义常数**

```text
message db 'hello, world'
msglen  equ $-message
```

**重复指令或数据**

```text
zerobuf:        times 64 db 0
```

## 算数运算

汇编中有一些算数运算指令用于进行算数运算, 例如如下汇编代码计算了 0 + 8 - 3 的值:

```text
section .text
global _start
_start:
    xor rdi, rdi
    add rdi, 8
    sub rdi, 3
    mov rax, 60
    syscall
```

## 流程控制

通常, 编程语言可以更改程序的执行顺序(如 if 语句, switch-case 语句, goto 等), 汇编语言当然也可以. cmp 指令用于在两个值之间执行比较, 它可与条件跳转指令一起用于流程控制, 例如:

```text
cmp rax, 50
```

cmp 指令仅比较 2 个操作数的值, 但不改变它们, 并且不执行任何操作, 但比较结果会保存在标志寄存器中. 条件跳转指令根据标志寄存器的标志位来判断是否进行跳转操作.

|   Instruction   |            Description            |
| --------------- | --------------------------------- |
| jmp Label       | Jump to label                     |
| jmp *Operand    | Jump to specified location        |
| je / jz Label   | Jump if equal/zero                |
| jne / jnz Label | Jump if not equal/nonzero         |
| js Label        | Jump if negative                  |
| jns Label       | Jump if non negative              |
| jg / jnle Label | Jump if greater (signed)          |
| jge / jnl Label | Jump if greater or equal (signed) |
| jl / jnge Label | Jump if less (signed)             |
| jle / jng Label | Jump if less or equal             |
| ja / jnbe Label | Jump if above (unsigned)          |
| jae / jnb Label | Jump if above or equal (unsigned) |
| jb / jnae Label | Jump if below (unsigned)          |
| jbe / jna Label | Jump if below or equal (unsigned) |

我们编写一个求 1 + 2 + ... + 100 的程序, 程序中使用到了比较和条件跳转指令. 另外, 由于我们使用 printf 函数打印出结果, 因此在编译的时候需要链接系统库.

```text
;------------------------------------------------------------------------------
; nasm -f elf64 -o main.o main.asm
; ld main.o -o main -lc --dynamic-linker /lib64/ld-linux-x86-64.so.2
;------------------------------------------------------------------------------
section .data
    msg db "%d", 0x0A

section .text
    global _start
    extern printf
_start:
    xor rsi, rsi
    mov rcx, 100
b1:
    cmp rcx, 0
    je  b2
    add rsi, rcx
    sub rcx, 1
    jmp b1
b2:
    mov rdi, msg
    call printf
    syscall
    mov rax, 60
    mov rdi, 0
    syscall
```
