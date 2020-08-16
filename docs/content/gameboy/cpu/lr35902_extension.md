# LR35902 扩展指令集

标准的算术逻辑指令通常将结果写回到寄存器 A. 它们所完成任务可以用如下语言描述: 从寄存器 A 拿出数据, 进行一些算术逻辑运算后再重新放回寄存器 A. 想象一下下面这个需求: 对寄存器 B 内存储的数据右移一位. 如下的操作步骤是一个可行的方案:

1. 将寄存器 A 的值保存到内存中.
2. 将寄存器 B 的值保存到寄存器 A.
3. 将寄存器 A 右移一位.
4. 将寄存器 A 的值保存到寄存器 B.
5. 将第一步保存的值写回寄存器 A.

这样操作显得有点麻烦, 如果可以直接对寄存器 B 的数据进行位移运算就好了! 但是 LR35902 是 8 位 CPU, 因此如果使用一个 Byte 来表示一个操作码的话, 其最多只允许表示 2^8 = 256 个指令, 如果读者曾注意上一节中标准指令集的操作码个数的话, 会发现单单标准指令集就已经有接近 256 个了. 现在已经没有足够的空位来为不同的寄存器都实现算术逻辑指令, 那么, 是否可以将指令扩展到两个 Byte？

# 什么是扩展指令集

扩展指令集是指为 CPU 增加新的指令集, 这些扩展指令可以提高 CPU 处理数学运算的能力. 在现代 CPU 中, 常见的有 MMX, SSE 等扩展指令集. 一个早期的比较著名的扩展指令集出现在上世纪 70 年代的街机游戏太空侵略者(其游戏画面如下图所示), 该街机使用 Intel 8080 CPU, 但 Intel 8080 CPU 的标准指令集不带数字的移位指令, 因此该街机选择通过外接硬件电路, 通过 CPU I/O 串口来实现移位操作.

![img](/img/gameboy/cpu/lr35902_extension/space_invaders.png)

LR35902 的扩展指令大小是两个 Byte, 其中第一个 Byte 固定是 0xcb. 因此在实现过程中, 如果发现取得的指令是 0xcb, 则需要继续取一个 Byte. 代码实现如下:

```rs
fn ex(&mut self) -> u32 {
    let opcode = self.imm();
    match opcode {
        0xcb => {
            cbcode = self.mem.borrow().get(self.reg.pc);
            self.reg.pc += 1;
            match cbcode {
                ...
            }
        }
        ...
    }
}
```

下面给出了扩展指令的摘要以及仿真实现. 如果该指令影响了标志位, 则会在指令描述中指明.

# 循环和移位操作

**RLC r8**

1) 描述

目标寄存器按位左移. 最高位移动至溢出标志位.

2) 标志位变化

- Z - 计算结果为零, 则置位
- N - 置零
- H - 置零
- C - 原始值的最高位.

3) 指令

Instruction | Parameters | Opcode | Cycles
----------- | ---------- | ------ | ------
RLC         | B          | 00     | 8
RLC         | C          | 01     | 8
RLC         | D          | 02     | 8
RLC         | E          | 03     | 8
RLC         | H          | 04     | 8
RLC         | L          | 05     | 8
RLC         | (HL)       | 06     | 16
RLC         | A          | 07     | 8

4) 代码实现

```rs
fn ex(&mut self) -> u32 {
    let opcode = self.imm();
    match opcode {
        0xcb => {
            cbcode = self.mem.borrow().get(self.reg.pc);
            self.reg.pc += 1;
            match cbcode {
                0x00 => self.reg.b = self.alu_rlc(self.reg.b),
                0x01 => self.reg.c = self.alu_rlc(self.reg.c),
                0x02 => self.reg.d = self.alu_rlc(self.reg.d),
                0x03 => self.reg.e = self.alu_rlc(self.reg.e),
                0x04 => self.reg.h = self.alu_rlc(self.reg.h),
                0x05 => self.reg.l = self.alu_rlc(self.reg.l),
                0x06 => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    let h = self.alu_rlc(v);
                    self.mem.borrow_mut().set(a, h);
                }
                0x07 => self.reg.a = self.alu_rlc(self.reg.a),
                ...
            }
        }
        ...
    }
}
```

**RRC r8**

1) 描述

目标寄存器按位右移. 最低位移动至溢出标志位.

2) 标志位变化

- Z - 计算结果为零, 则置位
- N - 置零
- H - 置零
- C - 原始值的最低位

3) 指令

 Instruction | Parameters | Opcode | Cycles
 ----------- | ---------- | ------ | ------
 RRC         | B          | 08     | 8
 RRC         | C          | 09     | 8
 RRC         | D          | 0a     | 8
 RRC         | E          | 0b     | 8
 RRC         | H          | 0c     | 8
 RRC         | L          | 0d     | 8
 RRC         | (HL)       | 0e     | 16
 RRC         | A          | 0f     | 8

4) 代码实现

```rs
fn ex(&mut self) -> u32 {
    let opcode = self.imm();
    match opcode {
        0xcb => {
            cbcode = self.mem.borrow().get(self.reg.pc);
            self.reg.pc += 1;
            match cbcode {
                0x08 => self.reg.b = self.alu_rrc(self.reg.b),
                0x09 => self.reg.c = self.alu_rrc(self.reg.c),
                0x0a => self.reg.d = self.alu_rrc(self.reg.d),
                0x0b => self.reg.e = self.alu_rrc(self.reg.e),
                0x0c => self.reg.h = self.alu_rrc(self.reg.h),
                0x0d => self.reg.l = self.alu_rrc(self.reg.l),
                0x0e => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    let h = self.alu_rrc(v);
                    self.mem.borrow_mut().set(a, h);
                }
                0x0f => self.reg.a = self.alu_rrc(self.reg.a),
                ...
            }
        }
        ...
    }
}
```

