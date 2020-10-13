# MBC1

MBC1 是 Game Boy 的第一款 MBC 芯片. 任何后续的升级型 MBC 芯片其工作原理都与 MBC1 相似, 因此将游戏程序从一个 MBC1 芯片升级到另一个 MBC 芯片相对容易, 甚至可以使同一个游戏与几种不同类型的 MBC 兼容. MBC1 的内存是非平坦的, 它的程序指令和数据并不像 ROM Only 芯片一样被包含在相同的地址空间中.

# MBC1 地址空间划分

MBC1 芯片理论上最大可拥有 128 个 ROM 存储体, 每个 ROM 存储体大小是 16 KB; 同时拥有 4 个 RAM 存储体, 每个 RAM 存储体大小是 8 KB. MBC1 芯片将 Game Boy 分配给游戏卡带的系统地址空间 0x0000...0x7FFF 和 0xA000...0xBFFF 划分为以下几个独立区间, 详细介绍如下.

1) 0000-3FFF ROM 存储体 00

只读区域. 该区域总是映射到 ROM 的前 16 KB 字节物理存储, 也就是第一个 ROM 存储体.

2) 4000-7FFF ROM 存储体 01-7F

只读区域. 该区域可以映射为第 0x01 到 0x7F 编号的 ROM 存储体. 注意的是其中编号为 0x20, 0x40 与 0x60 的存储体不能被使用, 因此 MBC1 芯片实际上最大可支持 125 个 ROM 存储体, 最大数据存储容量为 125 * 16 KB ~= 2 MB.

MBC1 芯片内部拥有一个 Bank Number 寄存器来控制哪个存储体会被映射到此区域.

3) A000-BFFF RAM 存储体 00-03

读写区域. 该区域用于读写游戏卡带中的外部 RAM(如果有的话). 外部 RAM 通常需要使用电池做持久化存储, 允许存储游戏存档或历史高分列表. 即使关闭游戏机或者从游戏机中移除了卡带, RAM 中保存的数据依然不会丢失. 但如果卡带中的电池电量耗尽, 或者插拔了电池, 所有数据将化为乌有. 注意, 如果游戏卡带不支持外部 RAM 的话, 对此区域的任何读操作均返回 0x00 值.

4) 0000-1FFF RAM 启用/禁用标志

只写区域. 在试图读取或写入 RAM 之前, 必须通过在该地址空间写入特定值来启用外部 RAM. Game Boy 的游戏开发手册上建议游戏开发者在访问外部 RAM 后立即禁用外部 RAM, 以保护其内容免受游戏机断电期间的损坏. 通常使用以下值:

- 0x00: 禁用 RAM, 这是默认值.
- 0x0A: 启用 RAM.

实际上, 只要低 4 位是 0x0A 的任何值都会启用 RAM, 比如 0x1A, 0x2A 等, 而任何其它值都会禁用 RAM.

5) 2000-3FFF Bank Number 第 0-4 位

只写区域. 该区域被映射到 Bank Number 寄存器的第 0-4 位, 用于存储当前的 ROM Bank Number. 如果写入的值是 0x00, 由于第一个分组已经被永久映射到 0x0000-0x3FFF 地址区间, 因此 MBC1 将把 0x00 当作 0x01 处理. 同时, 当试图写入 0x20, 0x40 和 0x60 时也会发生同样的情况: MBC1 将把这些值翻译为 Bank 0x21, 0x41 和 0x61. 这就是为什么不存在编号为 0x20, 0x40 与 0x60 的 ROM 存储体的原因.

6) 4000-5FFF Bank Number 第 5-6 位

只写区域. 该区域被映射到 Bank Number 寄存器的第 5-6 位, 用于存储当前的 RAM Bank Number, 或者与 ROM Bank Number 组合成一个 7 位数字以完整表达 0x00-0x7F.

7) 6000-7FFF Bank 模式选择

只写区域. 该区域被映射到 Bank Number 寄存器的第 7 位, 用于表示当前的 Bank Number 应该被表达为 ROM Bank Number 还是 RAM Bank Number. 它只有两个可选值:

- 0x00 ROM Bank Number 模式, 默认
- 0x01 RAM Bank Number 模式

游戏程序可以在两种模式之间自由切换, 同时并不意味着使用了 ROM Bank Number 模式就无法再访问 RAM. 其唯一的限制是在 ROM 模式期间只能使用第一个 RAM 存储体, 相应的在 RAM 模式期间只能使用 ROM 存储体 0x00-0x1F.

# Bank Number 寄存器再探

Bank Number 寄存器的作用相对来讲不是那么容易理解, 我们可以辅助图形来加深理解. 我们已经知道: 一个完整的 Bank Number 寄存器可被表示为以下形式:

```no-highlight
Bank Mode   RAM Bank Bits   ROM Bank Bits
1 bit       2 bit           5 bit
```

当 Bank Mode 置为 0 时, 当前卡带为 ROM Bank Number 模式, 此时

- ROM Bank Number = RAM Bank Bits + ROM Bank Bits
- RAM Bank Number = 0x00

当 Bank Mode 置为 1 时, 当前卡带为 RAM Banking Mode 模式, 此时

- ROM Bank Number = ROM Bank Bits
- RAM Bank Number = RAM Bank Bits

# SRAM 的数据持久化

在真实的 Game Boy 卡带中, 外部 RAM , 也就是 MBC1 中系统地址为 0xA000-0xBFFF 的区间, 通常使用一块 3 V 的纽扣电池来保证数据不丢失. 对于这种构造的卡带, 可以使用一个新的名词来指代其外部 RAM: 静态随机存取存储器(Static Random Access Memory, SRAM). SRAM 是随机存取存储器的一种. 所谓的"静态", 是指这种存储器只要保持通电, 里面储存的数据就可以恒常保持. 相对之下, 动态随机存取存储器(DRAM)里面所储存的数据就需要周期性地更新. 然而, 当电力供应停止时, SRAM 储存的数据还是会消失(被称为 Volatile Memory), 这与在断电后还能储存资料的 ROM 或 Flash Memory 是不同的. Game Boy 游戏卡带的外部 RAM 绝大部分都是 SRAM.

在一般玩家的正常使用下, Game Boy 中的纽扣电池能保证持续放电 2 到 3 年, 因此可以保证卡带 2 年内不会掉档. 但也有例外, 比如在《精灵宝可梦》系列中, 卡带中额外存在一个时钟电路, 此时纽扣电池除了要供电 SRAM 还要供电时钟电路, 耗电量的增加导致了电池寿命的严重下降, 虽然现在不是很确定, 但在笔者幼时的印象中, 《精灵宝可梦》系列的游戏存档大概只能保持 1 年左右. 但令人苦恼的是, 许多游戏卡带为了防止纽扣电池接触不良造成意外的掉电, 会选择将电池焊在电路上的. 这意味着, 一旦电池电量耗尽, 玩家几乎无法自己手动更换它. 不过某些店主可能会感谢这种设计, 在笔者居住的小镇中就有一家提供电池更换服务的钟表店, 它在孩子们之间口口相传...

![img](/img/gameboy/cartridge/mbc1/battery.png)

回忆是美好的事情, 但现在必须将思绪拉回正题了. 我们要在仿真器上实现 SRAM! 我们无法仿真一块电池, 并且这个主意糟透了. 我们所需要做的事情并不困难:

- 在合适的时候, 将 RAM 中的所有内容写入到本地文件作为存档文件.
- 在仿真器启动的时候, 读取该存档文件中的内容到 RAM.

合适的写入时机有两个:

- 一是在关闭仿真器的时候.
- 二是在 RAM 启用/禁用标志从 True 转变为 False 的时候, 这意味着 CPU 已经完成了读取/改写 RAM 内容的工作.

两种选择各有优缺点. 第一种方式会在突然断电, 或者仿真器崩溃等异常情况下无法正常写入文件导致存档丢失; 第二种选择则是写文件的次数可能会过于频繁, 比如笔者在测试《精灵宝可梦-水晶》的时候发现每秒写文件的次数就达到了两位数(当然这和具体游戏有关, 有的游戏就非常节约). 关于时机的选择, 本书会使用第一种, 因为相对而言这样会使得代码结构更加清晰.

