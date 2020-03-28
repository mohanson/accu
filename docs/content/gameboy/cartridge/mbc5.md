# MBC5

MBC5 是在 Game Boy 游戏卡带技术发展末期推出的游戏卡带类型. 它的 ROM 容量达到了 8M, RAM 容量则是 128K. 它是历史上第二受开发者喜爱的 MBC 类型, 在总共 6000 余个 Game Boy 游戏中占比 45%, 第一名则是 MBC1, 占比高达 50%.

# MBC5 地址空间划分

MBC5 芯片将 Game Boy 分配给游戏卡带的系统地址空间 0x0000...0x7fff 和 0xa000...0xbfff 划分为以下几个独立区间, 详细介绍如下.

1) 0000-3FFF ROM 存储体 00

只读区域. 该区域总是映射到 ROM 的前 16KB 字节物理存储.

2) 4000-7FFF ROM 存储体 00-1FF

只读区域. 该区域可以映射为第 0x01 到 0x01ff 编号的 ROM 存储体.

3) A000-BFFF RAM 存储体 00-0F

读写区域. 该区域用于读写游戏卡带中的外部 RAM(如果有的话).

4) 0000-1FFF RAM 启用/禁用标志

只写区域. 逻辑与 MBC1 完全一致.

5) 2000-2FFF ROM Bank Number 的低 8 位

只写区域. 存储 ROM Bank Number 的低 8 位. 注意与其他 MBC 类型不同的是, 如果写入 0x00不会被自动转换成 0x01.

6) 3000-3FFF ROM Bank Number的第 9 位

只写区域. 存储 ROM Bank Number 的第 9 位. 只使用输入数据的最低位, 其它位的数据会被忽略.

7) 4000-5FFF RAM Bank Number

只写区域. 输入数据的低 4 位将作为当前的 RAM Bank Number.

# 代码实现

事实上 MBC5 的代码整体结构与其它 MBC 类型同样没有多大区别. 定义 MBC5 结构体, 其成员包括 ROM, RAM, 各个前文介绍的寄存器和 sav_path.

```rs
pub struct Mbc5 {
    rom: Vec<u8>,
    ram: Vec<u8>,
    rom_bank: usize,
    ram_bank: usize,
    ram_enable: bool,
    sav_path: PathBuf,
}

impl Mbc5 {
    pub fn power_up(rom: Vec<u8>, ram: Vec<u8>, sav: impl AsRef<Path>) -> Self {
        Self {
            rom,
            ram,
            rom_bank: 1,
            ram_bank: 0,
            ram_enable: false,
            sav_path: PathBuf::from(sav.as_ref()),
        }
    }
}
```

为 MBC5 实现 Memory 泛型, 使得 CPU 可以通过内存地址读写这个对象. 读写规则可参照前文"MBC5 地址空间划分"一节.

```rs
impl Memory for Mbc5 {
    fn get(&self, a: u16) -> u8 {
        match a {
            0x0000..=0x3fff => self.rom[a as usize],
            0x4000..=0x7fff => {
                let i = self.rom_bank * 0x4000 + a as usize - 0x4000;
                self.rom[i]
            }
            0xa000..=0xbfff => {
                if self.ram_enable {
                    let i = self.ram_bank * 0x2000 + a as usize - 0xa000;
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
            0xa000..=0xbfff => {
                if self.ram_enable {
                    let i = self.ram_bank * 0x2000 + a as usize - 0xa000;
                    self.ram[i] = v;
                }
            }
            0x0000..=0x1fff => {
                self.ram_enable = v & 0x0f == 0x0a;
            }
            0x2000..=0x2fff => self.rom_bank = (self.rom_bank & 0x100) | (v as usize),
            0x3000..=0x3fff => self.rom_bank = (self.rom_bank & 0x0ff) | (((v & 0x01) as usize) << 8),
            0x4000..=0x5fff => self.ram_bank = (v & 0x0f) as usize,
            _ => {}
        }
    }
}
```

最后, 为 MBC5 实现 Stable 泛型. 当调用 sav 函数时, 如果 sav_path 路径下已经存在数据文件, 则覆盖旧的文件; 否则新建一个文件. 被保存的数据则是整个 RAM 中存储的内容.

```rs
impl Stable for Mbc5 {
    fn sav(&self) {
        rog::debugln!("Ram is being persisted");
        if self.sav_path.to_str().unwrap().is_empty() {
            return;
        }
        File::create(self.sav_path.clone())
            .and_then(|mut f| f.write_all(&self.ram))
            .unwrap()
    }
}
```
