# 即时编译/Brainfuck 中间码优化

目前为止, 我们已经有了一个能正常跑的解释器, 但我对上面的代码并不满意, 如果你仔细观察, 可以发现 brainfuck 源代码中存在着大量冗余. 例如将 Hello World! 的代码以 opcode 的形式打印出来并进行观察:

```rs
[
    ADD,     ADD,     ADD,     ADD,     ADD,     ADD,     ADD,     ADD,
    ADD,     ADD,     LB,      SHR,     ADD,     ADD,     ADD,     ADD,
    ADD,     ADD,     ADD,     SHR,     ADD,     ADD,     ADD,     ADD,
    ADD,     ADD,     ADD,     ADD,     ADD,     ADD,     SHR,     ADD,
    ADD,     ADD,     SHR,     ADD,     SHL,     SHL,     SHL,     SHL,
    SUB,     RB,      SHR,     ADD,     ADD,     PUTCHAR, SHR,     ADD,
    PUTCHAR, ADD,     ADD,     ADD,     ADD,     ADD,     ADD,     ADD,
    PUTCHAR, PUTCHAR, ADD,     ADD,     ADD,     PUTCHAR, SHR,     ADD,
    ADD,     PUTCHAR, SHL,     SHL,     ADD,     ADD,     ADD,     ADD,
    ADD,     ADD,     ADD,     ADD,     ADD,     ADD,     ADD,     ADD,
    ADD,     ADD,     ADD,     PUTCHAR, SHR,     PUTCHAR, ADD,     ADD,
    ADD,     PUTCHAR, SUB,     SUB,     SUB,     SUB,     SUB,     SUB,
    PUTCHAR, SUB,     SUB,     SUB,     SUB,     SUB,     SUB,     SUB,
    SUB,     PUTCHAR, SHR,     ADD,     PUTCHAR, SHR,     PUTCHAR,
]
```

如果希望解释器执行的稍微快一点, 可以对相邻的相同操作符进行折叠操作, 我们已经知道一个 ADD 操作符执行的是加 1 操作, 那么如果相邻着十个连续的 ADD, 便可以 ADD(10) 来表示. 为此定义如下的中间语言表示.

> 中间语言, 在计算机科学中, 是指一种应用于抽象机器的编程语言, 它设计的目的, 是用来帮助我们分析计算机程序. 这个术语源自于编译器, 在编译器将源代码编译为目的码的过程中, 会先将源代码转换为一个或多个的中间表述, 以方便编译器进行最佳化, 并产生出目的机器的机器语言.

```rs
enum IR {
    SHR(u32),
    SHL(u32),
    ADD(u8),
    SUB(u8),
    PUTCHAR,
    GETCHAR,
    JIZ(u32), // Jump if eql zero, alias of "["
    JNZ(u32), // Jump if not zero, alias of "]"
}
```

您需要自己编写一个优化器, 以便将原始代码翻译为中间代码.

```rs
use super::opcode;

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

#[derive(Debug)]
pub struct Code {
    pub instrs: Vec<IR>,
}

impl Code {
    pub fn from(data: Vec<opcode::Opcode>) -> Result<Self, Box<dyn std::error::Error>> {
        let mut instrs: Vec<IR> = Vec::new();
        let mut jstack: Vec<u32> = Vec::new();
        for e in data {
            match e {
                opcode::Opcode::SHR => match instrs.last_mut() {
                    Some(IR::SHR(x)) => {
                        *x += 1;
                    }
                    _ => {
                        instrs.push(IR::SHR(1));
                    }
                },
                opcode::Opcode::SHL => match instrs.last_mut() {
                    Some(IR::SHL(x)) => {
                        *x += 1;
                    }
                    _ => {
                        instrs.push(IR::SHL(1));
                    }
                },
                opcode::Opcode::ADD => match instrs.last_mut() {
                    Some(IR::ADD(x)) => {
                        let (b, _) = x.overflowing_add(1);
                        *x = b;
                    }
                    _ => {
                        instrs.push(IR::ADD(1));
                    }
                },
                opcode::Opcode::SUB => match instrs.last_mut() {
                    Some(IR::SUB(x)) => {
                        let (b, _) = x.overflowing_add(1);
                        *x = b;
                    }
                    _ => {
                        instrs.push(IR::SUB(1));
                    }
                },
                opcode::Opcode::GETCHAR => {
                    instrs.push(IR::GETCHAR);
                }
                opcode::Opcode::PUTCHAR => {
                    instrs.push(IR::PUTCHAR);
                }
                opcode::Opcode::LB => {
                    instrs.push(IR::JIZ(0));
                    jstack.push((instrs.len() - 1) as u32);
                }
                opcode::Opcode::RB => {
                    let j = jstack.pop().ok_or("pop from empty list")?;
                    instrs.push(IR::JNZ(j));
                    let instrs_len = instrs.len();
                    match &mut instrs[j as usize] {
                        IR::JIZ(x) => {
                            *x = (instrs_len - 1) as u32;
                        }
                        _ => {
                            unimplemented!();
                        }
                    }
                }
            }
        }
        Ok(Code { instrs })
    }
}
```