**RL r8**

1) 描述

目标寄存器按位左移运算. 溢出标志位补充最低位, 同时最高位移动至溢出标志位.

2) 标志位变化

- Z - 计算结果为零, 则置位
- N - 置零
- H - 置零
- C - 原始值的最高位.

3) 指令

Instruction | Parameters | Opcode | Cycles
----------- | ---------- | ------ | ------
RL          | B          | 10     | 8
RL          | C          | 11     | 8
RL          | D          | 12     | 8
RL          | E          | 13     | 8
RL          | H          | 14     | 8
RL          | L          | 15     | 8
RL          | (HL)       | 16     | 16
RL          | A          | 17     | 8

4) 代码实现

```rs
fn ex(&mut self) -> u32 {
    let opcode = self.imm();
    match opcode {
        0xcb => {
            cbcode = self.mem.borrow().get(self.reg.pc);
            self.reg.pc += 1;
            match cbcode {
                0x10 => self.reg.b = self.alu_rl(self.reg.b),
                0x11 => self.reg.c = self.alu_rl(self.reg.c),
                0x12 => self.reg.d = self.alu_rl(self.reg.d),
                0x13 => self.reg.e = self.alu_rl(self.reg.e),
                0x14 => self.reg.h = self.alu_rl(self.reg.h),
                0x15 => self.reg.l = self.alu_rl(self.reg.l),
                0x16 => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    let h = self.alu_rl(v);
                    self.mem.borrow_mut().set(a, h);
                }
                0x17 => self.reg.a = self.alu_rl(self.reg.a),
                ...
            }
        }
        ...
    }
}
```

**RR r8**

1) 描述

目标寄存器按位右移运算. 溢出标志位移动至最高位, 同时最低位移动至溢出标志位.

2) 标志位变化

- Z - 计算结果为零, 则置位
- N - 置零
- H - 置零
- C - 原始数据最低位

3) 指令

Instruction | Parameters | Opcode | Cycles
----------- | ---------- | ------ | ------
RR          | B          | 18     | 8
RR          | C          | 19     | 8
RR          | D          | 1a     | 8
RR          | E          | 1b     | 8
RR          | H          | 1c     | 8
RR          | L          | 1d     | 8
RR          | (HL)       | 1e     | 16
RR          | A          | 1f     | 8

4) 代码实现

```rs
fn ex(&mut self) -> u32 {
    let opcode = self.imm();
    match opcode {
        0xcb => {
            cbcode = self.mem.borrow().get(self.reg.pc);
            self.reg.pc += 1;
            match cbcode {
                0x18 => self.reg.b = self.alu_rr(self.reg.b),
                0x19 => self.reg.c = self.alu_rr(self.reg.c),
                0x1a => self.reg.d = self.alu_rr(self.reg.d),
                0x1b => self.reg.e = self.alu_rr(self.reg.e),
                0x1c => self.reg.h = self.alu_rr(self.reg.h),
                0x1d => self.reg.l = self.alu_rr(self.reg.l),
                0x1e => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    let h = self.alu_rr(v);
                    self.mem.borrow_mut().set(a, h);
                }
                0x1f => self.reg.a = self.alu_rr(self.reg.a),
                ...
            }
        }
        ...
    }
}
```

**SLA r8**

1) 描述

目标寄存器按位左移运算. 最高位移动至溢出标志位, 最低位设置为零.

2) 标志位变化

- Z - 计算结果为零, 则置位
- N - 置零
- H - 置零
- C - 原始数据最高位

3) 指令

Instruction | Parameters | Opcode | Cycles
----------- | ---------- | ------ | ------
SLA         | B          | 20     | 8
SLA         | C          | 21     | 8
SLA         | D          | 22     | 8
SLA         | E          | 23     | 8
SLA         | H          | 24     | 8
SLA         | L          | 25     | 8
SLA         | (HL)       | 26     | 16
SLA         | A          | 27     | 8

4) 代码实现

```rs
impl Cpu {
    // Shift n left into Carry. LSB of n set to 0.
    // n = A,B,C,D,E,H,L,(HL)
    //
    // Flags affected:
    // Z - Set if result is zero.
    // N - Reset.
    // H - Reset.
    // C - Contains old bit 7 data
    fn alu_sla(&mut self, a: u8) -> u8 {
        let c = (a & 0x80) >> 7 == 0x01;
        let r = a << 1;
        self.reg.set_flag(C, c);
        self.reg.set_flag(H, false);
        self.reg.set_flag(N, false);
        self.reg.set_flag(Z, r == 0x00);
        r
    }
}

fn ex(&mut self) -> u32 {
    let opcode = self.imm();
    match opcode {
        0xcb => {
            cbcode = self.mem.borrow().get(self.reg.pc);
            self.reg.pc += 1;
            match cbcode {
                0x20 => self.reg.b = self.alu_sla(self.reg.b),
                0x21 => self.reg.c = self.alu_sla(self.reg.c),
                0x22 => self.reg.d = self.alu_sla(self.reg.d),
                0x23 => self.reg.e = self.alu_sla(self.reg.e),
                0x24 => self.reg.h = self.alu_sla(self.reg.h),
                0x25 => self.reg.l = self.alu_sla(self.reg.l),
                0x26 => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    let h = self.alu_sla(v);
                    self.mem.borrow_mut().set(a, h);
                }
                0x27 => self.reg.a = self.alu_sla(self.reg.a),
                ...
            }
        }
        ...
    }
}
```

