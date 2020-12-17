# Linux x64 汇编/AT&T

我们将介绍 AT&T 汇编语法. 之前的文章中, 我们都使用了 nasm 汇编器, 但是还有一些其他汇编器, 它们使用了不同的语法. gcc 使用 GNU 汇编器, 尝试看看将一个 C 代码编译到汇编输出.

```c
#include <unistd.h>

int main(void) {
	write(1, "Hello World\n", 15);
	return 0;
}
```

```sh
$ gcc -o main.S -S main.c
```

```no-highlight
	.file	"main.c"
	.text
	.section	.rodata
.LC0:
	.string	"Hello World\n"
	.text
	.globl	main
	.type	main, @function
main:
.LFB0:
	.cfi_startproc
	pushq	%rbp
	.cfi_def_cfa_offset 16
	.cfi_offset 6, -16
	movq	%rsp, %rbp
	.cfi_def_cfa_register 6
	movl	$15, %edx
	leaq	.LC0(%rip), %rsi
	movl	$1, %edi
	call	write@PLT
	movl	$0, %eax
	popq	%rbp
	.cfi_def_cfa 7, 8
	ret
	.cfi_endproc
.LFE0:
	.size	main, .-main
	.ident	"GCC: (Ubuntu 7.5.0-3ubuntu1~18.04) 7.5.0"
	.section	.note.GNU-stack,"",@progbits
```

它看起来与 NASM 有很大的不同.

## 区别

在 AT&T 汇编格式中, 寄存器名要加上 % 作为前缀; 而在 Intel 汇编格式中, 寄存器名不需要加前缀.

 AT&T 格式   | Intel 格式
------------ | ----------
`pushl %eax` | `push eax`

在 AT&T 汇编格式中, 用 $ 前缀表示一个立即操作数; 而在 Intel 汇编格式中, 立即数的表示不用带任何前缀.

AT&T 格式  | Intel 格式
---------- | ----------
`pushl $1` | `push 1`

AT&T 和 Intel 格式中的源操作数和目标操作数的位置正好相反. 在 Intel 汇编格式中, 目标操作数在源操作数的左边; 而在 AT&T 汇编格式中, 目标操作数在源操作数的右边.

   AT&T 格式    |  Intel 格式
--------------- | ------------
`addl $1, %eax` | `add eax, 1`

在 AT&T 汇编格式中, 操作数的字长由操作符的最后一个字母决定, 后缀 b, w, l 分别表示操作数为字节, 字和双字; 而在 Intel 汇编格式中, 操作数的字长是用 byte ptr 和 word ptr 等前缀来表示的.

   AT&T 格式    |       Intel 格式
--------------- | ----------------------
`movb val, %al` | `mov al, byte ptr val`

在 AT&T 汇编格式中, 绝对转移和调用指令(jump/call)的操作数前要加上 \* 作为前缀, 而在 Intel 格式中则不需要. 远程转移指令和远程子调用指令的操作码, 在 AT&T 汇编格式中为 ljump 和 lcall, 而在 Intel 汇编格式中则为 jmp far 和 call far, 即:

        AT&T 格式         |        Intel 格式
------------------------- | -------------------------
`ljump $section, $offset` | `jmp far section:offset`
`lcall $section, $offset` | `call far section:offset`

与之相应的远程返回指令则为:

     AT&T 格式       |       Intel 格式
-------------------- | ----------------------
`lret $stack_adjust` | `ret far stack_adjust`

内存操作数的寻址方式不同

            AT&T 格式              |              Intel 格式
---------------------------------- | -------------------------------------
`section:disp(base, index, scale)` | `section:[base + index*scale + disp]`
