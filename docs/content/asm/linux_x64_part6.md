本文我们将研究如何将 C 与汇编一起使用. 实际上, 我们有 3 种不同的方式来联合使用它们:

- 从 C 代码调用汇编程序
- 从汇编代码调用 C 程序
- 在 C 代码中使用内联汇编

让我们编写 3 个简单的 Hello World! 程序, 来展示这三种情况.

# 在 C 里面调用汇编

首先让我们编写如下的简单 C 程序:

```c
#include <string.h>

extern void print(char *str, int size);

int main() {
	char* str = "Hello World\n";
	int len = strlen(str);
	print(str, len);
	return 0;
}
```

在这里, C 代码申明了一个外部函数 print, 这表明这个函数的实现并不在 C 代码内部. 当我们调用函数时, 前 6 个参数通过 rdi, rsi, rdx, rcx, r8 和 r9 传递, 其余全部通过堆栈. 因此, 我们可以从 rdi 和 rsi 寄存器中获取第一个和第二个参数, 也就是字符串的指针和字符串长度.

```nasm
global print

section .text
print:
		;; 1 arg
		mov r10, rdi
		;; 2 arg
		mov r11, rsi
		;; call write syscall
		mov rax, 1
		mov rdi, 1
		mov rsi, r10
		mov rdx, r11
		syscall
		ret
```

现在, 可以使用如下命令进行编译:

```sh
$ nasm -f elf64 -o main.o main.asm
$ ld -o main main.o
$ ./main
```

# 内联汇编

可以在 C 源代码中直接使用汇编代码, 为此需要一种特殊的语法:

```no-highlight
asm [volatile] ("assembly code" : output operand : input operand : clobbers);
```

我们的 Hello World! 程序现在可以写成这个样子:

```c
#include <string.h>

int main() {
	char* str = "Hello World!\n";
	long len = strlen(str);
	int ret = 0;

	__asm__(
		"movq $1, %%rax\n"
		"movq $1, %%rdi\n"
		"movq %1, %%rsi\n"
		"movl %2, %%edx\n"
		"syscall\n"
		: "=g"(ret)
		: "g"(str), "g"(len));

	return 0;
}
```

每个输入参数和输出参数都由约束字符串进行描述, 用来限制操作数的存储位置.

- r: 通用寄存器
- g: 允许使用任何寄存器, 内存或立即数整数, 但不是通用寄存器的寄存器除外
- f: 浮点寄存器
- m: 允许使用内存操作数

# 在汇编中调用 C

最后一种方法是从汇编代码中调用 C 函数. 例如, 我们有一个简单的C代码, 其中一个函数仅打印 Hello World!:

```c
#include <stdio.h>

extern int print();

int print() {
	printf("Hello World!\n");
	return 0;
}
```

现在, 我们可以在汇编代码中将此函数定义为 extern, 并使用调用指令对其进行调用, 就像我们在以前的文章中做的很多次一样.

```nasm
global _start

extern print

section .text
_start:
		call print
		mov rax, 60
		mov rdi, 0
		syscall
```

```sh
$ gcc -o print.o -c print.c
$ nasm -f elf64 -o main.o main.asm
$ ld -dynamic-linker /lib64/ld-linux-x86-64.so.2 -lc casm.o c.o -o casm
```