**SRA r8**

1) 描述

目标寄存器按位右移运算. 最低位保存入溢出标志位, 最高位保持不变.

2) 标志位变化

- Z - 计算结果为零, 则置位
- N - 置零
- H - 置零
- C - 原始数据最低位

3) 指令

Instruction | Parameters | Opcode | Cycles
----------- | ---------- | ------ | ------
SRA         | B          | 28     | 8
SRA         | C          | 29     | 8
SRA         | D          | 2a     | 8
SRA         | E          | 2b     | 8
SRA         | H          | 2c     | 8
SRA         | L          | 2d     | 8
SRA         | (HL)       | 2e     | 16
SRA         | A          | 2f     | 8

4) 代码实现

```rs
impl Cpu {
    // Shift n right into Carry. MSB doesn't change.
    // n = A,B,C,D,E,H,L,(HL)
    //
    // Flags affected:
    // Z - Set if result is zero.
    // N - Reset.
    // H - Reset.
    // C - Contains old bit 0 data.
    fn alu_sra(&mut self, a: u8) -> u8 {
        let c = a & 0x01 == 0x01;
        let r = (a >> 1) | (a & 0x80);
        self.reg.set_flag(C, c);
        self.reg.set_flag(H, false);
        self.reg.set_flag(N, false);
        self.reg.set_flag(Z, r == 0x00);
        r
    }
}

fn ex(&mut self) -> u32 {
    let opcode = self.imm();
    match opcode {
        0xcb => {
            cbcode = self.mem.borrow().get(self.reg.pc);
            self.reg.pc += 1;
            match cbcode {
                0x28 => self.reg.b = self.alu_sra(self.reg.b),
                0x29 => self.reg.c = self.alu_sra(self.reg.c),
                0x2a => self.reg.d = self.alu_sra(self.reg.d),
                0x2b => self.reg.e = self.alu_sra(self.reg.e),
                0x2c => self.reg.h = self.alu_sra(self.reg.h),
                0x2d => self.reg.l = self.alu_sra(self.reg.l),
                0x2e => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    let h = self.alu_sra(v);
                    self.mem.borrow_mut().set(a, h);
                }
                0x2f => self.reg.a = self.alu_sra(self.reg.a),
                ...
            }
        }
        ...
    }
}
```

**SRL r8**

1) 描述

目标寄存器按位右移运算. 最低位移动至溢出标志位, 最高位置零.

2) 标志位变化

- Z - 计算结果为零, 则置位
- N - 置零
- H - 置零
- C - 原始数据最低位

3) 指令

Instruction | Parameters | Opcode | Cycles
----------- | ---------- | ------ | ------
SRL         | B          | 38     | 8
SRL         | C          | 39     | 8
SRL         | D          | 3a     | 8
SRL         | E          | 3b     | 8
SRL         | H          | 3c     | 8
SRL         | L          | 3d     | 8
SRL         | (HL)       | 3e     | 16
SRL         | A          | 3f     | 8

4) 代码实现

```rs
impl Cpu {
    // Shift n right into Carry. MSB set to 0.
    // n = A,B,C,D,E,H,L,(HL)
    //
    // Flags affected:
    // Z - Set if result is zero.
    // N - Reset.
    // H - Reset.
    // C - Contains old bit 0 data.
    fn alu_srl(&mut self, a: u8) -> u8 {
        let c = a & 0x01 == 0x01;
        let r = a >> 1;
        self.reg.set_flag(C, c);
        self.reg.set_flag(H, false);
        self.reg.set_flag(N, false);
        self.reg.set_flag(Z, r == 0x00);
        r
    }
}

fn ex(&mut self) -> u32 {
    let opcode = self.imm();
    match opcode {
        0xcb => {
            cbcode = self.mem.borrow().get(self.reg.pc);
            self.reg.pc += 1;
            match cbcode {
                0x38 => self.reg.b = self.alu_srl(self.reg.b),
                0x39 => self.reg.c = self.alu_srl(self.reg.c),
                0x3a => self.reg.d = self.alu_srl(self.reg.d),
                0x3b => self.reg.e = self.alu_srl(self.reg.e),
                0x3c => self.reg.h = self.alu_srl(self.reg.h),
                0x3d => self.reg.l = self.alu_srl(self.reg.l),
                0x3e => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    let h = self.alu_srl(v);
                    self.mem.borrow_mut().set(a, h);
                }
                0x3f => self.reg.a = self.alu_srl(self.reg.a),
                ...
            }
        }
        ...
    }
}
```

# 交换

**SWAP r8**

1) 描述

交换目标寄存器高 4 位与低 4 位的比特.

2) 标志位变化

- Z - 计算结果为零, 则置位
- N - 置零
- H - 置零
- C - 置零

3) 指令

Instruction | Parameters | Opcode | Cycles
----------- | ---------- | ------ | ------
SWAP        | B          | 30     | 8
SWAP        | C          | 31     | 8
SWAP        | D          | 32     | 8
SWAP        | E          | 33     | 8
SWAP        | H          | 34     | 8
SWAP        | L          | 35     | 8
SWAP        | (HL)       | 36     | 16
SWAP        | A          | 37     | 8

4) 代码实现

