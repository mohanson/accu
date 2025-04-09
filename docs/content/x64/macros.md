# X64 汇编/宏

当我调用一个函数时, 我并不知道它会修改哪些寄存器, 因此我通常会决定将所有易失性寄存器保存起来, 然后在调用结束之后恢复寄存器的值. 同时, 我会确保 rsp 是 16 字节对齐的. 如果 rsp 已经是 16 字节对齐, 那我什么都不用做; 如果它不是, 那我会主动推入 8 个随机字节到栈上. 在函数调用结束后, 为了使栈保持平衡, 我必须确认在这次调用前我是否推入了额外的 8 个字节数据. 这些步骤看起来很麻烦, 但使用汇编编写的话只需要如下几行:

```text
push rax
push rcx
push rdx
push rdi
push rsi
push r8
push r9
push r10
push r11
push rbp
mov rbp, rsp
and rsp, -16
;-----------------------
; call any function here
;-----------------------
mov rsp, rbp
pop rbp
pop r11
pop r10
pop r9
pop r8
pop rsi
pop rdi
pop rdx
pop rcx
pop rax
```

它能很好的工作. 但对于我来说, 每次调用函数时都要重复的复制和粘贴代码太麻烦了. 我可以使用宏来进行优化. 宏能在编译期展开, 因而不会对性能有任何的影响.

Nasm 支持两种形式的宏, 分别是单行和多行宏. 我们先从多行宏开始. 多行宏以 `%macro` 指令开头, 并以 `%endmacro` 结尾. 它的一般形式如下:

```text
%macro name number_of_parameters
    instruction
    instruction
    instruction
%endmacro
```

我们可以使用多行宏改写我们的代码, 将它们封装为 `prepcall` 和 `postcall` 两个宏.

```text
%macro prepcall 0
push rax
push rcx
push rdx
push rdi
push rsi
push r8
push r9
push r10
push r11
push rbp
mov rbp, rsp
and rsp, -16
%endmacro

%macro postcall 0
mov rsp, rbp
pop rbp
pop r11
pop r10
pop r9
pop r8
pop rsi
pop rdi
pop rdx
pop rcx
pop rax
%endmacro
```

然后就可以在代码中使用它:

```text
prepcall
call printf
postcall
```

至于单行宏, 它和 c 中的语法非常相似. 所有单行宏都必须从 `%define` 指令开始, 形式如下:

```text
%define macro_name(parameter) value
```

我们可以创建以下的三个单行宏, 下面的代码会读取你的命令行输入, 然后打印出来.

```text
%define arg0 rsp + 8
%define arg1 rsp + 16
%define arg2 rsp + 24

section .data
    msg db "%s", 0x0A

section .text
    global _start
    extern printf
_start:
    mov rdi, msg
    mov rsi, [arg0]
    call printf
    mov rdi, msg
    mov rsi, [arg1]
    call printf
    mov rdi, msg
    mov rsi, [arg2]
    call printf
    syscall
    mov rax, 60
    mov rdi, 0
    syscall
```

```sh
$ nasm -f elf64 -o main.o main.asm
$ ld -o main -lc --dynamic-linker /lib64/ld-linux-x86-64.so.2 main.o
$ ./main Hello World!
$ ./main
# Hello
# World!
```
