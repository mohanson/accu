# Linux x64 汇编/汇编与 C

通常我们并不直接编写汇编代码, 而是将其与 C 语言一并使用. 原因可能是多样的, 就我个人而言, 一定是某些功能无法在 C 中实现, 才会考虑使用汇编. 尽管现代编译器的优化已经做得还不错了, 但还是不如自己手写的汇编代码. 实际上, 我们有 3 种不同的方式来联合使用它们:

- 从 C 代码调用汇编程序
- 从汇编代码调用 C 程序
- 在 C 代码中的内联汇编

让我们编写 3 个简单的例子程序, 来展示这三种情况.

## 在 C 里面调用汇编

首先让我们编写如下的简单 C 程序:

```c
#include <string.h>

extern void echo(char *str, int size);

int main() {
	char* str = "Hello World!\n";
	int len = strlen(str);
	echo(str, len);
	return 0;
}
```

在这里, C 代码申明了一个外部函数 print, 这表明这个函数的实现并不在 C 代码内部. 当我们调用函数时, 前 6 个参数通过 rdi, rsi, rdx, rcx, r8 和 r9 传递, 其余全部通过堆栈. 因此, 我们可以从 rdi 和 rsi 寄存器中获取第一个和第二个参数, 也就是字符串的指针和字符串长度.

```text
global echo

section .text
echo:
    mov r10, rdi
    mov r11, rsi
    mov rax, 1
    mov rdi, 1
    mov rsi, r10
    mov rdx, r11
    syscall
    ret
```

现在, 可以使用如下命令进行编译:

```sh
$ nasm -f elf64 -o echo.o echo.s
$ gcc -o main main.c echo.o
$ ./main
Hello World!
```

## 内联汇编

有一种更常见的用法是在 C 源代码中直接使用汇编代码, 这需要一种特殊的语法:

```text
__asm__ [volatile] (
	"assembly code"
	: output operand
	: input operand
	: clobbers
);
```

这种格式由四部分组成, 第一部分是汇编指令, 和上面的例子一样, 第二部分和第三部分是约束条件, 第二部分指示汇编指令的运算结果要输出到哪些 C 操作数中, 第三部分指示汇编指令需要从哪些 C 操作数获得输入, 第四部分是在汇编指令中被修改过的寄存器列表, 指示编译器哪些寄存器的值在执行这条内联汇编语句时会改变. 后三个部分都是可选的, 如果有就填写, 没有就空着只写个冒号.

我们的例子程序现在可以写成这个样子:

```c
#include <string.h>
#include <stdint.h>

int main() {
	char* str = "Hello World!\n";
	uint64_t len = strlen(str);
	uint64_t ret = 0;

	__asm__(
		"movq $1, %%rax\n"
		"movq $1, %%rdi\n"
		"movq %1, %%rsi\n"
		"movq %2, %%rdx\n"
		"syscall\n"
		: "=r"(ret)
		: "r"(str), "r"(len)
		: "%rax", "%rdi", "%rsi", "%rdx"
	);
	return ret;
}
```

```sh
$ gcc -o main main.c
$ ./main
Hello World!
```

## 在汇编中调用 C

最后一种方法是从汇编代码中调用 C 函数. 例如, 我们有一个简单的 C 代码, 其中一个函数仅打印 Hello World!:

```c
#include <stdio.h>

extern int echo();

int echo() {
	printf("Hello World!\n");
	return 0;
}
```

现在, 我们可以在汇编代码中将此函数定义为 extern, 并使用调用指令对其进行调用, 就像我们在以前的文章中做的很多次一样.

```text
extern echo

section .text
global _start
_start:
	call echo
	mov rax, 60
	mov rdi, 0
	syscall
```

```sh
$ gcc -c -o echo.o echo.c
$ nasm -f elf64 -o main.o main.asm
$ ld -dynamic-linker /lib64/ld-linux-x86-64.so.2 -o main -lc echo.o main.o
$ ./main
Hello World!
```
