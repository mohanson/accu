# 定时器

当计算机诞生后, 人们除了期望它计算加减乘除外, 还希望做一些更复杂的事: 比如按照某固定频率刷新画面以显示动态画面, 当外接键盘时可以识别键盘按钮的长按或短按, 计算一个计算机程序的执行时间等. 这一切都需要根据定时器进行协调操作. 定时器的目的是允许事情在给定时刻或以特定速率发生.

在本节所说的定时器与视频模块, 音频模块或 MBC3 卡带中的定时器有些不一样: 此处的定时器是 Game Boy 机器的一等公民, 它直接与内存管理模块相连. 定时器会定期中断 CPU 的执行, 以使 Game Boy 的 CPU 以固定频率执行某些工作. Game Boy 中的定时器具有 4096, 16384, 65536 或 262144 Hz 的可选频率.

不过值得注意的是, 虽然本节的定时器功能强大以至于直接和内存管理模块相连, 但事实上大部分 Game Boy 的游戏都没有很好的使用到这个元件. 因为就如前文所说, 视频模块可以保持恒定的每秒 60 帧画面, 因此开发者更常常直接在画面刷新的间隙去插入需要定时执行的代码, 比如获取游戏手柄的输入并判断其是长按还是短按.

定时器的工作流程是以特定频率使定时器计数器(TIMA)递增, 当它溢出时, 产生一个 CPU 中断, 然后加载 Timer Modulo(TMA) 的内容. 具体而言, 它具有以下几个寄存器.

# 寄存器描述


| 名称 |  地址  |                                                                        描述                                                                        |
| ---- | ------ | -------------------------------------------------------------------------------------------------------------------------------------------------- |
| DIV  | 0xff04 | DIV(Divider Register) 寄存器以 16384Hz 的速率递增. 将任何值写入该寄存器会将其重置为 0x00.                                                          |
| TIMA | 0xff05 | TIMA(Timer counter). 定时器以 TAC 寄存器指定的时钟频率(0xff07)递增. 当值溢出（> 0xff）时, 它将被重置为 TMA（0xff06）中指定的值, 并将请求 CPU 中断. |
| TMA  | 0xff06 | TMA(Timer Modulo). 当 TIMA 溢出时, TIMA 将被重置为该寄存器中指定的值.                                                                              |
| TAC  | 0xff07 | TAC(Timer Control). 详见下文说明                                                                                                                   |

TAC(Timer Control) 寄存器被区分为两段数据:

|   位    |                说明                 |
| ------- | ----------------------------------- |
| Bit 2   | 定时器启用/禁用标志(1=启动, 0=禁用) |
| Bit 1-0 | 设定定时器的频率                    |

频率选择:

| 标志位 |                          频率                           |
| ------ | ------------------------------------------------------- |
| 00     | CPU Clock / 1024 (DMG, CGB:   4096 Hz, SGB:   ~4194 Hz) |
| 01     | CPU Clock / 16   (DMG, CGB: 262144 Hz, SGB: ~268400 Hz) |
| 10     | CPU Clock / 64   (DMG, CGB:  65536 Hz, SGB:  ~67110 Hz) |
| 11     | CPU Clock / 256  (DMG, CGB:  16384 Hz, SGB:  ~16780 Hz) |

# 代码实现

```rs
// Sometimes it's useful to have a timer that interrupts at regular intervals for routines that require periodic or
// percise updates. The timer in the GameBoy has a selectable frequency of 4096, 16384, 65536, or 262144 Hertz.
// This frequency increments the Timer Counter (TIMA). When it overflows, it generates an interrupt. It is then loaded
// with the contents of Timer Modulo (TMA).
//
// See: http://gbdev.gg8.se/wiki/articles/Timer_and_Divider_Registers
use super::intf::{Flag, Intf};
use std::cell::RefCell;
use std::rc::Rc;

pub struct Timer {
    // Each time when the timer overflows (ie. when TIMA gets bigger than FFh), then an interrupt is requested by
    // setting Bit 2 in the IF Register (FF0F). When that interrupt is enabled, then the CPU will execute it by calling
    // the timer interrupt vector at 0050h.
    intf: Rc<RefCell<Intf>>,

    // This register is incremented at rate of 16384Hz (~16779Hz on SGB). Writing any value to this register resets it
    // to 00h.
    // Note: The divider is affected by CGB double speed mode, and will increment at 32768Hz in double speed.
    div: u8,
    // This timer is incremented by a clock frequency specified by the TAC register ($FF07). When the value overflows
    // (gets bigger than FFh) then it will be reset to the value specified in TMA (FF06), and an interrupt will be
    // requested, as described below.
    tima: u8,
    // When the TIMA overflows, this data will be loaded.
    tma: u8,
    //  Bit  2   - Timer Enable
    //  Bits 1-0 - Input Clock Select
    //             00: CPU Clock / 1024 (DMG, CGB:   4096 Hz, SGB:   ~4194 Hz)
    //             01: CPU Clock / 16   (DMG, CGB: 262144 Hz, SGB: ~268400 Hz)
    //             10: CPU Clock / 64   (DMG, CGB:  65536 Hz, SGB:  ~67110 Hz)
    //             11: CPU Clock / 256  (DMG, CGB:  16384 Hz, SGB:  ~16780 Hz)
    tac: u8,

    freq: u32,
    // Count the number of cycles and set 0 each 256 cycles
    tmp1: u32,
    // Count the number of cycles and set 0 each "freq" cycles
    tmp2: u32,
}

impl Timer {
    pub fn power_up(intf: Rc<RefCell<Intf>>) -> Self {
        Timer {
            intf,
            div: 0x00,
            tima: 0x00,
            tma: 0x00,
            tac: 0x00,
            freq: 256,
            tmp1: 0x00,
            tmp2: 0x00,
        }
    }

    pub fn get(&self, a: u16) -> u8 {
        match a {
            0xff04 => self.div,
            0xff05 => self.tima,
            0xff06 => self.tma,
            0xff07 => self.tac,
            _ => panic!("Unsupported address"),
        }
    }

    pub fn set(&mut self, a: u16, v: u8) {
        match a {
            0xff04 => self.div = 0x00,
            0xff05 => self.tima = v,
            0xff06 => self.tma = v,
            0xff07 => {
                self.tac = v;
                match v & 0x03 {
                    0x00 => self.freq = 1024,
                    0x01 => self.freq = 16,
                    0x02 => self.freq = 64,
                    0x03 => self.freq = 256,
                    _ => panic!(""),
                };
            }
            _ => panic!("Unsupported address"),
        }
    }

    pub fn next(&mut self, cycles: u32) {
        // Increment div at rate of 16384Hz. Because the clock cycles is 4194304, so div increment every 256 cycles.
        let c = 256;
        self.tmp1 += cycles;
        if self.tmp1 >= c {
            self.div = self.div.wrapping_add(1);
            self.tmp1 -= c;
        }

        // Increment tima at rate of Clock / freq
        if (self.tac & 0x04) != 0x00 {
            self.tmp2 += cycles;
            while self.tmp2 >= self.freq {
                self.tima = self.tima.wrapping_add(1);
                if self.tima == 0x00 {
                    self.tima = self.tma;
                    self.intf.borrow_mut().hi(Flag::Timer);
                }
                self.tmp2 -= self.freq;
            }
        }
    }
}
```
