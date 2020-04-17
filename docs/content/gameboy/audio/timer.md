# 512 Hz 时钟信号

Game Boy 内部存在一个 512 Hz 时钟信号, 用于向序列发生器(Frame Sequence)提供信号输入. 下面将在代码中实现该时钟信号.

```rs
struct ChannelSquare {}
struct ChannelWave {}
struct ChannelNoise {}

pub struct Apu {
    reg: Register,
    timer: Timer,
    channel1: ChannelSquare,
    channel2: ChannelSquare,
    channel3: ChannelWave,
    channel4: ChannelNoise,
}

impl Apu {
    pub fn power_up() -> Self {
        Self {
            reg: Register::power_up(Channel::Mixer),
            timer: Timer::power_up(4194304 / 512),
            channel1: ChannelSquare::power_up(),
            channel2: ChannelSquare::power_up(),
            channel3: ChannelWave::power_up(),
            channel4: ChannelNoise::power_up(),
        }
    }

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
        }
    }
}
```

结构体 Apu 是音频模块主要对外导出的结构类型, 它需要被嵌入内存管理模块上. 每当 CPU 执行完一条指令, CPU 通知音频模块该指令的执行周期, 这通过 next 函数完成. 由于 CPU 的时钟周期是 4194304, 因此为了获取 512 Hz 的时钟信号, 只需要每当 CPU 执行消耗 4194304/512 周期时产生一个新的信号即可. 在代码中表现来看, 将代码写入 "Your Codes" 代码块即可实现每秒执行指定代码 512 次.
