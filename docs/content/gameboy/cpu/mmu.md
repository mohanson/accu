# GB/CPU/内存管理单元与主板

内存管理单元(Memory Management Unit, MMU), 有时称作分页内存管理单元(Paged Memory Management Unit, PMMU). 它是一种负责处理中央处理器的内存访问请求的计算机硬件. 在 Game Boy 中, 它的功能主要是虚拟地址到物理地址的转换, 即虚拟内存管理.

Game Boy 供给 CPU 所使用的内存并不是一个简单的连续线性区域. Game Boy 通过内存管理单元的控制, 将不同的外部软硬件的存储空间拼接为一块连续的大小为 65536 的区域. 因此当 CPU 试图访问某个地址的内存数据时, 实际访问到的可能是某个外部硬件的存储空间, 比如游戏卡带中存储的数据.

CPU 可访问的所有区域与外部软硬件的映射关系如下：

|     地址      |                      说明                       |      备注      |
| ------------- | ----------------------------------------------- | -------------- |
| 0xffff        | Interrupt Enable Flag                           | 中断标志       |
| 0xff80-0xfffe | Zero Page - 127 bytes                           | 内存 HRAM      |
| 0xff00-0xff7f | Hardware I/O Registers                          | 硬件 IO        |
| 0xfea0-0xfeff | Unusable Memory                                 | 未使用         |
| 0xfe00-0xfe9f | OAM - Object Attribute Memory                   | GPU            |
| 0xe000-0xfdff | Echo RAM - Reserved, Do Not Use                 | WRAM           |
| 0xd000-0xdfff | Internal RAM - Bank 1-7 (switchable - CGB only) | 内存 WRAM      |
| 0xc000-0xcfff | Internal RAM - Bank 0 (fixed)                   | 内存 WRAM      |
| 0xa000-0xbfff | Cartridge RAM (If Available)                    | 卡带           |
| 0x9c00-0x9fff | BG Map Data 2                                   | GPU            |
| 0x9800-0x9bff | BG Map Data 1                                   | GPU            |
| 0x8000-0x97ff | Character RAM                                   | GPU            |
| 0x4000-0x7fff | Cartridge ROM - Switchable Banks 1-xx           | 卡带           |
| 0x0150-0x3fff | Cartridge ROM - Bank 0 (fixed)                  | 卡带           |
| 0x0100-0x014f | Cartridge Header Area                           | 卡带           |
| 0x0000-0x00ff | Restart and Interrupt Vectors                   | 重启和中断向量 |

可看到整个可索引内存区域被不同的软硬件分割, 这里需要特别注意一点的是 0xff00-0xff7f 区域, 该部分内存通常用于处理硬件的 IO, 常见的比如游戏控制器的输入, 音量调节按钮, 屏幕亮度调节按钮等外部输入. CPU 通过硬件中断来处理这些外部输入并给出反馈, 因此才使得计算机表现出可交互性.

内存管理单元的代码实现较为简单, 此处会给出一个大致框架, 但由于此时除 CPU 与卡带模块外并没有实现其余功能模块, 因此代码中在涉及这些未实现的模块时会预留空位. 一但这些模块被实现就可以立即加入这个框架.

```rs
pub struct Mmunit {
    pub cartridge: Box<Cartridge>, // 卡带
    pub apu: Option<Apu>,          // 音频 APU
    pub gpu: Gpu,                  // 视频 GPU
    pub joypad: Joypad,            // 控制器
    pub serial: Serial,            // 串行通行, 负责与其他 Game Boy 交换数据
    pub shift: bool,               // 与 speed 一起处理运行速度(单/双倍速)
    pub speed: Speed,              // 与 shift 一起处理运行速度(单/双倍速)
    pub term: Term,                // 游戏机型号
    pub timer: Timer,              // 定时器
    inte: u8,                      // 与 intf 一起处理中断
    intf: Rc<RefCell<Intf>>,       // 与 inte 一起处理中断
    hdma: Hdma,                    // 视频 GPU 的一部分
    hram: [u8; 0x7f],              // 视频 GPU 的一部分
    wram: [u8; 0x8000],            // 与 wram_bank 一起管理内部内存
    wram_bank: usize,              // 与 wram 一起管理内部内存
}
```

同时内存管理单元统一对外提供 0x0000-0xffff 范围的内存读写. 现在可暂时忽略每个内存区间的读写逻辑, 而只需要关心内存范围地址所对应的软硬件模块即可. 由于 Cartridge 模块现已实现, 因此 Cartridge 可以嵌入到 MMU 内了.

