# GB/音频/白噪音通道

噪音通道通常用于发出一些 "无规则的噪音". 早期的游戏主机空间既小又昂贵, 通过噪音通道模拟爆炸声或游戏背景音 "嗡嗡" 声, 是非常常见的一种做法. 噪音通道结构主要由三部分组成, 分别是长度计数器, 音量包络和线性反馈移位寄存器(Linear feedback shift register, LFSR). 前两个组件的功能与其他音频通道一致, 唯一区别在于 LFSR: LFSR 连接在音量包络之后, 它可以生成一连串 0, 1 序列, 如果当前生成的是 0, 则屏蔽音量包络的输出; 如果当前生成的是 1, 则正常放行音量包络的输出.

## LFSR

线性反馈移位寄存器是指给定前一状态的输出, 将该输出的线性函数再用作输入的移位寄存器. 异或运算是最常见的单比特线性函数: 对寄存器的某些位进行异或操作后作为输入, 再对寄存器中的各比特进行整体移位.

赋给寄存器的初始值叫做 "种子", 因为线性反馈移位寄存器的运算是确定性的, 所以, 由寄存器所生成的数据流完全决定于寄存器当时或者之前的状态. 而且, 由于寄存器的状态是有限的, 它最终肯定会是一个重复的循环. 然而, 通过本原多项式, 线性反馈移位寄存器可以生成看起来是随机的且循环周期非常长的序列.

线性反馈移位寄存器的应用包括生成伪随机数, 伪随机噪声序列, 快速数字计数器, 还有扰频器. 线性反馈移位寄存器在硬件和软件方面的应用都非常得普遍.

Game Boy 的 LFSR 可以生成伪随机的比特序列, 它有一个带反馈的 15 位移位寄存器. 当噪音通道的定时器生成一个时钟信号时, LFSR 低两位（0 和 1）被异或, 并且所有比特位右移一位, 同时异或的结果被放入现在为空的高位. 如果宽度模式为 1(由 NR43 寄存器决定), 则在移位后, 异或结果也会进入第 6 比特位, 从而产生 7 位宽度的 LFSR. LFSR 的第 0 位的取反将参与最终波形的计算.

## FF20

|   位    |     名称     |   说明   |
| ------- | ------------ | -------- |
| Bit 5-0 | Sound length | 声音长度 |

用于长度计数器(LengthCounter)计数的初始值. 当 NR44 的第 6 位被设置为 1 时, 长度计数器将加载 Sound Length.

## FF21

|   位    |            名称            |                说明                |
| ------- | -------------------------- | ---------------------------------- |
| Bit 7-4 | Initial Volume of envelope | 范围为(00-0F) (0=No Sound)         |
| Bit 3   | Envelope Direction         | 0: 减少, 1: 增加                   |
| Bit 2-0 | Number of envelope sweep   | 范围 0-7, 如果是 0, 则停止音量包络 |

## FF22

在给定频率下, 声波振幅在高和低之间随机切换. 较高的频率将使噪声显得 "更柔和". 当 Bit 3 被设置时, 输出将变得更加规则, 并且某些频率听起来更像 "音调" 而不是 "噪声".

|   位    |             名称              |                       说明                        |
| ------- | ----------------------------- | ------------------------------------------------- |
| Bit 7-4 | Shift Clock Frequency         | 和 Dividing Ratio of Frequencies 一起决定时钟频率 |
| Bit 3   | Counter Step/Width            | LSFR 宽度模式                                     |
| Bit 2-0 | Dividing Ratio of Frequencies | 和 Shift Clock Frequency 一起决定时钟频率         |

白噪声通道定时器的周期计算公式为:

```rs
let d = match reg.borrow().get_dividor_code() { // Dividing Ratio of Frequencies
    0 => 8,
    n => (u32::from(n) + 1) * 16,
};
d << reg.borrow().get_clock_shift() // Shift Clock Frequency
```

LSFR 的宽度有两种可能值, 其由 Counter Step/Width 控制. 当为 1 时, 宽度是 0x06; 当为 0 时, 宽度是 0x0e.

## FF23

与其他音频通道的最后一个寄存器效果一样, 区别在于该寄存器的低 3 位不再表示 "频率的高 3 位".

