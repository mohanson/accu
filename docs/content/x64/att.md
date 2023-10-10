# X64 汇编/AT&T

在 x64 汇编语法的领域内分成两个流派: NASM 和 AT&T. 大多数国人可能更为熟悉 NASM 语法, 因为它源自 8086 CPU, 许多大学都会开设 8086 CPU 的实验课, 我也是在那是第一次接触 NASM. 后者则流行于 Unix/Linux 平台上, 是目前更为主流的语法.

对我而言, 我更为喜欢 NASM 语法, 不过 AT&T 与 NASM 区别也不大. 在两种语法之间切换并不困难. 我们先来看下典型的 AT&T 语法的样子. 我们编译如下的 C 代码:

```c
int main() {
    return 0;
}
```

```sh
$ gcc -S -o main.s main.c
```

`-S` 命令表示 gcc 在生成汇编代码后停止后续工作. 打开 main.s, 内容如下:

```text
        .file   "main.c"
        .text
        .globl  main
        .type   main, @function
main:
.LFB0:
        .cfi_startproc
        pushq   %rbp
        .cfi_def_cfa_offset 16
        .cfi_offset 6, -16
        movq    %rsp, %rbp
        .cfi_def_cfa_register 6
        movl    $0, %eax
        popq    %rbp
        .cfi_def_cfa 7, 8
        ret
        .cfi_endproc
.LFE0:
        .size   main, .-main
        .ident  "GCC: (Ubuntu 7.5.0-3ubuntu1~18.04) 7.5.0"
        .section        .note.GNU-stack,"",@progbits
```

## AT&T vs NASM (简要区别)

AT&T 语法和 NASM(Netwide Assembler) 语法主要区别如下:

- 语法结构: AT&T 语法使用逗号作为操作数分隔符, 操作数的顺序是目标操作数在前, 源操作数在后. 而 NASM 语法使用逗号作为分隔符, 操作数的顺序是源操作数在前, 目标操作数在后.

例如, 将寄存器 eax 的值加到寄存器 ebx 中, AT&T 语法中的指令是:

```text
addl %eax, %ebx
```

而在 NASM 语法中的指令则是:

```text
add ebx, eax
```

- 寄存器表示: AT&T 语法在寄存器名前使用 % 符号, 而 NASM 语法中不使用 % 符号. 例如, 表示 eax 寄存器时, AT&T 语法为 %eax, 而 NASM 语法为 eax.
- 立即数表示: AT&T 语法使用 $ 符号表示立即数, 而 NASM 语法中不使用 $ 符号. 例如, 表示立即数 10 时, AT&T 语法为 $10, 而 NASM 语法为 10.
- 操作数大小: AT&T 语法在操作码后面使用后缀字符来表示操作数的大小, 例如, b 表示字节, w 表示字, l 表示双字. 而 NASM 语法使用关键字来表示操作数的大小, 例如, BYTE 表示字节, WORD 表示字, DWORD 表示双字.

例如, 将立即数 10 存储到寄存器 eax 中, AT&T 语法为:

```text
movl $10, %eax
```

而在 NASM 语法中的指令则是:

```text
mov eax, 10
```

## AT&T vs NASM (详细区别)

