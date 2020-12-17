# GB/音频/序列发生器

序列器发生器(Frame Sequencer)为调制单元生成低频时钟. 它由 512 Hz 的定时器提供时钟控制. 序列发生器间接接受 CPU 时钟输入, 它有点类似于一个入口函数, 基本上音频模块的所有逻辑都经由它的运作而触发.

序列器发生器在不同时间分片下触发不同的硬件单元:

```no-highlight
Step   Length Ctr  Vol Env     Sweep
---------------------------------------
0      Clock       -           -
1      -           -           -
2      Clock       -           Clock
3      -           -           -
4      Clock       -           -
5      -           -           -
6      Clock       -           Clock
7      -           Clock       -
---------------------------------------
Rate   256 Hz      64 Hz       128 Hz
```

由上表可知长度计数器(Length Ctr)的频率时 256 Hz, 音量包络(Vol Env)的频率是 64 Hz, 扫频器(Sweep)的频率是 128 Hz.

序列发生器的实现也非常简单, 基本上可看作一个周期固定为 8 的特殊定时器.

```rs
struct FrameSequencer {
    step: u8,
}

impl FrameSequencer {
    fn power_up() -> Self {
        Self { step: 0x00 }
    }

    fn next(&mut self) -> u8 {
        self.step += 1;
        self.step %= 8;
        self.step
    }
}
```

最后将 FrameSequencer 接入到 512 Hz 时钟信号, 并控制长度计数器, 音量包络和扫频器在 4 个音频通道中的运行. 注意目前并没有真的去实现这些逻辑硬件的代码, 它们仅仅在此处被占位.

```rs
impl Apu {
    pub fn next(&mut self, cycles: u32) {
        if !self.reg.get_power() {
            return;
        }

        for _ in 0..self.timer.next(cycles) {
            self.channel1.next(self.timer.period);
            self.channel2.next(self.timer.period);
            self.channel3.next(self.timer.period);
            self.channel4.next(self.timer.period);

            // 512 Hz 时钟信号
            //
            // ... Your Codes
            let step = self.fs.next();
            if step == 0 || step == 2 || step == 4 || step == 6 {
                // Length Ctr
                self.channel1.lc.next();
                self.channel2.lc.next();
                self.channel3.lc.next();
                self.channel4.lc.next();
            }
            if step == 7 {
                // Vol Env
                self.channel1.ve.next();
                self.channel2.ve.next();
                self.channel4.ve.next();
            }
            if step == 2 || step == 6 {
                // Sweep
                self.channel1.fs.next();
            }
        }
    }
}
```