```rs
impl Cpu {
    // Swap upper & lower nibles of n.
    // n = A,B,C,D,E,H,L,(HL)
    //
    // Flags affected:
    // Z - Set if result is zero.
    // N - Reset.
    // H - Reset.
    // C - Reset.
    fn alu_swap(&mut self, a: u8) -> u8 {
        self.reg.set_flag(C, false);
        self.reg.set_flag(H, false);
        self.reg.set_flag(N, false);
        self.reg.set_flag(Z, a == 0x00);
        (a >> 4) | (a << 4)
    }
}

fn ex(&mut self) -> u32 {
    let opcode = self.imm();
    match opcode {
        0xcb => {
            cbcode = self.mem.borrow().get(self.reg.pc);
            self.reg.pc += 1;
            match cbcode {
                0x30 => self.reg.b = self.alu_swap(self.reg.b),
                0x31 => self.reg.c = self.alu_swap(self.reg.c),
                0x32 => self.reg.d = self.alu_swap(self.reg.d),
                0x33 => self.reg.e = self.alu_swap(self.reg.e),
                0x34 => self.reg.h = self.alu_swap(self.reg.h),
                0x35 => self.reg.l = self.alu_swap(self.reg.l),
                0x36 => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    let h = self.alu_swap(v);
                    self.mem.borrow_mut().set(a, h);
                }
                0x37 => self.reg.a = self.alu_swap(self.reg.a),
                ...
            }
        }
        ...
    }
}
```

# 位数据获取与设置

**BIT**

1) 描述

取得目标寄存器中指定的 bit 位.

2) 标志位变化

- Z - 如果指定寄存器的指定 bit 位为零, 则置零.
- N - 置零
- H - 置位
- C - 保持不变

3) 指令

Instruction | Parameters | Opcode | Cycles
----------- | ---------- | ------ | ------
BIT         | B, 0       | 40     | 8
BIT         | C, 0       | 41     | 8
BIT         | D, 0       | 42     | 8
BIT         | E, 0       | 43     | 8
BIT         | H, 0       | 44     | 8
BIT         | L, 0       | 45     | 8
BIT         | (HL), 0    | 46     | 16
BIT         | A, 0       | 47     | 8
BIT         | B, 1       | 48     | 8
BIT         | C, 1       | 49     | 8
BIT         | D, 1       | 4a     | 8
BIT         | E, 1       | 4b     | 8
BIT         | H, 1       | 4c     | 8
BIT         | L, 1       | 4d     | 8
BIT         | (HL), 1    | 4e     | 16
BIT         | A, 1       | 4f     | 8
BIT         | B, 2       | 50     | 8
BIT         | C, 2       | 51     | 8
BIT         | D, 2       | 52     | 8
BIT         | E, 2       | 53     | 8
BIT         | H, 2       | 54     | 8
BIT         | L, 2       | 55     | 8
BIT         | (HL), 2    | 56     | 16
BIT         | A, 2       | 57     | 8
BIT         | B, 3       | 58     | 8
BIT         | C, 3       | 59     | 8
BIT         | D, 3       | 5a     | 8
BIT         | E, 3       | 5b     | 8
BIT         | H, 3       | 5c     | 8
BIT         | L, 3       | 5d     | 8
BIT         | (HL), 3    | 5e     | 16
BIT         | A, 3       | 5f     | 8
BIT         | B, 4       | 60     | 8
BIT         | C, 4       | 61     | 8
BIT         | D, 4       | 62     | 8
BIT         | E, 4       | 63     | 8
BIT         | H, 4       | 64     | 8
BIT         | L, 4       | 65     | 8
BIT         | (HL), 4    | 66     | 16
BIT         | A, 4       | 67     | 8
BIT         | B, 5       | 68     | 8
BIT         | C, 5       | 69     | 8
BIT         | D, 5       | 6a     | 8
BIT         | E, 5       | 6b     | 8
BIT         | H, 5       | 6c     | 8
BIT         | L, 5       | 6d     | 8
BIT         | (HL), 5    | 6e     | 16
BIT         | A, 5       | 6f     | 8
BIT         | B, 6       | 70     | 8
BIT         | C, 6       | 71     | 8
BIT         | D, 6       | 72     | 8
BIT         | E, 6       | 73     | 8
BIT         | H, 6       | 74     | 8
BIT         | L, 6       | 75     | 8
BIT         | (HL), 6    | 76     | 16
BIT         | A, 6       | 77     | 8
BIT         | B, 7       | 78     | 8
BIT         | C, 7       | 79     | 8
BIT         | D, 7       | 7a     | 8
BIT         | E, 7       | 7b     | 8
BIT         | H, 7       | 7c     | 8
BIT         | L, 7       | 7d     | 8
BIT         | (HL), 7    | 7e     | 16
BIT         | A, 7       | 7f     | 8

4) 代码实现

