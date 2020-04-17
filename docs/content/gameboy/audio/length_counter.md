# 长度计数器

长度计数器(Length Counter)在递减到零时禁用对应的音频通道. 它包含一个内部计数器和启用/禁用标志. 向 NRx1 寄存器写入一个字节会初始化或重载长度计数器的计数. Wave 通道使用全部 8 个 Bit 位, 而其他通道只使用低 6 个 Bit 位, 因此对于 Wave 通道而言, 其计数范围是 0 - 255, 其他通道则是 0 - 63. 如果向 NRx1 重复写入数据, 计数器将被重新加载为最后一次写入的数值.

当内部启用/禁用标志置零时, 通道将被禁用. 禁用通道时, 该通道的音量包络将接收到 0 值输入, 因此最终通道输出为 0 值, 即没有声音. 除长度计数器之外的其他内部单元也可以启用/禁用通道.

每个长度计数器由序列发生器以 256 Hz 的频率计时. 长度计数器除了以固定频率递减外, 还会被 NRx4 额外触发: 当写入 NRx4 且 NRx4 的最高位为 1 时, 如果长度计数器不为 0, 则递减 1. 如果它在执行完减法后变为 0, 同样会禁用该音频通道. 如果长度计数器在此种情形下成功降为 0, 则为其赋值为 256 或 64: 这取决于该音频通道是否是 Wave 通道.

# 代码实现

```rs
struct LengthCounter {
    reg: Rc<RefCell<Register>>,
    n: u16,
}

impl LengthCounter {
    fn power_up(reg: Rc<RefCell<Register>>) -> Self {
        Self { reg, n: 0x0000 }
    }

    fn next(&mut self) {
        if self.reg.borrow().get_length_enable() && self.n != 0 {
            self.n -= 1;
            if self.n == 0 {
                self.reg.borrow_mut().set_trigger(false);
            }
        }
    }

    fn reload(&mut self) {
        if self.n == 0x0000 {
            self.n = if self.reg.borrow().channel == Channel::Wave {
                1 << 8
            } else {
                1 << 6
            };
        }
    }
}
```