```rs
impl Memory for Mmunit {
    fn get(&self, a: u16) -> u8 {
        match a {
            0x0000...0x7fff => self.cartridge.get(a),                     // Cartridge
            0x8000...0x9fff => unimplement!(),                            // GPU
            0xa000...0xbfff => self.cartridge.get(a),                     // Cartridge
            0xc000...0xcfff => unimplement!(),                            // WRAM
            0xd000...0xdfff => unimplement!(),                            // WRAM
            0xe000...0xefff => unimplement!(),                            // WRAM
            0xf000...0xfdff => unimplement!(),                            // WRAM
            0xfe00...0xfe9f => unimplement!(),                            // GPU
            0xfea0...0xfeff => unimplement!(),                            // Unused
            0xff00 => unimplement!(),                                     // Joypad
            0xff01...0xff02 => unimplement!(),                            // Serial
            0xff04...0xff07 => unimplement!(),                            // Timer
            0xff0f => unimplement!(),                                     // Interrupt
            0xff10...0xff3f => unimplement!(),                            // APU
            0xff4d => unimplement!(),                                     // Speed
            0xff40...0xff45 | 0xff47...0xff4b | 0xff4f => unimplement!(), // GPU
            0xff51...0xff55 => unimplement!(),                            // HDMA
            0xff68...0xff6b => unimplement!(),                            // GPU
            0xff70 => unimplement!(),                                     // WRAM
            0xff80...0xfffe => unimplement!(),                            // HRAM
            0xffff => unimplement!(),                                     // Interrupe
            _ => 0x00,
        }
    }

    fn set(&mut self, a: u16, v: u8) {
        match a {
            0x0000...0x7fff => self.cartridge.set(a, v),                  // Cartridge
            0x8000...0x9fff => unimplement!(),                            // GPU
            0xa000...0xbfff => self.cartridge.set(a, v),                  // Cartridge
            0xc000...0xcfff => unimplement!(),                            // WRAM
            0xd000...0xdfff => unimplement!(),                            // WRAM
            0xe000...0xefff => unimplement!(),                            // WRAM
            0xf000...0xfdff => unimplement!(),                            // WRAM
            0xfe00...0xfe9f => unimplement!(),                            // GPU
            0xfea0...0xfeff => unimplement!(),                            // Unused
            0xff00 => unimplement!(),                                     // Joypad
            0xff01...0xff02 => unimplement!(),                            // Serial
            0xff04...0xff07 => unimplement!(),                            // Timer
            0xff0f => unimplement!(),                                     // Interrupt
            0xff10...0xff3f => unimplement!(),                            // APU
            0xff4d => unimplement!(),                                     // Speed
            0xff40...0xff45 | 0xff47...0xff4b | 0xff4f => unimplement!(), // GPU
            0xff51...0xff55 => unimplement!(),                            // HDMA
            0xff68...0xff6b => unimplement!(),                            // GPU
            0xff70 => unimplement!(),                                     // WRAM
            0xff80...0xfffe => unimplement!(),                            // HRAM
            0xffff => unimplement!(),                                     // Interrupe
            _ => 0x00,
        }
    }
}
```

还记得 CPU 的 power_up 函数吗？在初始化 CPU 时, 需要将 MMU 作为第二个参数传入即可完成对 CPU 的初始化. 这样, CPU 所访问的系统内存实质上就分布在卡带、GPU、游戏手柄等多个设备上了.

```rs
impl Cpu {
    pub fn power_up(term: Term, mem: Rc<RefCell<dyn Memory>>) -> Self {
        ...
    }
}
```

## 主板

CPU, 硬盘, 网卡, 外设, 无论是什么硬件设备, 都要插在计算机主板上, 可见主板对计算机系统来说是多么重要. 通常而言, 主板的升级换代是跟着 CPU 的升级换代而来的, 由于主板上的芯片组需要配合 CPU 进行协同工作, 同时又要配合许多新技术, 新技能和新外设, 因此从某一方面来说, 主板的发展可以代表计算机的发展. 主板与 CPU 有显著的不同, 每一代 CPU 的进化都有迹可循, 其继承自谁, 优化了什么地方等, 但每一代主板都几乎是重新设计的.

Game Boy 的主板结构经过简化, 可以用下示的结构图来表示：

![img](/img/gameboy/cpu/mmu/mb_struct.png)

由于 MMU 管理着全部的外部硬件, 且 CPU 只与 MMU 进行通信, 因此目前来讲, 主板的代码实现上只有两个成员. 在后面的章节中, 会慢慢再为主板补充额外的代码.

```rs
use super::cpu::Rtc;
use super::mmunit::Mmunit;
use std::cell::RefCell;
use std::path::Path;
use std::rc::Rc;

pub struct MotherBoard {
    pub mmu: Rc<RefCell<Mmunit>>,
    pub cpu: Rtc,
}

impl MotherBoard {
    pub fn power_up(path: impl AsRef<Path>) -> Self {
        let mmu = Rc::new(RefCell::new(Mmunit::power_up(path)));
        let cpu = Rtc::power_up(mmu.borrow().term, mmu.clone());
        Self { mmu, cpu }
    }
}
```