```rs
impl Cpu {
    // Test bit b in register r.
    // b = 0 - 7, r = A,B,C,D,E,H,L,(HL)
    //
    // Flags affected:
    // Z - Set if bit b of register r is 0.
    // N - Reset.
    // H - Set.
    // C - Not affected
    fn alu_bit(&mut self, a: u8, b: u8) {
        let r = a & (1 << b) == 0x00;
        self.reg.set_flag(H, true);
        self.reg.set_flag(N, false);
        self.reg.set_flag(Z, r);
    }
}

fn ex(&mut self) -> u32 {
    let opcode = self.imm();
    match opcode {
        0xcb => {
            cbcode = self.mem.borrow().get(self.reg.pc);
            self.reg.pc += 1;
            match cbcode {
                0x40 => self.alu_bit(self.reg.b, 0),
                0x41 => self.alu_bit(self.reg.c, 0),
                0x42 => self.alu_bit(self.reg.d, 0),
                0x43 => self.alu_bit(self.reg.e, 0),
                0x44 => self.alu_bit(self.reg.h, 0),
                0x45 => self.alu_bit(self.reg.l, 0),
                0x46 => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    self.alu_bit(v, 0);
                }
                0x47 => self.alu_bit(self.reg.a, 0),
                0x48 => self.alu_bit(self.reg.b, 1),
                0x49 => self.alu_bit(self.reg.c, 1),
                0x4a => self.alu_bit(self.reg.d, 1),
                0x4b => self.alu_bit(self.reg.e, 1),
                0x4c => self.alu_bit(self.reg.h, 1),
                0x4d => self.alu_bit(self.reg.l, 1),
                0x4e => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    self.alu_bit(v, 1);
                }
                0x4f => self.alu_bit(self.reg.a, 1),
                0x50 => self.alu_bit(self.reg.b, 2),
                0x51 => self.alu_bit(self.reg.c, 2),
                0x52 => self.alu_bit(self.reg.d, 2),
                0x53 => self.alu_bit(self.reg.e, 2),
                0x54 => self.alu_bit(self.reg.h, 2),
                0x55 => self.alu_bit(self.reg.l, 2),
                0x56 => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    self.alu_bit(v, 2);
                }
                0x57 => self.alu_bit(self.reg.a, 2),
                0x58 => self.alu_bit(self.reg.b, 3),
                0x59 => self.alu_bit(self.reg.c, 3),
                0x5a => self.alu_bit(self.reg.d, 3),
                0x5b => self.alu_bit(self.reg.e, 3),
                0x5c => self.alu_bit(self.reg.h, 3),
                0x5d => self.alu_bit(self.reg.l, 3),
                0x5e => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    self.alu_bit(v, 3);
                }
                0x5f => self.alu_bit(self.reg.a, 3),
                0x60 => self.alu_bit(self.reg.b, 4),
                0x61 => self.alu_bit(self.reg.c, 4),
                0x62 => self.alu_bit(self.reg.d, 4),
                0x63 => self.alu_bit(self.reg.e, 4),
                0x64 => self.alu_bit(self.reg.h, 4),
                0x65 => self.alu_bit(self.reg.l, 4),
                0x66 => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    self.alu_bit(v, 4);
                }
                0x67 => self.alu_bit(self.reg.a, 4),
                0x68 => self.alu_bit(self.reg.b, 5),
                0x69 => self.alu_bit(self.reg.c, 5),
                0x6a => self.alu_bit(self.reg.d, 5),
                0x6b => self.alu_bit(self.reg.e, 5),
                0x6c => self.alu_bit(self.reg.h, 5),
                0x6d => self.alu_bit(self.reg.l, 5),
                0x6e => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    self.alu_bit(v, 5);
                }
                0x6f => self.alu_bit(self.reg.a, 5),
                0x70 => self.alu_bit(self.reg.b, 6),
                0x71 => self.alu_bit(self.reg.c, 6),
                0x72 => self.alu_bit(self.reg.d, 6),
                0x73 => self.alu_bit(self.reg.e, 6),
                0x74 => self.alu_bit(self.reg.h, 6),
                0x75 => self.alu_bit(self.reg.l, 6),
                0x76 => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    self.alu_bit(v, 6);
                }
                0x77 => self.alu_bit(self.reg.a, 6),
                0x78 => self.alu_bit(self.reg.b, 7),
                0x79 => self.alu_bit(self.reg.c, 7),
                0x7a => self.alu_bit(self.reg.d, 7),
                0x7b => self.alu_bit(self.reg.e, 7),
                0x7c => self.alu_bit(self.reg.h, 7),
                0x7d => self.alu_bit(self.reg.l, 7),
                0x7e => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    self.alu_bit(v, 7);
                }
                0x7f => self.alu_bit(self.reg.a, 7),
                ...
            }
        }
        ...
    }
}
```

**RES**

1) 描述

置零目标寄存器中指定的 bit 位.

2) 标志位变化

无

3) 指令

