# 可编程波形通道

该通道可用于输出数字音频, 波形通道内部保存一个 16 字节长度的波形表, 每 4 Bit 采样一次, 因此波形通道可以播放周期为 32 的音频. 每个字节编码两个样本, 其中高位具有较高优先级. 波形通道同时具有一个位置计数器, 标明当前已经播放到波表的第几项.

# FF1A

|  位   |     名称     |       说明        |
| ----- | ------------ | ----------------- |
| Bit 7 | Sound on/off | DAC 启用/禁用标志 |

可编程波形通道同时具有一个 DAC(数位转换器)组件, 它接收数字信号并将其转换为模拟信号. 该组件的具体功能表达为: 从波表接收当前采样值 sample, 然后从寄存器中读取 volumn_code, 根据 volumn_code 找到对应的 shift 值, 并进行按位右移, 最终输出 sample >> shift. 即使禁用 DAC, 可编程波形通道依然会正常运作, 只是其音频输入始终为 0.

# FF1B

|   位    |     名称     |   说明   |
| ------- | ------------ | -------- |
| Bit 7-0 | Sound length | 声音长度 |

用于长度计数器(LengthCounter)计数的初始值. 当 NR34 的第 6 位被设置为 1 时, 长度计数器将加载 Sound Length.

# FF1C

|   位    |        名称         |     说明     |
| ------- | ------------------- | ------------ |
| Bit 6-5 | Select output level | 衰减输出音量 |

不同 Select output level 下对应的音量衰减的值:

- 0: 静音. 由于 Wave RAM 内的数据范围为 0 - 15, 相当于对其右移 4 位.
- 1: 100% 音量. 不做处理.
- 2: 50% 音量. 相当于对 Wave RAM 的数据右移 1 位.
- 3: 25% 音量. 相当于对 Wave RAM 的数据右移 2 位.

# FF1D

可编程波形通道的音频频率是 11 位无符号整数, 0xff1d 寄存器存储该数字的低 8 为. 高 3 位存储在 0xff1e 寄存器中.

# FF1E

|   位    |             名称              |                说明                |
| ------- | ----------------------------- | ---------------------------------- |
| Bit 7   | Initial                       | 写入 1, 则重启音频系统             |
| Bit 6   | Counter/consecutive selection | 写入 1, 则长度计数器到期后停止输出 |
| Bit 2-0 | Frequency's higher 3 bits     | 频率的高 3 位                      |

频率用来设置音频通道内部计数器的值, 其公式是

```no-highlight
Peroid = (2048 - Frequency) * 2
```

# FF30-FF3F 波形采样数据

该内存区间存储了任意声音数据的波形采样数据. 每一个采样数据占 4 位(0 - 15), 因此该存储区可以保存 32 个 4 位音频采样, 这些采样数据将被播放, 播放时首先播放高 4 位.

# 代码实现

代码结构与 Square 区别不大. 需要注意的是当触发事件时, waveidx 需要被重置为 0.

```rs
// The wave channel plays a 32-entry wave table made up of 4-bit samples. Each byte encodes two samples, the first in
// the high bits. The wave channel has a sample buffer and position counter.
// The wave channel's frequency timer period is set to (2048-frequency)*2. When the timer generates a clock, the
// position counter is advanced one sample in the wave table, looping back to the beginning when it goes past the end,
// then a sample is read into the sample buffer from this NEW position.
// The DAC receives the current value from the upper/lower nibble of the sample buffer, shifted right by the volume
// control.
//
// Code   Shift   Volume
// -----------------------
// 0      4         0% (silent)
// 1      0       100%
// 2      1        50%
// 3      2        25%
// Wave RAM can only be properly accessed when the channel is disabled (see obscure behavior).
struct ChannelWave {
    reg: Rc<RefCell<Register>>,
    timer: Timer,
    lc: LengthCounter,
    blip: Blip,
    waveram: [u8; 16],
    waveidx: usize,
}

impl ChannelWave {
    fn power_up(blip: BlipBuf) -> ChannelWave {
        let reg = Rc::new(RefCell::new(Register::power_up(Channel::Wave)));
        ChannelWave {
            reg: reg.clone(),
            timer: Timer::power_up(8192),
            lc: LengthCounter::power_up(reg.clone()),
            blip: Blip::power_up(blip),
            waveram: [0x00; 16],
            waveidx: 0x00,
        }
    }

    fn next(&mut self, cycles: u32) {
        let s = match self.reg.borrow().get_volume_code() {
            0 => 4,
            1 => 0,
            2 => 1,
            3 => 2,
            _ => unreachable!(),
        };
        for _ in 0..self.timer.next(cycles) {
            let sample = if self.waveidx & 0x01 == 0x00 {
                self.waveram[self.waveidx / 2] & 0x0f
            } else {
                self.waveram[self.waveidx / 2] >> 4
            };
            let ampl = if !self.reg.borrow().get_trigger() || !self.reg.borrow().get_dac_power() {
                0x00
            } else {
                i32::from(sample >> s)
            };
            self.blip.set(self.blip.from + self.timer.period, ampl);
            self.waveidx = (self.waveidx + 1) % 32;
        }
    }
}

impl Memory for ChannelWave {
    fn get(&self, a: u16) -> u8 {
        match a {
            0xff1a => self.reg.borrow().nrx0,
            0xff1b => self.reg.borrow().nrx1,
            0xff1c => self.reg.borrow().nrx2,
            0xff1d => self.reg.borrow().nrx3,
            0xff1e => self.reg.borrow().nrx4,
            0xff30...0xff3f => self.waveram[a as usize - 0xff30],
            _ => unreachable!(),
        }
    }

    fn set(&mut self, a: u16, v: u8) {
        match a {
            0xff1a => self.reg.borrow_mut().nrx0 = v,
            0xff1b => {
                self.reg.borrow_mut().nrx1 = v;
                self.lc.n = self.reg.borrow().get_length_load();
            }
            0xff1c => self.reg.borrow_mut().nrx2 = v,
            0xff1d => {
                self.reg.borrow_mut().nrx3 = v;
                self.timer.period = period(self.reg.clone());
            }
            0xff1e => {
                self.reg.borrow_mut().nrx4 = v;
                self.timer.period = period(self.reg.clone());
                if self.reg.borrow().get_trigger() {
                    self.lc.reload();
                    self.waveidx = 0x00;
                }
            }
            0xff30...0xff3f => self.waveram[a as usize - 0xff30] = v,
            _ => unreachable!(),
        }
    }
}
```