# 代码实现

万事具备! MBC1 游戏卡带的所有技术细节均已介绍完毕, 下面开始 MBC1 的仿真实现.

```rs
// 由于不是全部的卡带类型都带有 SRAM, 因此使用一个泛型 Stable 表示拥有 SRAM 的
// 卡带, Stable 泛型可以将游戏 卡带的内存数据以文件形式通过 sav 函数保存到本地
// 硬盘上.
pub trait Stable {
    fn sav(&self);
}

// MBC1 拥有两种 Bank Mode 类型, 因此在代码中使用一个枚举类型 BankMode 进行表
// 示.
enum BankMode {
    Rom,
    Ram,
}

// MBC1 主结构体.
pub struct Mbc1 {
    rom: Vec<u8>,
    ram: Vec<u8>,
    bank_mode: BankMode,
    bank: u8,
    ram_enable: bool,
    sav_path: PathBuf,
}

impl Mbc1 {
    pub fn power_up(rom: Vec<u8>, ram: Vec<u8>, sav: impl AsRef<Path>) -> Self {
        Mbc1 {
            rom,
            ram,
            bank_mode: BankMode::Rom,
            bank: 0x01,
            ram_enable: false,
            sav_path: PathBuf::from(sav.as_ref()),
        }
    }

    fn rom_bank(&self) -> usize {
        let n = match self.bank_mode {
            BankMode::Rom => self.bank & 0x7f,
            BankMode::Ram => self.bank & 0x1f,
        };
        n as usize
    }

    fn ram_bank(&self) -> usize {
        let n = match self.bank_mode {
            BankMode::Rom => 0x00,
            BankMode::Ram => (self.bank & 0x60) >> 5,
        };
        n as usize
    }
}

// 为 MBC1 实现 Memory 泛型, 使得 CPU 可以通过内存地址读写这个对象.
impl Memory for Mbc1 {
    fn get(&self, a: u16) -> u8 {
        match a {
            0x0000...0x3fff => self.rom[a as usize],
            0x4000...0x7fff => {
                let i = self.rom_bank() * 0x4000 + a as usize - 0x4000;
                self.rom[i]
            }
            0xa000...0xbfff => {
                if self.ram_enable {
                    let i = self.ram_bank() * 0x2000 + a as usize - 0xa000;
                    self.ram[i]
                } else {
                    0x00
                }
            }
            _ => 0x00,
        }
    }

    fn set(&mut self, a: u16, v: u8) {
        match a {
            0xa000...0xbfff => {
                if self.ram_enable {
                    let i = self.ram_bank() * 0x2000 + a as usize - 0xa000;
                    self.ram[i] = v;
                }
            }
            0x0000...0x1fff => {
                self.ram_enable = v & 0x0f == 0x0a;
                if !self.ram_enable {
                    self.sav();
                }
            }
            0x2000...0x3fff => {
                let n = v & 0x1f;
                let n = match n {
                    0x00 => 0x01,
                    _ => n,
                };
                self.bank = (self.bank & 0x60) | n;
            }
            0x4000...0x5fff => {
                let n = v & 0x03;
                self.bank = self.bank & 0x9f | (n << 5)
            }
            0x6000...0x7fff => match v {
                0x00 => self.bank_mode = BankMode::Rom,
                0x01 => self.bank_mode = BankMode::Ram,
                n => panic!("Invalid cartridge type {}", n),
            },
            _ => {}
        }
    }
}

// 最后, 为 MBC1 实现 Stable 泛型. 当调用 sav 函数时, 如果 sav_path 路径下已经
// 存在数据文件, 则覆盖旧的文件; 否则新建一个文件. 被保存的数据则是整个 RAM 中
// 存储的内容.
impl Stable for Mbc1 {
    fn sav(&self) {
        if self.sav_path.to_str().unwrap().is_empty() {
            return;
        }
        File::create(self.sav_path.clone())
            .and_then(|mut f| f.write_all(&self.ram))
            .unwrap()
    }
}
```
