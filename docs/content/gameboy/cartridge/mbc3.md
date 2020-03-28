# MBC3

与 MBC2 一样, MBC3 也与 MBC1 非常类似, 区别在于 MBC3 包含一个新的硬件设备: 实时时钟(RealTimeClock, RTC). 实时时钟类似一个内置在卡带中的时钟, 通过它, 游戏程式可以获取到"流逝的时间", 用以反向推算当前的日期, 时刻, 游戏时长等信息. 一个广为人知的案例是 MBC3 芯片在《精灵宝可梦》游戏系列中的广泛使用, 在《精灵宝可梦-水晶》中拥有与现实世界一致的昼夜系统和星期系统: ——有些精灵只出现在白天或夜晚, 甚至是特殊的限定稀有精灵乘龙, 只有在周五黄昏才会出现在 32 号道路洞穴深处水面.

RTC 需要一个外部的 32.768kHz Quartz 振荡器和一枚外部纽扣电池才能工作, 因此即使 Game Boy 关闭后, RTC 仍然会依靠电池而继续工作. 不过也正因为如此, MBC3 芯片电池的耗电速度明显加快.

精灵宝可梦-水晶中的昼/夜系统:

![img](/img/gameboy/cartridge/mbc3/crystal.png)

# MBC3 地址空间划分

MBC3 芯片将 Game Boy 分配给游戏卡带的系统地址空间 0x0000...0x7fff 和 0xa000...0xbfff 划分为以下几个独立区间, 详细介绍如下.

1) 0000-3FFF ROM 存储体 00

只读区域. 该区域总是映射到 ROM 的前 16KB 字节物理存储.

2) 4000-7FFF ROM 存储体 01-7F

只读区域. 该区域可以映射为第 0x01 到 0x7f 编号的 ROM 存储体. 与 MBC1 逻辑大体相同, 但存储体 0x20h, 0x40h 和 0x60 可以被正常使用了.

3) A000-BFFF RAM 存储体 00-03 或 RTC 寄存器 08-0C

读写区域. 具体是读写 RAM 还是 RTC 寄存器, 取决于当前卡带的 RAM Bank Number. 如果当前的 RAM Bank Number 小于等于 3, 则读写指定 RAM Bank Number 对应的 RAM 分组. 如果当前的 RAM Bank Number 属于 0x08-0x0c 范围, 则读写指定的 RTC 寄存器. RTC 寄存器详细规范将在后文进行介绍.

4) 0000-1FFF RAM/RTC 启用/禁用标志

只写区域. 启用或禁用外部 RAM 与 RTC. 写入 0x0a 启用外部 RAM 与 RTC, 其余情况则禁用它们.

5) 2000-3FFF ROM Bank Number

只写区域. 与 MBC1 类似, 只是 ROM Bank Number 将取写入值的后 7 位而不是后 5 位, 因此存储体的数量范围扩大到 0x00 到 0x7f. 注意当写入值是 0x00 时, 则替换为 0x01.

6) 4000-5FFF RAM Bank Number

只写区域. 写入值的后 2 位(范围 0x00-0x03)将作为卡带当前的 RAM Bank Number.

7) 6000-7FFF 锁存时钟数据

只写区域. 首先向该地址区域写入 0x00, 然后写入 0x01, 当前的时间流逝量将被锁存到 RTC 寄存器中. 通过重复写入 0x00 -> 0x01 这个过程, 可以修改 RTC 寄存器中锁存的时间. 注意, 如果重复写入 0x01 并不会改变锁存的时间值.

# RTC 寄存器

RTC 模块包含 5 个寄存器: 秒寄存器, 分寄存器, 小时寄存器, 日寄存器和标志寄存器. 它记录了自上一次复位以来, 总共流逝了多少时间. 各个寄存器所处地址与其说明如下所示.

```
0x08  RTC S   Seconds   0-59 (0-3Bh)
0x09  RTC M   Minutes   0-59 (0-3Bh)
0x0A  RTC H   Hours     0-23 (0-17h)
0x0B  RTC DL  Lower 8 bits of Day Counter (0-FFh)
0x0C  RTC DH  Upper 1 bit of Day Counter, Carry Bit, Halt Flag
    Bit 0  Most significant bit of Day Counter (Bit 8)
    Bit 6  Halt (0=Active, 1=Stop Timer)
    Bit 7  Day Counter Carry Bit (1=Counter Overflow)
```

正常情况下, 在写入 RTC 寄存器之前应该先置位 Halt(0x0c 寄存器的第 6 位)中断 RTC 的执行, 写入完成后再重置 Halt.

Day Counter(日计数器)总共有 9 位, 包括 0x0b 寄存器本身 8 位与 0x0c 寄存器第 0 位. 它允许计算 0-511(0x0000-0x01ff)范围内的天数. 当此值溢出时, 日计数器进位位(0x0c 寄存器第 7 位)置 1. 在这种情况下, 进位位保持置位状态, 直到程序重置它为止.

# 代码实现

首先需要实现 RTC 的仿真. 要注意, RTC 同 RAM 一样, 需要在仿真器关闭的时候写数据到本地文件, 然后再在仿真器启动的时候进行加载以保持时间的连贯性. 为了获取"流逝的时间", 在仿真实现上会稍微做一些小 trick, zero 字段保存系统的 timestamp, 这样当需要取得"流逝的时间"时, 只需要将当前的 timestamp 减去之前存储在 zero 字段的值即可.

