# GB/音频/音量包络

Game Boy 音频系统的核心本质是: 要想播放声音, 只要在特定的时间点向特定的寄存器写入特定的值. 换句话说, Game Boy 的 CPU 生成的信号是在时间-幅度坐标轴上离散的一系列点. 音量包络的作用便是平滑这些离散的点, 同时向其提供信号(音量)增益或衰减.

音量包络由序列发生器为其提供 64 Hz 时钟. 同时它内部存在一个计数器, 当时钟生成一个新的时钟信号并且音量包络的周期不为 0 时, 当前音量中将加上或减去(由 NRx2 设定)一个值来计算新音量, 同时计数器减 1. 如果此新音量在 0 到 15 范围内, 则音量会更新, 否则保持不变, 并且在再次触发通道之前不会对当前音量进行进一步的自动增加或减少.

需要特别注意的一点是, 如果音量包络中定时器的周期为 0, 则默认以周期 8 替代.

## 代码实现

与音量包络相关的寄存器数值有两个, 分别由寄存器的两个函数 get_period() 与 get_starting_volume() 指定, 代表计时器周期与音量包络的初始化音量大小.

```rs
struct VolumeEnvelope {
    reg: Rc<RefCell<Register>>,
    timer: Timer,
    volume: u8,
}

impl VolumeEnvelope {
    fn power_up(reg: Rc<RefCell<Register>>) -> Self {
        Self {
            reg,
            timer: Timer::power_up(8),
            volume: 0x00,
        }
    }

    fn reload(&mut self) {
        let p = self.reg.borrow().get_period();
        self.timer.period = if p == 0 { 8 } else { u32::from(p) };
        self.volume = self.reg.borrow().get_starting_volume();
    }

    fn next(&mut self) {
        if self.reg.borrow().get_period() == 0 {
            return;
        }
        if self.timer.next(1) == 0x00 {
            return;
        };
        // If this new volume within the 0 to 15 range, the volume is updated
        let v = if self.reg.borrow().get_envelope_add_mode() {
            self.volume.wrapping_add(1)
        } else {
            self.volume.wrapping_sub(1)
        };
        if v <= 15 {
            self.volume = v;
        }
    }
}
```