Instruction | Parameters | Opcode | Cycles
----------- | ---------- | ------ | ------
RES         | B, 0       | 80     | 8
RES         | C, 0       | 81     | 8
RES         | D, 0       | 82     | 8
RES         | E, 0       | 83     | 8
RES         | H, 0       | 84     | 8
RES         | L, 0       | 85     | 8
RES         | (HL), 0    | 86     | 16
RES         | A, 0       | 87     | 8
RES         | B, 1       | 88     | 8
RES         | C, 1       | 89     | 8
RES         | D, 1       | 8a     | 8
RES         | E, 1       | 8b     | 8
RES         | H, 1       | 8c     | 8
RES         | L, 1       | 8d     | 8
RES         | (HL), 1    | 8e     | 16
RES         | A, 1       | 8f     | 8
RES         | B, 2       | 90     | 8
RES         | C, 2       | 91     | 8
RES         | D, 2       | 92     | 8
RES         | E, 2       | 93     | 8
RES         | H, 2       | 94     | 8
RES         | L, 2       | 95     | 8
RES         | (HL), 2    | 96     | 16
RES         | A, 2       | 97     | 8
RES         | B, 3       | 98     | 8
RES         | C, 3       | 99     | 8
RES         | D, 3       | 9a     | 8
RES         | E, 3       | 9b     | 8
RES         | H, 3       | 9c     | 8
RES         | L, 3       | 9d     | 8
RES         | (HL), 3    | 9e     | 16
RES         | A, 3       | 9f     | 8
RES         | B, 4       | a0     | 8
RES         | C, 4       | a1     | 8
RES         | D, 4       | a2     | 8
RES         | E, 4       | a3     | 8
RES         | H, 4       | a4     | 8
RES         | L, 4       | a5     | 8
RES         | (HL), 4    | a6     | 16
RES         | A, 4       | a7     | 8
RES         | B, 5       | a8     | 8
RES         | C, 5       | a9     | 8
RES         | D, 5       | aa     | 8
RES         | E, 5       | ab     | 8
RES         | H, 5       | ac     | 8
RES         | L, 5       | ad     | 8
RES         | (HL), 5    | ae     | 16
RES         | A, 5       | af     | 8
RES         | B, 6       | b0     | 8
RES         | C, 6       | b1     | 8
RES         | D, 6       | b2     | 8
RES         | E, 6       | b3     | 8
RES         | H, 6       | b4     | 8
RES         | L, 6       | b5     | 8
RES         | (HL), 6    | b6     | 16
RES         | A, 6       | b7     | 8
RES         | B, 7       | b8     | 8
RES         | C, 7       | b9     | 8
RES         | D, 7       | ba     | 8
RES         | E, 7       | bb     | 8
RES         | H, 7       | bc     | 8
RES         | L, 7       | bd     | 8
RES         | (HL), 7    | be     | 16
RES         | A, 7       | bf     | 8

4) 代码实现

```rs
impl Cpu {
    // Reset bit b in register r.
    // b = 0 - 7, r = A,B,C,D,E,H,L,(HL)
    //
    // Flags affected:  None.
    fn alu_res(&mut self, a: u8, b: u8) -> u8 {
        a & !(1 << b)
    }
}

fn ex(&mut self) -> u32 {
    let opcode = self.imm();
    match opcode {
        0xcb => {
            cbcode = self.mem.borrow().get(self.reg.pc);
            self.reg.pc += 1;
            match cbcode {
                0x80 => self.reg.b = self.alu_res(self.reg.b, 0),
                0x81 => self.reg.c = self.alu_res(self.reg.c, 0),
                0x82 => self.reg.d = self.alu_res(self.reg.d, 0),
                0x83 => self.reg.e = self.alu_res(self.reg.e, 0),
                0x84 => self.reg.h = self.alu_res(self.reg.h, 0),
                0x85 => self.reg.l = self.alu_res(self.reg.l, 0),
                0x86 => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    let h = self.alu_res(v, 0);
                    self.mem.borrow_mut().set(a, h);
                }
                0x87 => self.reg.a = self.alu_res(self.reg.a, 0),
                0x88 => self.reg.b = self.alu_res(self.reg.b, 1),
                0x89 => self.reg.c = self.alu_res(self.reg.c, 1),
                0x8a => self.reg.d = self.alu_res(self.reg.d, 1),
                0x8b => self.reg.e = self.alu_res(self.reg.e, 1),
                0x8c => self.reg.h = self.alu_res(self.reg.h, 1),
                0x8d => self.reg.l = self.alu_res(self.reg.l, 1),
                0x8e => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    let h = self.alu_res(v, 1);
                    self.mem.borrow_mut().set(a, h);
                }
                0x8f => self.reg.a = self.alu_res(self.reg.a, 1),
                0x90 => self.reg.b = self.alu_res(self.reg.b, 2),
                0x91 => self.reg.c = self.alu_res(self.reg.c, 2),
                0x92 => self.reg.d = self.alu_res(self.reg.d, 2),
                0x93 => self.reg.e = self.alu_res(self.reg.e, 2),
                0x94 => self.reg.h = self.alu_res(self.reg.h, 2),
                0x95 => self.reg.l = self.alu_res(self.reg.l, 2),
                0x96 => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    let h = self.alu_res(v, 2);
                    self.mem.borrow_mut().set(a, h);
                }
                0x97 => self.reg.a = self.alu_res(self.reg.a, 2),
                0x98 => self.reg.b = self.alu_res(self.reg.b, 3),
                0x99 => self.reg.c = self.alu_res(self.reg.c, 3),
                0x9a => self.reg.d = self.alu_res(self.reg.d, 3),
                0x9b => self.reg.e = self.alu_res(self.reg.e, 3),
                0x9c => self.reg.h = self.alu_res(self.reg.h, 3),
                0x9d => self.reg.l = self.alu_res(self.reg.l, 3),
                0x9e => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    let h = self.alu_res(v, 3);
                    self.mem.borrow_mut().set(a, h);
                }
                0x9f => self.reg.a = self.alu_res(self.reg.a, 3),
                0xa0 => self.reg.b = self.alu_res(self.reg.b, 4),
                0xa1 => self.reg.c = self.alu_res(self.reg.c, 4),
                0xa2 => self.reg.d = self.alu_res(self.reg.d, 4),
                0xa3 => self.reg.e = self.alu_res(self.reg.e, 4),
                0xa4 => self.reg.h = self.alu_res(self.reg.h, 4),
                0xa5 => self.reg.l = self.alu_res(self.reg.l, 4),
                0xa6 => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    let h = self.alu_res(v, 4);
                    self.mem.borrow_mut().set(a, h);
                }
                0xa7 => self.reg.a = self.alu_res(self.reg.a, 4),
                0xa8 => self.reg.b = self.alu_res(self.reg.b, 5),
                0xa9 => self.reg.c = self.alu_res(self.reg.c, 5),
                0xaa => self.reg.d = self.alu_res(self.reg.d, 5),
                0xab => self.reg.e = self.alu_res(self.reg.e, 5),
                0xac => self.reg.h = self.alu_res(self.reg.h, 5),
                0xad => self.reg.l = self.alu_res(self.reg.l, 5),
                0xae => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    let h = self.alu_res(v, 5);
                    self.mem.borrow_mut().set(a, h);
                }
                0xaf => self.reg.a = self.alu_res(self.reg.a, 5),
                0xb0 => self.reg.b = self.alu_res(self.reg.b, 6),
                0xb1 => self.reg.c = self.alu_res(self.reg.c, 6),
                0xb2 => self.reg.d = self.alu_res(self.reg.d, 6),
                0xb3 => self.reg.e = self.alu_res(self.reg.e, 6),
                0xb4 => self.reg.h = self.alu_res(self.reg.h, 6),
                0xb5 => self.reg.l = self.alu_res(self.reg.l, 6),
                0xb6 => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    let h = self.alu_res(v, 6);
                    self.mem.borrow_mut().set(a, h);
                }
                0xb7 => self.reg.a = self.alu_res(self.reg.a, 6),
                0xb8 => self.reg.b = self.alu_res(self.reg.b, 7),
                0xb9 => self.reg.c = self.alu_res(self.reg.c, 7),
                0xba => self.reg.d = self.alu_res(self.reg.d, 7),
                0xbb => self.reg.e = self.alu_res(self.reg.e, 7),
                0xbc => self.reg.h = self.alu_res(self.reg.h, 7),
                0xbd => self.reg.l = self.alu_res(self.reg.l, 7),
                0xbe => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    let h = self.alu_res(v, 7);
                    self.mem.borrow_mut().set(a, h);
                }
                0xbf => self.reg.a = self.alu_res(self.reg.a, 7),
                ...
            }
        }
        ...
    }
}
```

