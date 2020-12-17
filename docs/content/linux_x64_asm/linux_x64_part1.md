# Linux x64 汇编/Hello World

我们每天产出大量的<del>垃圾</del>代码, 我们每个人都可以像这样简单地编写最简单的代码:

```c
#include <stdio.h>

int main() {
  int x = 10;
  int y = 100;
  printf("x + y = %d", x + y);
  return 0;
}
```

希望读者们都可以理解上述 C 代码的作用. 但是, 此代码在底层如何工作? 我认为并非所有人都能回答这个问题, 我也是. 我可以用Haskell, Erlang, Go 等高级编程语言编写代码, 但是在它们编译后我并不知道它在底层是如何工作的. 因此, 我决定采取一些更深入的步骤, 进行记录, 并描述我对此的学习过程. 希望这个过程不仅仅只是对我来说很有趣. 让我们开始吧.

## 准备

开始之前, 我们必须准备一些事情, 如我所写的那样, 我目前使用 Ubuntu 18.04, 因此我的文章将针对该操作系统和体系结构. 不同的 CPU 支持不同的指令集, 目前我使用 Intel 的 64 位 CPU. 同时我也将使用 NASM 语法. 您可以使用以下方法安装它:

```sh
$ apt install nasm
```

记住, Netwide Assembler(简称 NASM)是一款基于英特尔 x86 架构的汇编与反汇编工具. 这就是我们目前需要的. 其他工具将在下一篇文章中介绍.

## NASM 语法

在这里, 我将不介绍完整的汇编语法, 我们仅提及其庞大语法的一小部分, 也是那些我们将在本文中使用到的部分. 通常, NASM 程序分为几个段(section), 在这篇文章中, 我们将遇到以下两个段:

* 数据: data section
* 文本: text section

数据部分用于声明常量, 此数据在运行时不会更改. 声明数据部分的语法为:

```text
section .data
```

文本部分用于代码. 该部分必须以全局声明 _start 开头, 该声明告诉内核程序从何处开始执行.

```text
section .text
global _start
_start:
```

注释以符号 `;` 开头. 每条 NASM 源代码行都包含以下四个字段的某种组合:

```text
[label:] instruction [operands] [; comment]
```

方括号中的字段是可选的. 基本的 NASM 指令由两部分组成, 第一部分是要执行的指令的名称, 第二部分是该命令的操作数. 例如:

```text
mov rax, 48 ; put value 48 in the rax register
```

## Hello World!

让我们用 NASM 编写第一个程序. 当然, 这将是传统的 Hello World! 程序. 这是它的代码:

```text
section .data
    msg db "Hello World!", 0x0A

section .text
global _start
_start:
    mov rax, 1
    mov rdi, 1
    mov rsi, msg
    mov rdx, 13
    syscall
    mov rax, 60
    mov rdi, 0
    syscall
```

是的, 它看起来一点都不像 `printf("Hello World!\n")`. 让我们尝试了解它是什么以及它如何工作. 首先看第一和第二行, 我们定义了数据部分, 并将 msg 常量与 "Hello, World!" 值放在一起. 现在, 我们可以在代码中使用此常量. 接下来是声明文本部分和程序的入口. 程序将从 7 行开始执行. 现在开始最有趣的部分, 我们已经知道 mov 指令是什么, 它获得 2 个操作数, 并将第二个的值放在第一位. 但是这些 rax, rdi 等是什么? 正如我们在 Wikipedia 中可以看到的:

> 中央处理器(CPU)是计算机中的硬件, 它通过执行系统的基本算术, 逻辑和输入/输出操作来执行计算机程序的指令.

好的, CPU 会执行一些运算. 但是, 在哪里可以获取该运算的数据, 是内存吗? 从内存中读取数据并将数据写回到内存中会减慢处理器的速度, 因为它涉及通过控制总线发送数据请求的复杂过程. 因此, CPU 具有自己的内部存储器, 称为寄存器.

因此, 当我们编写 `mov rax, 1` 时, 意味着将 1 放入 rax 寄存器. 现在我们知道 rax，rdi，rsi 等代表了什么了, 但是还需要知道什么时候该使用 rax 什么时候使用 rdi 等.

- rax, 临时寄存器. 当我们调用 syscall 时, rax 必须包含 syscall 号码
- rdi, 用于将第 1 个参数传递给函数
- rsi, 用于将第 2 个参数传递给函数
- rdx, 用于将第 3 个参数传递给函数

换句话说, 我们只是在调用 `sys_write` syscall. 看看 `sys_write` 的定义:

```c
size_t sys_write(unsigned int fd, const char * buf, size_t count);
```

它具有3个参数:

- fd, 文件描述符. 对于 stdin，stdout 和 stderr 来说，其值分别为 0, 1 和 2
- buf, 指向字符数组
- count, 指定要写入的字节数

我们将 1 写入 rax, 这意味我们要调用 `sys_write`. 完整的 syscall 列表可以在 [https://github.com/torvalds/linux/blob/master/arch/x86/entry/syscalls/syscall_64.tbl](https://github.com/torvalds/linux/blob/master/arch/x86/entry/syscalls/syscall_64.tbl) 找到. 在完成该调用之后, 将 60 写入 rax, 这意味着我们要调用 `sys_exit` 退出程序, 且退出码为 0.

最后, 让我们来构建这个程序, 我们需要执行以下命令:

```sh
$ nasm -f elf64 -o main.o main.asm
$ ld -o main main.o
```

尝试运行这个程序吧!
