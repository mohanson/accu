# ROM Only

不超过 32KB 的小型游戏不需要使用 MBC 芯片: 因为它已经可以完整的映射到系统地址空间了. 此种情况下 ROM 被直接映射到 0x0000-0x7fff系统地址空间. 同时如果卡带支持的话, 可选择在 0xa000-0xbfff 系统地址空间上连接多达 8KB 的 RAM. 该类 ROM 通常用作发布会上的技术演示和 DEMO 之用, 比如进行 3D 画面的技术展示, 声音和音效展示等. 下图所示的《3D Wireframe Demo》和《175 Sprite Parallax Starfield Demo》皆曾被用于 Game Boy 的技术演示, 前者演示了一个会随时间改变颜色和空间位置的三维的方形, 后者则是拥有4 个图层, 动态的背景星空与前景漂浮文字的动画.

![img](/img/gameboy/cartridge/rom_only/3d_wireframe_demo.png)

![img](/img/gameboy/cartridge/rom_only/175_sprite_parallax_starfield_demo.png)

ROM Only 芯片的模拟实现是如此之简单以至于此时并不需要花太大力气. 但为了保证扩展性, 下面的代码会使用一些 Rust 高级用法: 泛型. 首先定义一个 Memory 泛型, 它拥有非常简单的 get 与 set 方法, 表示从一个存储(ROM 或 RAM)中读取一 Byte 数据, 或写入一 Byte 数据到存储.

```rs
pub trait Memory {
    fn get(&self, a: u16) -> u8;

    fn set(&mut self, a: u16, v: u8);
}
```

之后开始完善 ROM Only 的代码. 由于ROM Only 卡带是只读的, 因此, 可以忽略 Memory 泛型的 set 方法.

```rs
pub struct RomOnly {
    rom: Vec<u8>,
}

impl RomOnly {
    pub fn power_up(rom: Vec<u8>) -> Self {
        RomOnly { rom }
    }
}

impl Memory for RomOnly {
    fn get(&self, a: u16) -> u8 {
        self.rom[a as usize]
    }

    fn set(&mut self, _: u16, _: u8) {}
}
```

RomOnly 的 rom 字段存储 ROM 文件的原始数据, 同时该结构体使用了一个名叫 "power_up" 的函数(而不是 "new")作为结构体的初始化方法. 之所以如此是希望名字 power_up(通电) 能确切地让读者产生"我们在实现硬件仿真器"的感觉. 以后的代码也将遵从该设计理念, 即代码向硬件靠拢.

初始化 RomOnly 结构体的方式也非常简单: 从本地磁盘读取 ROM 文件的全部数据, 并传入 power_up 函数的第一个参数即可.

```rs
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cart = RomOnly::power_up(std::fs::read("3D.gb")?);
    println!("{:?}", cart.get(0));
    Ok(())
}
```

如此, Rom Only 类型的卡带的仿真实现便完成了.
