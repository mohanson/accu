# GB/音频/频率扫描器

方波通道 1 具有一个频率扫描单元, 由寄存器 NR10 控制. 扫频器有一个定时器, 内部启用/禁用标志和影子寄存器(用于存储当前通道的频率). 扫频器的作用是定期向上或向下调整方波通道 1 的频率.

当扫频器被方波通道 1 触发工作时, 扫频器将完成以下几件事:

1. 方波通道 1 的当前频率被复制到扫频器的影子寄存器中
2. 扫频器的定时器重置
3. 如果扫描周期或移位(shift)值非零, 则设置启用标志, 否则禁用
4. 如果扫描移位非零, 则立即执行频率计算和溢出检查

频率计算包括获取影子寄存器中的值, 并通过扫频移位右移, 可选地取消该值, 并将其与影子寄存器相加以产生新频率. 对这个新频率所做的工作取决于具体情况.

溢出检查只是计算新频率, 如果大于 2047, 则禁用方波通道 1.

扫频器由序列发生器为其提供 128 Hz 时钟. 当它产生一个时钟信号并且内部启用/禁用标志为 1 且扫描周期不为零时, 将执行一次频率计算和溢出检查. 如果新频率小于等于 2047 且扫描移位不为零, 则将此新频率写回到影子频率和 NR13 和 NR14 寄存器中. 然后使用此新值立即执行频率计算和溢出检查, 但是得到的这第二个新频率不会被回写.

需要额外注意的有两点:

- 当扫描有效时, 可以通过 NR13 和 NR14 寄存器修改方波通道 1 的频率, 但其影子频率不会受到影响, 因此下次扫描更新通道的频率时, 此修改将丢失.
- 如果试图设置扫频器的周期为 0, 则以周期 8 替代.

扫频器会使用到寄存器中的以下几个函数

- get_frequency(): 获取当前的通道频率
- get_sweep_period(): 获取当前的扫频器的频率
- get_shift(): 获取当期的扫频器的移位值

## 代码实现

```rs
// The first square channel has a frequency sweep unit, controlled by NR10. This has a timer, internal enabled flag,
// and frequency shadow register. It can periodically adjust square 1's frequency up or down.
// During a trigger event, several things occur:
//
//   - Square 1's frequency is copied to the shadow register.
//   - The sweep timer is reloaded.
//   - The internal enabled flag is set if either the sweep period or shift are non-zero, cleared otherwise.
//   - If the sweep shift is non-zero, frequency calculation and the overflow check are performed immediately.
//
// Frequency calculation consists of taking the value in the frequency shadow register, shifting it right by sweep
// shift, optionally negating the value, and summing this with the frequency shadow register to produce a new
// frequency. What is done with this new frequency depends on the context.
//
// The overflow check simply calculates the new frequency and if this is greater than 2047, square 1 is disabled.
// The sweep timer is clocked at 128 Hz by the frame sequencer. When it generates a clock and the sweep's internal
// enabled flag is set and the sweep period is not zero, a new frequency is calculated and the overflow check is
// performed. If the new frequency is 2047 or less and the sweep shift is not zero, this new frequency is written back
// to the shadow frequency and square 1's frequency in NR13 and NR14, then frequency calculation and overflow check are
// run AGAIN immediately using this new value, but this second new frequency is not written back.
// Square 1's frequency can be modified via NR13 and NR14 while sweep is active, but the shadow frequency won't be
// affected so the next time the sweep updates the channel's frequency this modification will be lost.
struct FrequencySweep {
    reg: Rc<RefCell<Register>>,
    timer: Timer,
    enable: bool,
    shadow: u16,
    newfeq: u16,
}

impl FrequencySweep {
    fn power_up(reg: Rc<RefCell<Register>>) -> Self {
        Self {
            reg,
            timer: Timer::power_up(8),
            enable: false,
            shadow: 0x0000,
            newfeq: 0x0000,
        }
    }

    fn reload(&mut self) {
        self.shadow = self.reg.borrow().get_frequency();
        let p = self.reg.borrow().get_sweep_period();
        // The volume envelope and sweep timers treat a period of 0 as 8.
        self.timer.period = if p == 0 { 8 } else { u32::from(p) };
        self.enable = p != 0x00 || self.reg.borrow().get_shift() != 0x00;
        if self.reg.borrow().get_shift() != 0x00 {
            self.frequency_calculation();
            self.overflow_check();
        }
    }

    fn frequency_calculation(&mut self) {
        let offset = self.shadow >> self.reg.borrow().get_shift();
        if self.reg.borrow().get_negate() {
            self.newfeq = self.shadow.wrapping_sub(offset);
        } else {
            self.newfeq = self.shadow.wrapping_add(offset);
        }
    }

    fn overflow_check(&mut self) {
        if self.newfeq >= 2048 {
            self.reg.borrow_mut().set_trigger(false);
        }
    }

    fn next(&mut self) {
        if !self.enable || self.reg.borrow().get_sweep_period() == 0 {
            return;
        }
        if self.timer.next(1) == 0x00 {
            return;
        }
        self.frequency_calculation();
        self.overflow_check();

        if self.newfeq < 2048 && self.reg.borrow().get_shift() != 0 {
            self.reg.borrow_mut().set_frequency(self.newfeq);
            self.shadow = self.newfeq;
            self.frequency_calculation();
            self.overflow_check();
        }
    }
}
```