这很简单, 因此我假设您已经写好了. 经过中间语言优化后的 Hello World! 代码如下所示, 它大概减少了 60% 左右的大小.

```rs
[
    ADD(10),  JIZ(12),  SHR(1),  ADD(7),  SHR(1),  ADD(10),  SHR(1),  ADD(3),
    SHR(1),   ADD(1),   SHL(4),  SUB(1),  JNZ(1),  SHR(1),   ADD(2),  PUTCHAR,
    SHR(1),   ADD(1),   PUTCHAR, ADD(7),  PUTCHAR, PUTCHAR,  ADD(3),  PUTCHAR,
    SHR(1),   ADD(2),   PUTCHAR, SHL(2),  ADD(15), PUTCHAR,  SHR(1),  PUTCHAR,
    ADD(3),   PUTCHAR,  SUB(6),  PUTCHAR, SUB(8),  PUTCHAR,  SHR(1),  ADD(1),
    PUTCHAR,  SHR(1),   PUTCHAR
]
```

之后我们便可以针对此中间语言编写解释器(再一次的, 相信您应该已经知道该怎么做了). 我仍然会在下方给出一个简单的实现.

```rs
use std::io::prelude::*;

use brainfuck::ir;
use brainfuck::opcode;

struct Interpreter {
    stack: Vec<u8>,
}

impl std::default::Default for Interpreter {
    fn default() -> Self {
        Self { stack: vec![0; 1] }
    }
}

impl Interpreter {
    fn run(&mut self, data: Vec<u8>) -> Result<(), Box<dyn std::error::Error>> {
        let opcode_code = opcode::Code::from(data)?;
        let code = ir::Code::from(opcode_code.instrs)?;
        let code_len = code.instrs.len();
        let mut pc: usize = 0;
        let mut ps: usize = 0;
        loop {
            if pc >= code_len {
                break;
            }
            match code.instrs[pc] {
                ir::IR::SHL(x) => ps = ps.saturating_sub(x as usize),
                ir::IR::SHR(x) => {
                    ps += x as usize;
                    if ps >= self.stack.len() {
                        let expand = ps - self.stack.len() + 1;
                        for _ in 0..expand {
                            self.stack.push(0);
                        }
                    }
                }
                ir::IR::ADD(x) => {
                    self.stack[ps] = self.stack[ps].overflowing_add(x).0;
                }
                ir::IR::SUB(x) => {
                    self.stack[ps] = self.stack[ps].overflowing_sub(x).0;
                }
                ir::IR::PUTCHAR => {
                    std::io::stdout().write_all(&[self.stack[ps]])?;
                }
                ir::IR::GETCHAR => {
                    let mut buf: Vec<u8> = vec![0; 1];
                    std::io::stdin().read_exact(&mut buf)?;
                    self.stack[ps] = buf[0];
                }
                ir::IR::JIZ(x) => {
                    if self.stack[ps] == 0x00 {
                        pc = x as usize;
                    }
                }
                ir::IR::JNZ(x) => {
                    if self.stack[ps] != 0x00 {
                        pc = x as usize;
                    }
                }
            }
            pc += 1;
        }
        Ok(())
    }
}

fn main() -> Result<(), Box<dyn std::error::Error>> {
    let args: Vec<String> = std::env::args().collect();
    assert!(args.len() >= 2);
    let mut f = std::fs::File::open(&args[1])?;
    let mut c: Vec<u8> = Vec::new();
    f.read_to_end(&mut c)?;
    let mut i = Interpreter::default();
    i.run(c)
}
```

在测试中, 基于中间语言的解释器大概要比原始解释器快 5 倍左右. 真棒! 但请记住本文设计的 IR 并非最优化的, 其仍然有优化空间, 例如, 您可以进一步融合连续的 ADD 和 SUB 以单个 ADD 或 SUB 替代.

下一篇文章将会介绍如何针对该中间语言编写 jit 编译器. 其核心思想是: 将中间语言翻译为语义等价的汇编代码.

## 参考

- [1] [维基百科. 中间语言.](https://zh.wikipedia.org/zh-hans/中間語言)