```rs
struct RealTimeClock {
    s: u8,
    m: u8,
    h: u8,
    dl: u8,
    dh: u8,
    zero: u64,
    sav_path: PathBuf,
}

impl RealTimeClock {
    fn power_up(sav_path: impl AsRef<Path>) -> Self {
        let zero = match std::fs::read(sav_path.as_ref()) {
            Ok(ok) => {
                let mut b: [u8; 8] = Default::default();
                b.copy_from_slice(&ok);
                u64::from_be_bytes(b)
            }
            Err(_) => SystemTime::now()
                .duration_since(SystemTime::UNIX_EPOCH)
                .unwrap()
                .as_secs(),
        };
        Self {
            zero,
            s: 0,
            m: 0,
            h: 0,
            dl: 0,
            dh: 0,
            sav_path: sav_path.as_ref().to_path_buf(),
        }
    }

    fn tic(&mut self) {
        let d = SystemTime::now()
            .duration_since(SystemTime::UNIX_EPOCH)
            .unwrap()
            .as_secs()
            - self.zero;

        self.s = (d % 60) as u8;
        self.m = (d / 60 % 60) as u8;
        self.h = (d / 3600 % 24) as u8;
        let days = (d / 3600 / 24) as u16;
        self.dl = (days % 256) as u8;
        match days {
            0x0000..=0x00ff => {}
            0x0100..=0x01ff => {
                self.dh |= 0x01;
            }
            _ => {
                self.dh |= 0x01;
                self.dh |= 0x80;
            }
        }
    }
}
```

为 RTC 实现 Memory 泛型, 使得 CPU 可以通过内存地址读写这个对象. 读写规则可参照前文"RTC 寄存器"一节.

```rs
impl Memory for RealTimeClock {
    fn get(&self, a: u16) -> u8 {
        match a {
            0x08 => self.s,
            0x09 => self.m,
            0x0a => self.h,
            0x0b => self.dl,
            0x0c => self.dh,
            _ => panic!("No entry"),
        }
    }

    fn set(&mut self, a: u16, v: u8) {
        match a {
            0x08 => self.s = v,
            0x09 => self.m = v,
            0x0a => self.h = v,
            0x0b => self.dl = v,
            0x0c => self.dh = v,
            _ => panic!("No entry"),
        }
    }
}
```

为 RTC 实现 Stable 泛型, 使得其在仿真器关闭时可写入数据到文件.

```rs
impl Stable for RealTimeClock {
    fn sav(&self) {
        if self.sav_path.to_str().unwrap().is_empty() {
            return;
        }
        File::create(self.sav_path.clone())
            .and_then(|mut f| f.write_all(&self.zero.to_be_bytes()))
            .unwrap()
    }
}
```

接着再实现 MBC3 的完整仿真, 它同样与之前的 MBC1 或 MBC2 非常类似. 定义 MBC1 结构体, 其成员包括 ROM, RAM, RTC, 各个前文介绍的寄存器和 sav_path.

```rs
pub struct Mbc3 {
    rom: Vec<u8>,
    ram: Vec<u8>,
    rtc: RealTimeClock,
    rom_bank: usize,
    ram_bank: usize,
    ram_enable: bool,
    sav_path: PathBuf,
}

impl Mbc3 {
    pub fn power_up(rom: Vec<u8>, ram: Vec<u8>, sav: impl AsRef<Path>, rtc: impl AsRef<Path>) -> Self {
        Self {
            rom,
            ram,
            rtc: RealTimeClock::power_up(rtc),
            rom_bank: 1,
            ram_bank: 0,
            ram_enable: false,
            sav_path: PathBuf::from(sav.as_ref()),
        }
    }
}
```

为 MBC3 实现 Memory 泛型, 使得 CPU 可以通过内存地址读写这个对象. 读写规则可参照前文"MBC3 地址空间划分"一节.

```rs
impl Memory for Mbc3 {
    fn get(&self, a: u16) -> u8 {
        match a {
            0x0000..=0x3fff => self.rom[a as usize],
            0x4000..=0x7fff => {
                let i = self.rom_bank * 0x4000 + a as usize - 0x4000;
                self.rom[i]
            }
            0xa000..=0xbfff => {
                if self.ram_enable {
                    if self.ram_bank <= 0x03 {
                        let i = self.ram_bank * 0x2000 + a as usize - 0xa000;
                        self.ram[i]
                    } else {
                        self.rtc.get(self.ram_bank as u16)
                    }
                } else {
                    0x00
                }
            }
            _ => 0x00,
        }
    }

    fn set(&mut self, a: u16, v: u8) {
        match a {
            0xa000..=0xbfff => {
                if self.ram_enable {
                    if self.ram_bank <= 0x03 {
                        let i = self.ram_bank * 0x2000 + a as usize - 0xa000;
                        self.ram[i] = v;
                    } else {
                        self.rtc.set(self.ram_bank as u16, v)
                    }
                }
            }
            0x0000..=0x1fff => {
                self.ram_enable = v & 0x0f == 0x0a;
            }
            0x2000..=0x3fff => {
                let n = (v & 0x7f) as usize;
                let n = match n {
                    0x00 => 0x01,
                    _ => n,
                };
                self.rom_bank = n;
            }
            0x4000..=0x5fff => {
                let n = (v & 0x0f) as usize;
                self.ram_bank = n;
            }
            0x6000..=0x7fff => {
                if v & 0x01 != 0 {
                    self.rtc.tic();
                }
            }
            _ => {}
        }
    }
}
```

最后, 为 MBC3 实现 Stable 泛型. 当调用 sav 函数时, 除了保存 MBC3 RAM 中的内容外, 还需要同时调用 RTC 的 sav 函数以保存 RTC 中的内容.

```rs
impl Stable for Mbc3 {
    fn sav(&self) {
        rog::debugln!("Ram is being persisted");
        self.rtc.sav();
        if self.sav_path.to_str().unwrap().is_empty() {
            return;
        }
        File::create(self.sav_path.clone())
            .and_then(|mut f| f.write_all(&self.ram))
            .unwrap();
    }
}
```
