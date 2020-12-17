# Linux x64 汇编/宏

NASM 支持两种形式的宏:

- 单行
- 多行

所有单行宏都必须从 `%define` 指令开始, 形式如下:

```nasm
%define macro_name(parameter) value
```

NASM 宏的行为与 C 中的行为非常相似, 例如, 我们可以创建以下单行宏:

```nasm
%define argc rsp + 8
%define cliArg1 rsp + 24
```

然后就可以在代码中使用它:

```nasm
;;
;; argc will be expanded to rsp + 8
;;
mov rax, [argc]
cmp rax, 3
jne .mustBe3args
```

多行宏以 `%macro` 指令开头, 并以 `%endmacro` 结尾. 它的一般形式如下:

```nasm
%macro name number_of_parameters
    instruction
    instruction
    instruction
%endmacro
```
