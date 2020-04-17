# 寄存器

声音寄存器映射到内存中的 0xff10 到 0xff3f 地址. 每个音频通道均有五个逻辑寄存器, 依次命名为 NRx0 到 NRx4, 但有些通道可能不会使用 NRx0 寄存器. 每个寄存器均是 8 位大小, 它的 8 个 bit 通常被划分为不同的位段, 被不同的逻辑程序或电路所使用. 下表展示了每个寄存器在不同音频通道中的作用. 标有 "-" 的位的值没有实际作用. 对寄存器中的值的引用意味着写入的最后一个值, 即虽然 "-" 位不会被使用, 但依然能被正常读取.

```no-highlight
-----------------------------------------------------------------
       Square 1
NR10 FF10 -PPP NSSS Sweep period, negate, shift
NR11 FF11 DDLL LLLL Duty, Length load (64-L)
NR12 FF12 VVVV APPP Starting volume, Envelope add mode, period
NR13 FF13 FFFF FFFF Frequency LSB
NR14 FF14 TL-- -FFF Trigger, Length enable, Frequency MSB

       Square 2
     FF15 ---- ---- Not used
NR21 FF16 DDLL LLLL Duty, Length load (64-L)
NR22 FF17 VVVV APPP Starting volume, Envelope add mode, period
NR23 FF18 FFFF FFFF Frequency LSB
NR24 FF19 TL-- -FFF Trigger, Length enable, Frequency MSB

       Wave
NR30 FF1A E--- ---- DAC power
NR31 FF1B LLLL LLLL Length load (256-L)
NR32 FF1C -VV- ---- Volume code (00=0%, 01=100%, 10=50%, 11=25%)
NR33 FF1D FFFF FFFF Frequency LSB
NR34 FF1E TL-- -FFF Trigger, Length enable, Frequency MSB

       Noise
     FF1F ---- ---- Not used
NR41 FF20 --LL LLLL Length load (64-L)
NR42 FF21 VVVV APPP Starting volume, Envelope add mode, period
NR43 FF22 SSSS WDDD Clock shift, Width mode of LFSR, Divisor code
NR44 FF23 TL-- ---- Trigger, Length enable

       Control/Status
NR50 FF24 ALLL BRRR Vin L enable, Left vol, Vin R enable, Right vol
NR51 FF25 NW21 NW21 Left enables, Right enables
NR52 FF26 P--- NW21 Power control/status, Channel length statuses

       Not used
     FF27 ---- ----
     .... ---- ----
     FF2F ---- ----

       Wave Table
     FF30 0000 1111 Samples 0 and 1
     ....
     FF3F 0000 1111 Samples 30 and 31
```

初次阅读此表可能会产生一些疑惑, 这里以此表的第一个寄存器 Square1 的 NR10 寄存器进行解释说明:

```no-highlight
NR10 FF10 -PPP NSSS Sweep period, negate, shift
```

NR10 是寄存器的名字, FF10 表示该寄存器被映射到内存中的地址, "-PPP NSSS Sweep period, negate, shift" 表示该寄存器低 3 位的助记词是 shift, 第 3 位的助记词是 negate, 第 4 到 6 位的助记词是 Sweep period.

# 控制与状态寄存器

有 3 个寄存器可以对 Game Boy 进行全局的系统控制, 它们分别被映射到内存地址的 0xff24, 0xff25 与 0xff26.

- 0xff24 分别控制左声道音量启用/禁用, 左声道音量, 右声道音量启用/禁用和右声道音量
- 0xff25 分别控制左声道启用/警用和右声道启用/警用
- 0xff26 分别控制音频系统总开关与 4 个通道的当前状态

0xff24 与 0xff25 寄存器中的两个启用/警用开关有所区别, 前者是决定是否将音量增益/衰减应用到原始数据上, 而后者则决定是否完全关闭左右声道的音频输出. 0xff25 寄存器的每一位表示如下

|  位   |                                    |
| ----- | ---------------------------------- |
| Bit 7 | 白噪声通道是否允许从左声道输出     |
| Bit 6 | 可编程波形通道是否允许从左声道输出 |
| Bit 5 | 方波通道 2 是否允许从左声道输出    |
| Bit 4 | 方波通道 1 是否允许从左声道输出    |
| Bit 3 | 白噪声通道是否允许从右声道输出     |
| Bit 2 | 可编程波形通道是否允许从右声道输出 |
| Bit 1 | 方波通道 2 是否允许从右声道输出    |
| Bit 0 | 方波通道 1 是否允许从右声道输出    |

