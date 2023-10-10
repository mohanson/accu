# GB/音频/混频器

混频器的功能是混合叠加 4 个通道的输出. 每个通道的输出在发送到左/右混频器之前需要经过一对额外的开关, 混频器只是将每个通道的输出电压叠加在一起. 这些左/右开关由 NR51 寄存器控制. 当开关关闭时, 混频器接收到 0 伏特的电压信号.

NR50 寄存器的 Vin L enable 与 Vin R enable 位控制来自卡带的 Vin 信号. 这允许游戏开发者在卡带上添加额外的声音硬件.

混合后的左/右信号将继续通过左/右主音量控制. 这些信号将被乘以(音量 + 1)后输出. 因此一个音量为 2 的通道在主音量为 7 的情况下听起来和一个音量为 15 的通道在主音量为 0 的情况下差不太多.

## 代码实现

混频器的实现最主要的部分是生成最终音频数据: 这些数据存储在 `buffer: Arc<Mutex<Vec<(f32, f32)>>>` 中. next 函数中处理了各个通道的长度计数器, 音量包络和扫频器的执行. mix 函数将各个通道的 blipbuf 数据合并叠加在一起称为一连串的 `(f32, f32)` 数据.

```rs
pub struct Apu {
    pub buffer: Arc<Mutex<Vec<(f32, f32)>>>,
    reg: Register,
    timer: Timer,
    fs: FrameSequencer,
    channel1: ChannelSquare,
    channel2: ChannelSquare,
    channel3: ChannelWave,
    channel4: ChannelNoise,
    sample_rate: u32,
}

impl Apu {
    pub fn power_up(sample_rate: u32) -> Self {
        let blipbuf1 = create_blipbuf(sample_rate);
        let blipbuf2 = create_blipbuf(sample_rate);
        let blipbuf3 = create_blipbuf(sample_rate);
        let blipbuf4 = create_blipbuf(sample_rate);
        Self {
            buffer: Arc::new(Mutex::new(Vec::new())),
            reg: Register::power_up(Channel::Mixer),
            timer: Timer::power_up(cpu::CLOCK_FREQUENCY / 512),
            fs: FrameSequencer::power_up(),
            channel1: ChannelSquare::power_up(blipbuf1, Channel::Square1),
            channel2: ChannelSquare::power_up(blipbuf2, Channel::Square2),
            channel3: ChannelWave::power_up(blipbuf3),
            channel4: ChannelNoise::power_up(blipbuf4),
            sample_rate,
        }
    }

    fn play(&mut self, l: &[f32], r: &[f32]) {
        assert_eq!(l.len(), r.len());
        let mut buffer = self.buffer.lock().unwrap();
        for (l, r) in l.iter().zip(r) {
            // Do not fill the buffer with more than 1 second of data
            // This speeds up the resync after the turning on and off the speed limiter
            if buffer.len() > self.sample_rate as usize {
                return;
            }
            buffer.push((*l, *r));
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

            let step = self.fs.next();
            if step == 0 || step == 2 || step == 4 || step == 6 {
                self.channel1.lc.next();
                self.channel2.lc.next();
                self.channel3.lc.next();
                self.channel4.lc.next();
            }
            if step == 7 {
                self.channel1.ve.next();
                self.channel2.ve.next();
                self.channel4.ve.next();
            }
            if step == 2 || step == 6 {
                self.channel1.fs.next();
                self.channel1.timer.period = period(self.channel1.reg.clone());
            }

            self.channel1.blip.data.end_frame(self.timer.period);
            self.channel2.blip.data.end_frame(self.timer.period);
            self.channel3.blip.data.end_frame(self.timer.period);
            self.channel4.blip.data.end_frame(self.timer.period);
            self.channel1.blip.from -= self.timer.period;
            self.channel2.blip.from -= self.timer.period;
            self.channel3.blip.from -= self.timer.period;
            self.channel4.blip.from -= self.timer.period;
            self.mix();
        }
    }

    fn mix(&mut self) {
        let sc1 = self.channel1.blip.data.samples_avail();
        let sc2 = self.channel2.blip.data.samples_avail();
        let sc3 = self.channel3.blip.data.samples_avail();
        let sc4 = self.channel4.blip.data.samples_avail();
        assert_eq!(sc1, sc2);
        assert_eq!(sc2, sc3);
        assert_eq!(sc3, sc4);

        let sample_count = sc1 as usize;
        let mut sum = 0;

        let l_vol = (f32::from(self.reg.get_l_vol()) / 7.0) * (1.0 / 15.0) * 0.25;
        let r_vol = (f32::from(self.reg.get_r_vol()) / 7.0) * (1.0 / 15.0) * 0.25;

        while sum < sample_count {
            let buf_l = &mut [0f32; 2048];
            let buf_r = &mut [0f32; 2048];
            let buf = &mut [0i16; 2048];

            let count1 = self.channel1.blip.data.read_samples(buf, false);
            for (i, v) in buf[..count1].iter().enumerate() {
                if self.reg.nrx1 & 0x01 == 0x01 {
                    buf_l[i] += f32::from(*v) * l_vol;
                }
                if self.reg.nrx1 & 0x10 == 0x10 {
                    buf_r[i] += f32::from(*v) * r_vol;
                }
            }

            let count2 = self.channel2.blip.data.read_samples(buf, false);
            for (i, v) in buf[..count2].iter().enumerate() {
                if self.reg.nrx1 & 0x02 == 0x02 {
                    buf_l[i] += f32::from(*v) * l_vol;
                }
                if self.reg.nrx1 & 0x20 == 0x20 {
                    buf_r[i] += f32::from(*v) * r_vol;
                }
            }

            let count3 = self.channel3.blip.data.read_samples(buf, false);
            for (i, v) in buf[..count3].iter().enumerate() {
                if self.reg.nrx1 & 0x04 == 0x04 {
                    buf_l[i] += f32::from(*v) * l_vol;
                }
                if self.reg.nrx1 & 0x40 == 0x40 {
                    buf_r[i] += f32::from(*v) * r_vol;
                }
            }

            let count4 = self.channel4.blip.data.read_samples(buf, false);
            for (i, v) in buf[..count4].iter().enumerate() {
                if self.reg.nrx1 & 0x08 == 0x08 {
                    buf_l[i] += f32::from(*v) * l_vol;
                }
                if self.reg.nrx1 & 0x80 == 0x80 {
                    buf_r[i] += f32::from(*v) * r_vol;
                }
            }

            assert_eq!(count1, count2);
            assert_eq!(count2, count3);
            assert_eq!(count3, count4);

            self.play(&buf_l[..count1], &buf_r[..count1]);
            sum += count1;
        }
    }
}
```
