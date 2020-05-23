# Brainfuck 解释器与 IR 优化

Brainfuck 是一种简单且最小的图灵完备编程语言. 这种语言由八种运算符构成:

| 字符 |                              含义                               |
| ---- | --------------------------------------------------------------- |
| >    | 指针加一                                                        |
| <    | 指针减一                                                        |
| +    | 指针指向的字节的值加一                                          |
| -    | 指针指向的字节的值减一                                          |
| .    | 输出指针指向的单元内容(ASCII码)                                 |
| ,    | 输入内容到指针指向的单元(ASCII码)                               |
| [    | 如果指针指向的单元值为零，向后跳转到对应的 ] 指令的次一指令处   |
| ]    | 如果指针指向的单元值不为零，向前跳转到对应的 [ 指令的次一指令处 |

Brainfuck 完全模仿了图灵纸带机, 后者则是计算机的老祖宗. 理论上一切能被计算的问题都能通过 Brainfuck 被计算(注: 有些问题是不能被计算的, 对于这些问题现代计算机也无能无力).

Brainfuck 可以通过解释器实现, 也能通过编译器实现. 当然本文的目的是介绍 JIT 方案, 因此必须得先实现一个解释器(没错!). 我会使用 Rust 来编写这个解释器并省略了一部分无关紧要的代码, 以使得核心逻辑清晰.

定义一个枚举类型 Opcode 来代表以上的 8 个字符, 然后编写一个转换函数将字节转换为 Opcode. 由于 `[` 与 `]` 总是成双成对的出现且互相关联, 代码内使用了 jtable 来存储它们之间的位置关系, 以便快速决定跳转的位置.

```rs
#[derive(Debug, PartialEq)]
pub enum Opcode {
    SHR = 0x3E,
    SHL = 0x3C,
    ADD = 0x2B,
    SUB = 0x2D,
    PUTCHAR = 0x2E,
    GETCHAR = 0x2C,
    LB = 0x5B,
    RB = 0x5D,
}

pub struct Code {
    pub instrs: Vec<Opcode>,
    pub jtable: std::collections::HashMap<usize, usize>,
}

impl Code {
    pub fn from(data: Vec<u8>) -> Result<Self, Box<dyn std::error::Error>> {
        // transform bytes to opcodes
        // ...
    }
}
```

再拿到 Opcode 数组之后, 便可以编写针对 Opcode 解释器. Brainfuck 的执行需要首先定义一个栈, 一个栈指针 SP, 源码以及计数器 PC.

```rs
struct Interpreter {
    stack: Vec<u8>,
}

impl Interpreter {
    fn run(&mut self, data: Vec<u8>) -> Result<(), Box<dyn std::error::Error>> {
        let code = Code::from(data)?;
        let code_len = code.instrs.len();
        let mut pc = 0;
        let mut ps = 0;
        loop {
            if pc >= code_len {
                break;
            }
            match code.instrs[pc] {
                Opcode::SHL => ps = if ps == 0 { 0 } else { ps - 1 },
                Opcode::SHR => {
                    ps += 1;
                    if ps == self.stack.len() {
                        self.stack.push(0)
                    }
                }
                Opcode::ADD => {
                    self.stack[ps] = self.stack[ps].overflowing_add(1).0;
                }
                Opcode::SUB => {
                    self.stack[ps] = self.stack[ps].overflowing_sub(1).0;
                }
                Opcode::PUTCHAR => {
                    std::io::stdout().write_all(&[self.stack[ps]])?;
                }
                Opcode::GETCHAR => {
                    let mut buf: Vec<u8> = vec![0; 1];
                    std::io::stdin().read_exact(&mut buf)?;
                    self.stack[ps] = buf[0];
                }
                Opcode::LB => {
                    if self.stack[ps] == 0x00 {
                        pc = code.jtable[&pc];
                    }
                }
                Opcode::RB => {
                    if self.stack[ps] != 0x00 {
                        pc = code.jtable[&pc];
                    }
                }
            }
            pc += 1;
        }
        Ok(())
    }
}
```

# Hello World!

下面是一个在屏幕上打印 Hello World! 的程序.

```no-highlight
++++++++++[>+++++++>++++++++++>+++>+<<<<-]
>++.>+.+++++++..+++.>++.<<+++++++++++++++.
>.+++.------.--------.>+.>.
```

虽然不太清楚上古的程序员们是如何写出这份代码的, 不过我也不在乎...毕竟能运行不是吗?

# IR 与优化

目前为止, 我们已经有了一个能正常跑的解释器, 但我对上面的代码并不满意, 如果你仔细观察, 可以发现 Brainfuck 源代码中存在着大量冗余. 下面将 Hello World 的代码以 Opcode 的形式打印出来:

```rs
[
    ADD, ADD, ADD, ADD, ADD, ADD, ADD, ADD, ADD, ADD, LB, SHR, ADD, ADD, ADD, ADD,
    ADD, ADD, ADD, SHR, ADD, ADD, ADD, ADD, ADD, ADD, ADD, ADD, ADD, ADD, SHR, ADD,
    ADD, ADD, SHR, ADD, SHL, SHL, SHL, SHL, SUB, RB, SHR, ADD, ADD, PUTCHAR, SHR,
    ADD, PUTCHAR, ADD, ADD, ADD, ADD, ADD, ADD, ADD, PUTCHAR, PUTCHAR, ADD, ADD, ADD,
    PUTCHAR, SHR, ADD, ADD, PUTCHAR, SHL, SHL, ADD, ADD, ADD, ADD, ADD, ADD, ADD,
    ADD, ADD, ADD, ADD, ADD, ADD, ADD, ADD, PUTCHAR, SHR, PUTCHAR, ADD, ADD, ADD,
    PUTCHAR, SUB, SUB, SUB, SUB, SUB, SUB, PUTCHAR, SUB, SUB, SUB, SUB, SUB, SUB,
    SUB, SUB, PUTCHAR, SHR, ADD, PUTCHAR, SHR, PUTCHAR
]
```

如果希望解释器执行的稍微快一点, 可以对相邻的相同操作符进行**折叠**操作, 比如以 ADD(10) 来表示连续存储的十个 ADD 操作符. 为此定义如下的中间表示.

> 中间语言(英语: Intermediate Language, IR), 在计算机科学中, 是指一种应用于抽象机器(abstract machine)的编程语言, 它设计的目的, 是用来帮助我们分析计算机程序. 这个术语源自于编译器, 在编译器将源代码编译为目的码的过程中, 会先将源代码转换为一个或多个的中间表述, 以方便编译器进行最佳化, 并产生出目的机器的机器语言.

```rs
#[derive(Debug, PartialEq)]
pub enum IR {
    SHR(u32),
    SHL(u32),
    ADD(u8),
    SUB(u8),
    PUTCHAR,
    GETCHAR,
    JIZ(u32),
    JNZ(u32),
}
```

好吧, 让我们直接给出 Hello World! 程序的 IR 表示:

```rs
[
    ADD(10), JIZ(12), SHR(1), ADD(7), SHR(1), ADD(10), SHR(1), ADD(3), SHR(1),
    ADD(1), SHL(4), SUB(1), JNZ(1), SHR(1), ADD(2), PUTCHAR, SHR(1), ADD(1), PUTCHAR,
    ADD(7), PUTCHAR, PUTCHAR, ADD(3), PUTCHAR, SHR(1), ADD(2), PUTCHAR, SHL(2),
    ADD(15), PUTCHAR, SHR(1), PUTCHAR, ADD(3), PUTCHAR, SUB(6), PUTCHAR, SUB(8),
    PUTCHAR, SHR(1), ADD(1), PUTCHAR, SHR(1), PUTCHAR
]
```

我们可以针对此中间语言编写解释器(相信你应该已经知道该怎么做了). 在测试中, 基于中间语言的解释器大概要比原始解释器快 5 倍左右.

下一篇文章将会介绍如何针对该中间语言编写 JIT 编译器. 稍微透露一下: **将中间语言翻译为语义等价的汇编代码**.

# 参考

- [1] 中间语言, 维基百科, [https://zh.wikipedia.org/zh-hans/中間語言](https://zh.wikipedia.org/zh-hans/中間語言)