0xff26 寄存器的第一位通常可以是 1, 当然前提是音频系统正在运行时; 而后 4 位表示当前 4 个音频通道的状态. 当音频通道正在工作时, 则相应位为 1, 否则为 0. 因此, 考虑如下一种情形, 方波通道 2 被禁用而其他所有音频通道均在正常执行, 则 0xff26 的值为(以二进制位表示)

```no-highlight
| 1 | - | - | - | 1 | 1 | 0 | 1 |
```

# 代码实现

定义一个枚举类型, 表明寄存器被应用在哪个音频通道中.

```rs
#[derive(Clone, Eq, PartialEq)]
enum Channel {
    Square1,
    Square2,
    Wave,
    Noise,
}
```

定义寄存器结构体, 它拥有一个 channel 字段表明当前的音频通道类型, 以及 5 个 u8 类型的成员变量用于存储数据.

```rs
struct Register {
    channel: Channel,
    nrx0: u8,
    nrx1: u8,
    nrx2: u8,
    nrx3: u8,
    nrx4: u8,
}
```

定义一些简便方法来完成寄存器中的数值读取和修改. 某些数据类型是专用于某些音频通道的, 因此会在代码中使用 assert 语法进行限定, 可以避免类似在 Suqare 2 通道读取 NRX0 寄存器中的值一类的错误.

```rs
impl Register {
    fn get_sweep_period(&self) -> u8 {
        assert!(self.channel == Channel::Square1);
        (self.nrx0 >> 4) & 0x07
    }

    fn get_negate(&self) -> bool {
        assert!(self.channel == Channel::Square1);
        self.nrx0 & 0x08 != 0x00
    }

    fn get_shift(&self) -> u8 {
        assert!(self.channel == Channel::Square1);
        self.nrx0 & 0x07
    }

    fn get_dac_power(&self) -> bool {
        assert!(self.channel == Channel::Wave);
        self.nrx0 & 0x80 != 0x00
    }

    fn get_duty(&self) -> u8 {
        assert!(self.channel == Channel::Square1 || self.channel == Channel::Square2);
        self.nrx1 >> 6
    }

    fn get_length_load(&self) -> u16 {
        if self.channel == Channel::Wave {
            (1 << 8) - u16::from(self.nrx1)
        } else {
            (1 << 6) - u16::from(self.nrx1 & 0x3f)
        }
    }

    fn get_starting_volume(&self) -> u8 {
        assert!(self.channel != Channel::Wave);
        self.nrx2 >> 4
    }

    fn get_volume_code(&self) -> u8 {
        assert!(self.channel == Channel::Wave);
        (self.nrx2 >> 5) & 0x03
    }

    fn get_envelope_add_mode(&self) -> bool {
        assert!(self.channel != Channel::Wave);
        self.nrx2 & 0x08 != 0x00
    }

    fn get_period(&self) -> u8 {
        assert!(self.channel != Channel::Wave);
        self.nrx2 & 0x07
    }

    fn get_frequency(&self) -> u16 {
        assert!(self.channel != Channel::Noise);
        u16::from(self.nrx4 & 0x07) << 8 | u16::from(self.nrx3)
    }

    fn set_frequency(&mut self, f: u16) {
        assert!(self.channel != Channel::Noise);
        let h = ((f >> 8) & 0x07) as u8;
        let l = f as u8;
        self.nrx4 = (self.nrx4 & 0xf8) | h;
        self.nrx3 = l;
    }

    fn get_clock_shift(&self) -> u8 {
        assert!(self.channel == Channel::Noise);
        self.nrx3 >> 4
    }

    fn get_width_mode_of_lfsr(&self) -> bool {
        assert!(self.channel == Channel::Noise);
        self.nrx3 & 0x08 != 0x00
    }

    fn get_dividor_code(&self) -> u8 {
        assert!(self.channel == Channel::Noise);
        self.nrx3 & 0x07
    }

    fn get_trigger(&self) -> bool {
        self.nrx4 & 0x80 != 0x00
    }

    fn set_trigger(&mut self, b: bool) {
        if b {
            self.nrx4 |= 0x80;
        } else {
            self.nrx4 &= 0x7f;
        };
    }

    fn get_length_enable(&self) -> bool {
        self.nrx4 & 0x40 != 0x00
    }
}
```

最后写上构造方法.

```rs
impl Register {
    fn power_up(channel: Channel) -> Self {
        Self {
            channel,
            nrx0: 0x00,
            nrx1: 0x00,
            nrx2: 0x00,
            nrx3: 0x00,
            nrx4: 0x00,
        }
    }
}
```