|  位   |             名称              |                说明                |
| ----- | ----------------------------- | ---------------------------------- |
| Bit 7 | Initial                       | 写入 1, 则重启音频系统             |
| Bit 6 | Counter/consecutive selection | 写入 1, 则长度计数器到期后停止输出 |

## 代码实现

在实现 LFSR 的时候, 我稍微修改了一下实现的逻辑: 原文档中寄存器是低位异或, 然后右移; 在下面的代码实现中, 采用的高位异或并且左移. 采用第二种方案, 代码的实现会稍微简洁一点.

```rs
// The linear feedback shift register (LFSR) generates a pseudo-random bit sequence. It has a 15-bit shift register
// with feedback. When clocked by the frequency timer, the low two bits (0 and 1) are XORed, all bits are shifted right
// by one, and the result of the XOR is put into the now-empty high bit. If width mode is 1 (NR43), the XOR result is
// ALSO put into bit 6 AFTER the shift, resulting in a 7-bit LFSR. The waveform output is bit 0 of the LFSR, INVERTED.
struct Lfsr {
    reg: Rc<RefCell<Register>>,
    n: u16,
}

impl Lfsr {
    fn power_up(reg: Rc<RefCell<Register>>) -> Self {
        Self { reg, n: 0x0001 }
    }

    fn next(&mut self) -> bool {
        let s = if self.reg.borrow().get_width_mode_of_lfsr() {
            0x06
        } else {
            0x0e
        };
        let src = self.n;
        self.n <<= 1;
        let bit = ((src >> s) ^ (self.n >> s)) & 0x0001;
        self.n |= bit;
        (src >> s) & 0x0001 != 0x0000
    }

    fn reload(&mut self) {
        self.n = 0x0001
    }
}
```

补完噪音通道的代码:

```rs
struct ChannelNoise {
    reg: Rc<RefCell<Register>>,
    timer: Timer,
    lc: LengthCounter,
    ve: VolumeEnvelope,
    lfsr: Lfsr,
    blip: Blip,
}

impl ChannelNoise {
    fn power_up(blip: BlipBuf) -> ChannelNoise {
        let reg = Rc::new(RefCell::new(Register::power_up(Channel::Noise)));
        ChannelNoise {
            reg: reg.clone(),
            timer: Timer::power_up(4096),
            lc: LengthCounter::power_up(reg.clone()),
            ve: VolumeEnvelope::power_up(reg.clone()),
            lfsr: Lfsr::power_up(reg.clone()),
            blip: Blip::power_up(blip),
        }
    }

    fn next(&mut self, cycles: u32) {
        for _ in 0..self.timer.next(cycles) {
            let ampl = if !self.reg.borrow().get_trigger() || self.ve.volume == 0 {
                0x00
            } else if self.lfsr.next() {
                i32::from(self.ve.volume)
            } else {
                i32::from(self.ve.volume) * -1
            };
            self.blip.set(self.blip.from + self.timer.period, ampl);
        }
    }
}

impl Memory for ChannelNoise {
    fn get(&self, a: u16) -> u8 {
        match a {
            0xff1f => self.reg.borrow().nrx0,
            0xff20 => self.reg.borrow().nrx1,
            0xff21 => self.reg.borrow().nrx2,
            0xff22 => self.reg.borrow().nrx3,
            0xff23 => self.reg.borrow().nrx4,
            _ => unreachable!(),
        }
    }

    fn set(&mut self, a: u16, v: u8) {
        match a {
            0xff1f => self.reg.borrow_mut().nrx0 = v,
            0xff20 => {
                self.reg.borrow_mut().nrx1 = v;
                self.lc.n = self.reg.borrow().get_length_load();
            }
            0xff21 => self.reg.borrow_mut().nrx2 = v,
            0xff22 => {
                self.reg.borrow_mut().nrx3 = v;
                self.timer.period = period(self.reg.clone());
            }
            0xff23 => {
                self.reg.borrow_mut().nrx4 = v;
                if self.reg.borrow().get_trigger() {
                    self.lc.reload();
                    self.ve.reload();
                    self.lfsr.reload();
                }
            }
            _ => unreachable!(),
        }
    }
}
```