```text
AT&T vs. NASM

There are two main forms of assembly syntax:AT&T and Intel.
AT&T syntax is used by the GNU Assembler(gas), contained in the gcc compiler suite, and is often used by Linux developers.
Of the Intel syntax assemblers, the Netwide Assembler(NASM) is the most commonly used.
The NSAM format is used by many windows assemblers and debuggers.
The two formats yield exactly the same machine language; however, there are a few differences in style and format:

The source and destination operands are reversed, and different symbols are used to mark the beginning of a comment:
    NASM format CMD <dest>, <source><comment>
    AT&T format CMD <source>, <dest><#comment>
    AT&T format uses a % before registers; NASM does not
    AT&T format uses a $ before literal values; NASM does not
    AT&T handles memory reference differnetly than NASM

mov
The mov command copies data from the source to the destination. The value is not removed from the source location.
    NASM Syntax          NASM Example            AT&T Example
    mov<dest>,<source>   mov eax, 51h;comment    movl $51, %eax#comment

Data cannot be moved directly from memory to a segment register. Instead, you must use a general purpose register as an intermediate step;

mov eax, 1234h; sotre the value 1234 (hex) into EAX
mov cs, ax; then copy the value of AX into CS.

add and sub
The add command adds the source to the destination and stores the result in the destination.
The sub command subtracts the source form the destionation and stores the result in the destination
    NASM Syntax               NASM Example        AT&T Example
    add <dest>, <source>      add eax, 51h        addl $51h, %eax
    sub <dest>, <source>      sub eax, 51h        subl $51h, %eax

push and pop
The push and pop commands push and pop items from the stack
    NASM Syntax        NASM Example         AT&T Example
    push <value>       push eax             pushl %eax
    pop <dest>         pop eax              popl %eax

xor
The xor command conduts a bitwise logical "exclusive or" (XOR) function. XOR value, value to zero out or clear a register or memory location
    NASM Syntax            NASM Example      AT&T Example
    xor <dest>, <source>   xor eax, eax      xor %eax, %eax

The jne, je, jz, and jmp commands branch the flow of the program to another location based on the value of the eflag "zero flag."
jne/jnz jumps if the "zero flag"=0; je/jz jumps if the "zero flag"=1; and jmp always jumps.
    NASM Example              NASM Example      AT&T Example
    jnz <dest> / jne <dest>   jne start         jne start
    jz <dest> / je <dest>     jz loop           jz loop
    jmp <dest>                jmp end           jmp end

call and ret
The call command calls a procedure (not jumps to a label). The ret command is used at the end of a procedure to return the flow to the command after the call.
    NASM Example       NASM Example        AT&T Example
    call <dest>        call subroutine1    call subroutine1
    ret                ret                 ret

inc and dec
The inc and dec commands increment or decrement the destination, respectively.
    NASM Example        NASM Example       AT&T Example
    inc <dest>          inc eax            incl %eax
    dec <dest>          dec eax            decl %eax

lea
The lea command loads the effective address of the source into the destination
    NASM Example            NASM Example        AT&T Example
    lea <dest>, <source>    lea eax, [dsi+4]    leal 4(%dsi), %eax

int
The int command throws asystem interrupt signal to the processor. The common interrupt you will use is 0x80, which signals a system call to the kernel.
    NASM Syntax      NASM Example    AT&T Example
    int <val>        int 0x80        int $0x80

Addressing Modes
In assembly, several methods can be used to accomplish the same thing.
In particular, there are many ways to indicate the effective address to manipulate in memory.
These options are called addressing modes.

Register: Registers hold the data to be manipulated / No memory interaction / Both registers must be the same size
    NASM Example: mov ebx, edx / add al, ch
Immediate: The source operand is a numerical value / Decimal is assumed; use h for hex
    NASM Example: mov eax, 1234h / mov dx, 301
Direct: The first operand is the address of memory to manipulate / It's marked with brackets.
    NASM Example: mov bh, 100 / mov [4321h], bh
Register Indirect: The first operand is a regsiter in brackets that holds the address to be manipulated
    NASM Example: mov [di], ecx
Based Relative: The effective address to be manipulated is calculated by using ebx or ebp plus an offset value
    NASM Example: mov edx, 20[ebx]
Indexed Relative: Same as Based Relative, but edi and esi are used to hold the offset
    NASM Example: mov ecx, 20[esi]
Based Indexed-Relative: The effective address is found by combining Based and Indexed Relative modes
    NASM Example: mov ax, [bx][si]+1
```

## 参考

- [1] Allen Harper. Gray Hat Hacking the Ethical Hacker's Handbook.