**SET**

1) 描述

置位寄存器中指定的 bit 位.

2) 标志位变化

无

3) 指令

Instruction | Parameters | Opcode | Cycles
----------- | ---------- | ------ | ------
SET         | B, 0       | c0     | 8
SET         | C, 0       | c1     | 8
SET         | D, 0       | c2     | 8
SET         | E, 0       | c3     | 8
SET         | H, 0       | c4     | 8
SET         | L, 0       | c5     | 8
SET         | (HL), 0    | c6     | 16
SET         | A, 0       | c7     | 8
SET         | B, 1       | c8     | 8
SET         | C, 1       | c9     | 8
SET         | D, 1       | ca     | 8
SET         | E, 1       | cb     | 8
SET         | H, 1       | cc     | 8
SET         | L, 1       | cd     | 8
SET         | (HL), 1    | ce     | 16
SET         | A, 1       | cf     | 8
SET         | B, 2       | d0     | 8
SET         | C, 2       | d1     | 8
SET         | D, 2       | d2     | 8
SET         | E, 2       | d3     | 8
SET         | H, 2       | d4     | 8
SET         | L, 2       | d5     | 8
SET         | (HL), 2    | d6     | 16
SET         | A, 2       | d7     | 8
SET         | B, 3       | d8     | 8
SET         | C, 3       | d9     | 8
SET         | D, 3       | da     | 8
SET         | E, 3       | db     | 8
SET         | H, 3       | dc     | 8
SET         | L, 3       | dd     | 8
SET         | (HL), 3    | de     | 16
SET         | A, 3       | df     | 8
SET         | B, 4       | e0     | 8
SET         | C, 4       | e1     | 8
SET         | D, 4       | e2     | 8
SET         | E, 4       | e3     | 8
SET         | H, 4       | e4     | 8
SET         | L, 4       | e5     | 8
SET         | (HL), 4    | e6     | 16
SET         | A, 4       | e7     | 8
SET         | B, 5       | e8     | 8
SET         | C, 5       | e9     | 8
SET         | D, 5       | ea     | 8
SET         | E, 5       | eb     | 8
SET         | H, 5       | ec     | 8
SET         | L, 5       | ed     | 8
SET         | (HL), 5    | ee     | 16
SET         | A, 5       | ef     | 8
SET         | B, 6       | f0     | 8
SET         | C, 6       | f1     | 8
SET         | D, 6       | f2     | 8
SET         | E, 6       | f3     | 8
SET         | H, 6       | f4     | 8
SET         | L, 6       | f5     | 8
SET         | (HL), 6    | f6     | 16
SET         | A, 6       | f7     | 8
SET         | B, 7       | f8     | 8
SET         | C, 7       | f9     | 8
SET         | D, 7       | fa     | 8
SET         | E, 7       | fb     | 8
SET         | H, 7       | fc     | 8
SET         | L, 7       | fd     | 8
SET         | (HL), 7    | fe     | 16
SET         | A, 7       | ff     | 8


4) 代码实现

