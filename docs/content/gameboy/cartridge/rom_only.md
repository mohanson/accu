# GB/游戏卡带/ROM only

不超过 32 KB 的小型游戏不需要使用 MBC 芯片: 因为它已经可以完整的映射到系统地址空间了. 此种情况下 ROM 被直接且完整的映射到 0x0000-0x7FFF 系统地址空间. 同时如果卡带支持的话, 可选择在 0xA000-0xBFFF 系统地址空间上额外连接多达 8 KB 的 RAM. 该类型的 ROM 通常用作发布会上的技术演示和 Demo 之用, 比如可以进行包括 3D 画面的技术, 声音和音效演示. 下图所示的《3D Wireframe Demo》和《175 Sprite Parallax Starfield Demo》皆曾被用于此种用途, 前者演示了一个会随时间改变颜色和空间位置的三维的方形, 后者则是一个拥有4 个图层, 动态的背景星空与前景漂浮文字的动画.

![img](/img/gameboy/cartridge/rom_only/3d_wireframe_demo.png)

![img](/img/gameboy/cartridge/rom_only/175_sprite_parallax_starfield_demo.png)

我们会用一点简单的代码来对 ROM Only 芯片进行仿真. 为了保证扩展性, 下面的代码会使用一些 Rust 高级用法: 泛型. 首先我们定义一个 Memory 泛型, 它拥有非常简单的 get 与 set 方法, 用以表示从一个地址中读取 1 Byte 的数据, 或写入 1 Byte 数据到一个地址. 在之后的代码种, ROM Only 卡带的仿真代码将实现这个泛型, 并且除 ROM Only 之外, MBC1, MBC2, MBC3 和 MBC5 的仿真代码也都将这么做.

```rs
pub trait Memory {
    fn get(&self, a: u16) -> u8;

    fn set(&mut self, a: u16, v: u8);
}
```

我们开始完善 ROM Only 的代码. 由于 ROM Only 卡带是只读的, 因此, 可以安全的忽略 Memory 泛型的 set 方法. 当然一种更好的方式是在 set 函数中引发一个异常(对于大多数人来说, 我不确定...), 但是正如我时常说的, 只要你相信自己的代码, 你的代码就会回应你, 因此放心大胆的移除你确认不会被执行到的异常处理代码吧!

```rs
pub struct RomOnly {
    // ROM 文件的二进制数据
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

    fn set(&mut self, _: u16, _: u8) {
        // 该函数永远不会被执行
    }
}
```

RomOnly 的 rom 字段存储 ROM 文件的原始数据, 大多数情况下它从文件中读取而来. 同时该结构体使用了一个名为 "power_up(通电)" 的函数作为结构体的初始化方法, 而非大多数情况下采用的 "new". 之所以如此设计名字, 是希望名字 power_up 能确切地让读者产生"我们在实现硬件仿真器"的感觉. 以后的代码也将遵从该设计理念, 即尽量让代码向硬件靠拢.

下面的代码演示了如何从本地磁盘读取 ROM 文件并初始化 RomOnly 结构体.

```rs
fn main() -> Result<(), Box<dyn std::error::Error>> {
    let cart = RomOnly::power_up(std::fs::read("3D.gb")?);
    println!("{:?}", cart.get(0));
    Ok(())
}
```

如此, Rom Only 类型的卡带的仿真实现便完成了. 希望你可以在此时惊呼"这太简单了!", 没错, 任何复杂深奥的技术背后，都可以分解为可简单处理的基本单元.
