# GB/游戏卡带/MBC2

MBC2 拥有固定且自带的 512 x 4 Bits RAM 并同时支持最大 256 KB ROM. MBC2 与 MBC1 非常相似但更加的简单.

## MBC2 地址空间划分

MBC2 芯片将 Game Boy 分配给游戏卡带的系统地址空间 0x0000...0x7FFF 和 0xA000...0xBFFF 划分为以下几个独立区间, 详细介绍如下.

1) 0000-3FFF ROM 存储体 00

只读区域. 该区域总是映射到 ROM 的前 16 KB 字节物理存储.

2) 4000-7FFF ROM 存储体 01-0F

只读区域. 该区域可以映射为第 0x01 到 0x0F 编号的 ROM 存储体.

3) A000-A1FF 512 x 4 Bits RAM

读写区域. MBC2 芯片不支持外部 RAM, 作为替代的是内置的 512 x 4 Bits RAM. 这部分内置的 RAM 仍然需要外部电池来静态保存数据. 由于数据由 4 Bits 组成, 因此该存储区中只有每个字节的低 4 位才会被使用.

4) 0000-1FFF RAM 启用/禁用标志

只写区域. 用于启用或关闭 RAM. 只有高位地址字节的最低有效位为零才能启用/关闭 RAM. 例如, 向以下地址写入数据可用于启用/禁用 RAM：0x0000-0x00FF, 0x0200-0x02FF, 0x0400-0x04FF, ..., 0x1E00-0x1EFF. 当输入数据的低 4 位为 0b1010 时, 启用 RAM, 其余情况则禁用. 例如向 0x0000 写入 0x0A 可用于启用 RAM.

5) 2000-3FFF ROM Bank Number

只写区域. 向 0x2000-0x3FFF 写入的数值的低 4 位将作为当前的 ROM Bank Number. 但注意, 只有写入地址的高位字节的最低有效位为 1 才能正确写入. 例如, 向以下地址写入数据可用于选择 ROM Bank Number：0x2100-0x21FF, 0x2300-0x23FF, 0x2500-0x25FF, ..., 0x3F00-0x3FFF.

## 代码实现

MBC2 的代码仿真过程与 MBC1 十分相似, 甚至只是需要略微修改 MBC1 的代码即可

```rs
pub struct Mbc2 {
    rom: Vec<u8>,
    ram: Vec<u8>,
    rom_bank: usize,
    ram_enable: bool,
    sav_path: PathBuf,
}

impl Mbc2 {
    pub fn power_up(rom: Vec<u8>, ram: Vec<u8>, sav: impl AsRef<Path>) -> Self {
        Self {
            rom,
            ram,
            rom_bank: 1,
            ram_enable: false,
            sav_path: PathBuf::from(sav.as_ref()),
        }
    }
}

// 为 MBC2 实现 Memory 泛型, 使得 CPU 可以通过内存地址读写这个对象.
impl Memory for Mbc2 {
    fn get(&self, a: u16) -> u8 {
        match a {
            0x0000..=0x3fff => self.rom[a as usize],
            0x4000..=0x7fff => {
                let i = self.rom_bank * 0x4000 + a as usize - 0x4000;
                self.rom[i]
            }
            0xa000..=0xa1ff => {
                if self.ram_enable {
                    self.ram[(a - 0xa000) as usize]
                } else {
                    0x00
                }
            }
            _ => 0x00,
        }
    }

    fn set(&mut self, a: u16, v: u8) {
        // 只有低 4 位会被使用
        let v = v & 0x0f;
        match a {
            0xa000..=0xa1ff => {
                if self.ram_enable {
                    self.ram[(a - 0xa000) as usize] = v
                }
            }
            0x0000..=0x1fff => {
                if a & 0x0100 == 0 {
                    self.ram_enable = v == 0x0a;
                }
            }
            0x2000..=0x3fff => {
                if a & 0x0100 != 0 {
                    self.rom_bank = v as usize;
                }
            }
            _ => {}
        }
    }
}

impl Stable for Mbc2 {
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