```rs
impl Cpu {
    // Set bit b in register r.
    // b = 0 - 7, r = A,B,C,D,E,H,L,(HL)
    //
    // Flags affected:  None.
    fn alu_set(&mut self, a: u8, b: u8) -> u8 {
        a | (1 << b)
    }
}

fn ex(&mut self) -> u32 {
    let opcode = self.imm();
    match opcode {
        0xcb => {
            cbcode = self.mem.borrow().get(self.reg.pc);
            self.reg.pc += 1;
            match cbcode {
                0xc0 => self.reg.b = self.alu_set(self.reg.b, 0),
                0xc1 => self.reg.c = self.alu_set(self.reg.c, 0),
                0xc2 => self.reg.d = self.alu_set(self.reg.d, 0),
                0xc3 => self.reg.e = self.alu_set(self.reg.e, 0),
                0xc4 => self.reg.h = self.alu_set(self.reg.h, 0),
                0xc5 => self.reg.l = self.alu_set(self.reg.l, 0),
                0xc6 => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    let h = self.alu_set(v, 0);
                    self.mem.borrow_mut().set(a, h);
                }
                0xc7 => self.reg.a = self.alu_set(self.reg.a, 0),
                0xc8 => self.reg.b = self.alu_set(self.reg.b, 1),
                0xc9 => self.reg.c = self.alu_set(self.reg.c, 1),
                0xca => self.reg.d = self.alu_set(self.reg.d, 1),
                0xcb => self.reg.e = self.alu_set(self.reg.e, 1),
                0xcc => self.reg.h = self.alu_set(self.reg.h, 1),
                0xcd => self.reg.l = self.alu_set(self.reg.l, 1),
                0xce => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    let h = self.alu_set(v, 1);
                    self.mem.borrow_mut().set(a, h);
                }
                0xcf => self.reg.a = self.alu_set(self.reg.a, 1),
                0xd0 => self.reg.b = self.alu_set(self.reg.b, 2),
                0xd1 => self.reg.c = self.alu_set(self.reg.c, 2),
                0xd2 => self.reg.d = self.alu_set(self.reg.d, 2),
                0xd3 => self.reg.e = self.alu_set(self.reg.e, 2),
                0xd4 => self.reg.h = self.alu_set(self.reg.h, 2),
                0xd5 => self.reg.l = self.alu_set(self.reg.l, 2),
                0xd6 => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    let h = self.alu_set(v, 2);
                    self.mem.borrow_mut().set(a, h);
                }
                0xd7 => self.reg.a = self.alu_set(self.reg.a, 2),
                0xd8 => self.reg.b = self.alu_set(self.reg.b, 3),
                0xd9 => self.reg.c = self.alu_set(self.reg.c, 3),
                0xda => self.reg.d = self.alu_set(self.reg.d, 3),
                0xdb => self.reg.e = self.alu_set(self.reg.e, 3),
                0xdc => self.reg.h = self.alu_set(self.reg.h, 3),
                0xdd => self.reg.l = self.alu_set(self.reg.l, 3),
                0xde => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    let h = self.alu_set(v, 3);
                    self.mem.borrow_mut().set(a, h);
                }
                0xdf => self.reg.a = self.alu_set(self.reg.a, 3),
                0xe0 => self.reg.b = self.alu_set(self.reg.b, 4),
                0xe1 => self.reg.c = self.alu_set(self.reg.c, 4),
                0xe2 => self.reg.d = self.alu_set(self.reg.d, 4),
                0xe3 => self.reg.e = self.alu_set(self.reg.e, 4),
                0xe4 => self.reg.h = self.alu_set(self.reg.h, 4),
                0xe5 => self.reg.l = self.alu_set(self.reg.l, 4),
                0xe6 => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    let h = self.alu_set(v, 4);
                    self.mem.borrow_mut().set(a, h);
                }
                0xe7 => self.reg.a = self.alu_set(self.reg.a, 4),
                0xe8 => self.reg.b = self.alu_set(self.reg.b, 5),
                0xe9 => self.reg.c = self.alu_set(self.reg.c, 5),
                0xea => self.reg.d = self.alu_set(self.reg.d, 5),
                0xeb => self.reg.e = self.alu_set(self.reg.e, 5),
                0xec => self.reg.h = self.alu_set(self.reg.h, 5),
                0xed => self.reg.l = self.alu_set(self.reg.l, 5),
                0xee => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    let h = self.alu_set(v, 5);
                    self.mem.borrow_mut().set(a, h);
                }
                0xef => self.reg.a = self.alu_set(self.reg.a, 5),
                0xf0 => self.reg.b = self.alu_set(self.reg.b, 6),
                0xf1 => self.reg.c = self.alu_set(self.reg.c, 6),
                0xf2 => self.reg.d = self.alu_set(self.reg.d, 6),
                0xf3 => self.reg.e = self.alu_set(self.reg.e, 6),
                0xf4 => self.reg.h = self.alu_set(self.reg.h, 6),
                0xf5 => self.reg.l = self.alu_set(self.reg.l, 6),
                0xf6 => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    let h = self.alu_set(v, 6);
                    self.mem.borrow_mut().set(a, h);
                }
                0xf7 => self.reg.a = self.alu_set(self.reg.a, 6),
                0xf8 => self.reg.b = self.alu_set(self.reg.b, 7),
                0xf9 => self.reg.c = self.alu_set(self.reg.c, 7),
                0xfa => self.reg.d = self.alu_set(self.reg.d, 7),
                0xfb => self.reg.e = self.alu_set(self.reg.e, 7),
                0xfc => self.reg.h = self.alu_set(self.reg.h, 7),
                0xfd => self.reg.l = self.alu_set(self.reg.l, 7),
                0xfe => {
                    let a = self.reg.get_hl();
                    let v = self.mem.borrow().get(a);
                    let h = self.alu_set(v, 7);
                    self.mem.borrow_mut().set(a, h);
                }
                0xff => self.reg.a = self.alu_set(self.reg.a, 7),
                ...
            }
        }
        ...
    }
}
```
