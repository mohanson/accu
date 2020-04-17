# LR35902 时钟周期与频率仿真

CPU 的时钟频率简单说就是 CPU 运算时的工作的频率(1 秒内发生的同步脉冲数)的简称, 单位是 Hz. 它决定计算机的运行速度. 在 21 世纪初的时候, 许多 DIY 爱好者喜欢对 CPU 做"超频"处理, 即把 CPU 的时脉速度提升至高于厂方所定的速度运作, 从而提升性能. 但由于此种操作会影响 CPU 的寿命和稳定性, 近些年已经鲜少有人再这么做.

Game Boy 的 LR35902 CPU 的时钟频率是 4194304 Hz 或 4 MHz.

# 指令周期

指令周期是指 CPU 执行一条机器指令需要消耗的时钟周期. LR35902 指令集的指令周期可以用如下的数组表示:

1) 标准指令集

```rs
//  0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
[
    1, 3, 2, 2, 1, 1, 2, 1, 5, 2, 2, 2, 1, 1, 2, 1, // 0
    0, 3, 2, 2, 1, 1, 2, 1, 3, 2, 2, 2, 1, 1, 2, 1, // 1
    2, 3, 2, 2, 1, 1, 2, 1, 2, 2, 2, 2, 1, 1, 2, 1, // 2
    2, 3, 2, 2, 3, 3, 3, 1, 2, 2, 2, 2, 1, 1, 2, 1, // 3
    1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, // 4
    1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, // 5
    1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, // 6
    2, 2, 2, 2, 2, 2, 0, 2, 1, 1, 1, 1, 1, 1, 2, 1, // 7
    1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, // 8
    1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, // 9
    1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, // a
    1, 1, 1, 1, 1, 1, 2, 1, 1, 1, 1, 1, 1, 1, 2, 1, // b
    2, 3, 3, 4, 3, 4, 2, 4, 2, 4, 3, 0, 3, 6, 2, 4, // c
    2, 3, 3, 0, 3, 4, 2, 4, 2, 4, 3, 0, 3, 0, 2, 4, // d
    3, 3, 2, 0, 0, 4, 2, 4, 4, 1, 4, 0, 0, 0, 2, 4, // e
    3, 3, 2, 1, 0, 4, 2, 4, 3, 2, 4, 1, 0, 0, 2, 4, // f
]
```

比如 Opcode 为 0x16 的指令, 可以通过查找上表的第一行第六列获取它的指令周期表示.

2) 扩展指令集

```rs
//  0  1  2  3  4  5  6  7  8  9  a  b  c  d  e  f
[
    2, 2, 2, 2, 2, 2, 4, 2, 2, 2, 2, 2, 2, 2, 4, 2, // 0
    2, 2, 2, 2, 2, 2, 4, 2, 2, 2, 2, 2, 2, 2, 4, 2, // 1
    2, 2, 2, 2, 2, 2, 4, 2, 2, 2, 2, 2, 2, 2, 4, 2, // 2
    2, 2, 2, 2, 2, 2, 4, 2, 2, 2, 2, 2, 2, 2, 4, 2, // 3
    2, 2, 2, 2, 2, 2, 3, 2, 2, 2, 2, 2, 2, 2, 3, 2, // 4
    2, 2, 2, 2, 2, 2, 3, 2, 2, 2, 2, 2, 2, 2, 3, 2, // 5
    2, 2, 2, 2, 2, 2, 3, 2, 2, 2, 2, 2, 2, 2, 3, 2, // 6
    2, 2, 2, 2, 2, 2, 3, 2, 2, 2, 2, 2, 2, 2, 3, 2, // 7
    2, 2, 2, 2, 2, 2, 4, 2, 2, 2, 2, 2, 2, 2, 4, 2, // 8
    2, 2, 2, 2, 2, 2, 4, 2, 2, 2, 2, 2, 2, 2, 4, 2, // 9
    2, 2, 2, 2, 2, 2, 4, 2, 2, 2, 2, 2, 2, 2, 4, 2, // a
    2, 2, 2, 2, 2, 2, 4, 2, 2, 2, 2, 2, 2, 2, 4, 2, // b
    2, 2, 2, 2, 2, 2, 4, 2, 2, 2, 2, 2, 2, 2, 4, 2, // c
    2, 2, 2, 2, 2, 2, 4, 2, 2, 2, 2, 2, 2, 2, 4, 2, // d
    2, 2, 2, 2, 2, 2, 4, 2, 2, 2, 2, 2, 2, 2, 4, 2, // e
    2, 2, 2, 2, 2, 2, 4, 2, 2, 2, 2, 2, 2, 2, 4, 2, // f
]
```

上述两个数组采用的是 Game Boy 硬件规范文档中的"机器周期"表述, 且 1 个机器周期等于 4 个 CPU 时钟周期. 因此当需要实际使用的时候, 需要乘上 4 再行计算.

需要特别注意的是, 有四种带条件的指令根据条件不同可能消耗不同的 CPU 时钟周期, 它们分别是:

- JR IF: 如果条件成立, 额外消耗 1 个机器周期(4 个时钟周期)
- RET IF: 如果条件成立, 额外消耗 3 个机器周期(12 个时钟周期)
- CALL IF: 如果条件成立, 额外消耗 3 个机器周期(12 个时钟周期)
- JUMP IF: 如果条件成立, 额外消耗 1 个机器周期(4 个时钟周期)

在实现仿真时, 首先根据 Opcode 获取该指令所固定消耗的指令周期, 然后判断该指令是否包含条件判断以及条件判断是否成立; 若成立, 则需要计算额外消耗的指令周期. 代码实现如下所示.

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
    let ecycle = match opcode {
        0x20 | 0x30 => {
            if self.reg.get_flag(Z) {
                0x00
            } else {
                0x01
            }
        }
        0x28 | 0x38 => {
            if self.reg.get_flag(Z) {
                0x01
            } else {
                0x00
            }
        }
        0xc0 | 0xd0 => {
            if self.reg.get_flag(Z) {
                0x00
            } else {
                0x03
            }
        }
        0xc8 | 0xcc | 0xd8 | 0xdc => {
            if self.reg.get_flag(Z) {
                0x03
            } else {
                0x00
            }
        }
        0xc2 | 0xd2 => {
            if self.reg.get_flag(Z) {
                0x00
            } else {
                0x01
            }
        }
        0xca | 0xda => {
            if self.reg.get_flag(Z) {
                0x01
            } else {
                0x00
            }
        }
        0xc4 | 0xd4 => {
            if self.reg.get_flag(Z) {
                0x00
            } else {
                0x03
            }
        }
        _ => 0x00,
    };
    if opcode == 0xcb {
        CB_CYCLES[cbcode as usize]
    } else {
        OP_CYCLES[opcode as usize] + ecycle
    }
}
```

由于 ex 函数返回的是机器周期, 在实际使用时大多需要转换为时钟周期, 故此添加以下函数, 在获取机器周期后乘以 4 再做返回.

```rs
impl Cpu {
    pub fn next(&mut self) -> u32 {
        self.ex() * 4
    }
}
```

# 频率仿真

目前家用电脑的 CPU 频率已经普遍到达 GHz 级别, 为了完成 Game Boy 仿真器, 仿真器系统必须保证呈现给外部的行为与真实硬件一致, 因此仿真器系统必须人为限制 LR35902 CPU 仿真代码的运行速度.

这里介绍一种最简单也是最常用的方法: CPU 仿真器每执行一段指令后休眠一段时间, 使每 1 秒时间内仿真器执行的所有指令的指令周期之和为 4194304.

为此可以创建一个新的结构 RTC(Real Time Clock), 经由它的控制来限制模拟 CPU 的执行速度. 下面的逻辑代码所执行的操作是可以表述为以下几步:

1. 记录当前的系统时间 T.
2. 开始执行指令, 当被执行的指令们的指令周期之和达到 67108(4194304 / 1000 * 16)时, 则进行休眠, 直到系统时间到达 T + 16 毫秒.
3. 重复步骤 1.

16 毫秒是一个在游戏领域和仿真器领域非常常见的值, 因为它代表了 60 帧率: 16 毫秒 * 60 ~= 1000 毫秒 ~= 1 秒. 虽然并不需要一定是 16, 但 16 真的是一个很棒的数字. 代码实现如下所示.

```rs
pub const CLOCK_FREQUENCY: u32 = 4_194_304;
pub const STEP_TIME: u32 = 16;
pub const STEP_CYCLES: u32 = (STEP_TIME as f64 / (1000_f64 / CLOCK_FREQUENCY as f64)) as u32;

// Real time cpu provided to simulate real hardware speed.
pub struct Rtc {
    pub cpu: Cpu,
    step_cycles: u32,
    step_zero: time::SystemTime,
    step_flip: bool,
}

impl Rtc {
    pub fn power_up(term: Term, mem: Rc<RefCell<Memory>>) -> Self {
        let cpu = Cpu::power_up(term, mem);
        Self {
            cpu,
            step_cycles: 0,
            step_zero: time::SystemTime::now(),
            step_flip: false,
        }
    }

    // Function next simulates real hardware execution speed, by
    // limiting the frequency of the function cpu.next().
    pub fn next(&mut self) -> u32 {
        if self.step_cycles > STEP_CYCLES {
            self.step_flip = true;
            self.step_cycles -= STEP_CYCLES;
            let d = time::SystemTime::now().duration_since(self.step_zero).unwrap();
            let s = u64::from(STEP_TIME.saturating_sub(d.as_millis() as u32));
            thread::sleep(time::Duration::from_millis(s));
            self.step_zero = self
                .step_zero
                .checked_add(time::Duration::from_millis(u64::from(STEP_TIME)))
                .unwrap();
        }
        let cycles = self.cpu.next();
        self.step_cycles += cycles;
        cycles
    }

    pub fn flip(&mut self) -> bool {
        let r = self.step_flip;
        if r {
            self.step_flip = false;
        }
        r
    }
}
```

其中 flip 函数返回一个布尔值, 用于判断是否产生了新的一帧. 在后期实现视频画面和游戏手柄时会需要用到这个函数, 因为在一些情况下需要每秒对一个指定条件进行 60 次判断. 如此一来, 一个按照真实硬件速度执行的 CPU 在代码中诞生了!
