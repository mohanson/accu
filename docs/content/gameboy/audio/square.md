# GB/音频/方波通道

方波通道 1 具有扫频和包络功能. 从功能组件来说, 方波通道 1 主要包含定时器, 长度计数器, 音量调节器和扫频器几个功能组件. 它与方波通道 2 几乎一致, 唯一区别是方波通道 2 不包含扫频器. 下面将先行介绍方波通道 1 的寄存器与其功能细节.

## FF10

|   位    |          名称           |                说明                 |
| ------- | ----------------------- | ----------------------------------- |
| Bit 6-4 | Sweep Time              | 扫频器周期                          |
| Bit 3   | Sweep Increase/Decrease | 0: 扫频器提升频率 1: 扫频器减少频率 |
| Bit 2-0 | Number of sweep shift   | 扫频器的移位值                      |

**Sweep Time**

- 000: sweep off - no freq change
- 001: 7.8 ms  (1/128Hz)
- 010: 15.6 ms (2/128Hz)
- 011: 23.4 ms (3/128Hz)
- 100: 31.3 ms (4/128Hz)
- 101: 39.1 ms (5/128Hz)
- 110: 46.9 ms (6/128Hz)
- 111: 54.7 ms (7/128Hz)

每个 shift 的频率变化(NR13, NR14)通过以下公式计算, 其中 X(0) 是初始频率, X(t-1) 是计算后的频率:

```no-highlight
X(t) = X(t-1) +/- X(t-1)/2^n
```

## FF11

|   位    |       名称        |      说明      |
| ------- | ----------------- | -------------- |
| Bit 7-6 | Wave Pattern Duty | 波形占空比模式 |
| Bit 5-0 | Sound length      | 声音长度       |

**Wave Duty**

Wave Duty 用于控制方波通道 1 的波形占空比. 方波通道 1 的音频输出会被裁剪, 在以 8 为周期的时间内, 只有其中固定的时间段会有声波输出, 其余时间无论原始声波的振幅是多少, 都以 0 对待. 下表列出了 Wave Duty 从 0 到 3 这四种情况对应的占空比信息. 当 Waveform 中的某位为 0 时, 即表示在以 8 为周期的时间内不允许该时间段输出音频信号.

| Duty | Waveform | Ratio |
|------|----------|-------|
| 00   | 00000001 | 12.5% |
| 01   | 10000001 | 25%   |
| 10   | 10000111 | 50%   |
| 11   | 01111110 | 75%   |

**Sound Length**

用于长度计数器(LengthCounter) 计数的初始值. 当 NR14 的第 6 位被设置为 1 时, 长度计数器将加载 Sound Length.

## FF12

|   位    |            名称            |                说明                |
| ------- | -------------------------- | ---------------------------------- |
| Bit 7-4 | Initial Volume of envelope | 范围为 (00-0F) (0=No Sound)        |
| Bit 3   | Envelope Direction         | 0: 减少, 1: 增加                   |
| Bit 2-0 | Number of envelope sweep   | 范围 0-7, 如果是 0, 则停止音量包络 |

## FF13

方波通道 1 的音频频率是 11 位无符号整数, 0xff13 寄存器存储该数字的低 8 为. 高 3 位存储在 0xff14 寄存器中.

## FF14

|   位    |             名称              |                说明                |
| ------- | ----------------------------- | ---------------------------------- |
| Bit 7   | Initial                       | 写入 1, 则重启音频系统             |
| Bit 6   | Counter/consecutive selection | 写入 1, 则长度计数器到期后停止输出 |
| Bit 2-0 | Frequency's higher 3 bits     | 频率的高 3 位                      |

频率用来设置音频通道内部计数器的值, 其公式是

```no-highlight
Peroid = (2048 - Frequency) * 4
```

## 方波通道 2 与方波通道 1 的区别

方波通道 2 与方波通道 1 首先在寄存器地址上有区别:

| 寄存器名称 | 方波通道 1 地址 | 方波通道 2 地址 |
| ---------- | --------------- | --------------- |
| NRX0       | 0xff10          | -               |
| NRX1       | 0xff11          | 0xff16          |
| NRX2       | 0xff12          | 0xff17          |
| NRX3       | 0xff13          | 0xff18          |
| NRX4       | 0xff14          | 0xff19          |

其次方波通道 2 不包含扫频器. 在代码实现上只需要屏蔽扫频器相关代码, 即可无缝迁移方波通道 1 的代码到方波通道 2. 不再赘述.

## 代码实现

为了保存音频数据, 代码内将用到 BlipBuf 库. 对该库做一次简单的封装:

```rs
struct Blip {
    data: BlipBuf,
    from: u32, // 最后一次改变振幅的时间点
    ampl: i32, // 当前振幅
}

impl Blip {
    fn power_up(data: BlipBuf) -> Self {
        Self {
            data,
            from: 0x0000_0000,
            ampl: 0x0000_0000,
        }
    }

    fn set(&mut self, time: u32, ampl: i32) {
        self.from = time;
        let d = ampl - self.ampl;
        self.ampl = ampl;
        self.data.add_delta(time, d);
    }
}
```


在了解方波通道的组件后, 代码实现异常简单, 主要处理好 next() 函数就可以了.

```rs
struct ChannelSquare {
    reg: Rc<RefCell<Register>>,
    timer: Timer,
    lc: LengthCounter,
    ve: VolumeEnvelope,
    fs: FrequencySweep,
    blip: Blip,
    idx: u8,
}

impl ChannelSquare {
    fn power_up(blip: BlipBuf, mode: Channel) -> ChannelSquare {
        let reg = Rc::new(RefCell::new(Register::power_up(mode.clone())));
        ChannelSquare {
            reg: reg.clone(),
            timer: Timer::power_up(8192),
            lc: LengthCounter::power_up(reg.clone()),
            ve: VolumeEnvelope::power_up(reg.clone()),
            fs: FrequencySweep::power_up(reg.clone()),
            blip: Blip::power_up(blip),
            idx: 1,
        }
    }

    // This assumes no volume or sweep adjustments need to be done in the meantime
    fn next(&mut self, cycles: u32) {
        let pat = match self.reg.borrow().get_duty() {
            0 => 0b0000_0001,
            1 => 0b1000_0001,
            2 => 0b1000_0111,
            3 => 0b0111_1110,
            _ => unreachable!(),
        };
        let vol = i32::from(self.ve.volume);
        for _ in 0..self.timer.next(cycles) {
            let ampl = if !self.reg.borrow().get_trigger() || self.ve.volume == 0 {
                0x00
            } else if (pat >> self.idx) & 0x01 != 0x00 {
                vol
            } else {
                vol * -1
            };
            self.blip.set(self.blip.from + self.timer.period, ampl);
            self.idx = (self.idx + 1) % 8;
        }
    }
}
```

之后为方波通道实现内存读写, 注意当写 0xff14 和 0xff19 内存时, 将触发事件操作. 其中扫频器的事件是方波通道 1 独有的.

```rs
impl Memory for ChannelSquare {
    fn get(&self, a: u16) -> u8 {
        match a {
            0xff10 | 0xff15 => self.reg.borrow().nrx0,
            0xff11 | 0xff16 => self.reg.borrow().nrx1,
            0xff12 | 0xff17 => self.reg.borrow().nrx2,
            0xff13 | 0xff18 => self.reg.borrow().nrx3,
            0xff14 | 0xff19 => self.reg.borrow().nrx4,
            _ => unreachable!(),
        }
    }

    fn set(&mut self, a: u16, v: u8) {
        match a {
            0xff10 | 0xff15 => self.reg.borrow_mut().nrx0 = v,
            0xff11 | 0xff16 => {
                self.reg.borrow_mut().nrx1 = v;
                self.lc.n = self.reg.borrow().get_length_load();
            }
            0xff12 | 0xff17 => self.reg.borrow_mut().nrx2 = v,
            0xff13 | 0xff18 => {
                self.reg.borrow_mut().nrx3 = v;
                self.timer.period = period(self.reg.clone());
            }
            0xff14 | 0xff19 => {
                self.reg.borrow_mut().nrx4 = v;
                self.timer.period = period(self.reg.clone());
                // Trigger Event
                //
                // Writing a value to NRx4 with bit 7 set causes the following things to occur:
                //
                //   - Channel is enabled (see length counter).
                //   - If length counter is zero, it is set to 64 (256 for wave channel).
                //   - Frequency timer is reloaded with period.
                //   - Volume envelope timer is reloaded with period.
                //   - Channel volume is reloaded from NRx2.
                //   - Noise channel's LFSR bits are all set to 1.
                //   - Wave channel's position is set to 0 but sample buffer is NOT refilled.
                //   - Square 1's sweep does several things (see frequency sweep).
                //
                // Note that if the channel's DAC is off, after the above actions occur the channel will be immediately
                // disabled again.
                if self.reg.borrow().get_trigger() {
                    self.lc.reload();
                    self.ve.reload();
                    if self.reg.borrow().channel == Channel::Square1 {
                        self.fs.reload();
                    }
                }
            }
            _ => unreachable!(),
        }
    }
}
```
