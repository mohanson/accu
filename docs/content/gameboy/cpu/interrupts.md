# GB/CPU/LR35902 中断

中断(Interrupt)是计算机科学中的一个术语, 指 CPU 接收到来自硬件或软件的事件信号. 来自硬件的中断称为硬件中断, 来自软件的中断称为软件中断.

在接收到来自外围硬件的异步信号, 或来自软件的同步信号之后, CPU 将会进行相应的硬件软件处理. 发出中断信号称为进行中断请求(Interrupt request, IRQ). 硬件中断将导致 CPU 通过一个运行时上下文切换来保存当前执行状态(以程序计数器和程序状态字等寄存器信息为主). 软件中断则通常作为 CPU 指令集中的一个指令, 以可编程的方式直接指示这种运行信息切换, 并将处理导向一段中断处理代码. 中断在计算机多任务处理, 尤其是即时系统中尤为有用. 这样的系统, 包括运行于其上的操作系统, 也被称为"中断驱动的"(interrupt-driven).

中断的几个要点:

- 中断请求来自中断源, 中断源通常是外围硬件. 中断不是"异常", 而是 CPU 正常处理过程一部分.
- CPU 接受中断请求后将执行该类型中断请求对应的中断服务程序(ISR).
- CPU 接受中断请求后将进行保留现场操作, 在执行完中断请求后执行恢复现场操作.
- 中断存在中断优先级的概念, 即当多个中断同时向处理器发出请求时, 处理器将对请求做优先级的排序.
- 中断可以存在/不存在嵌套, 即当 CPU 正在处理一个请求时接受到更高优先级的中断, CPU 可以选择"中断"当前的中断请求转而去执行更高优先级的中断请求.

LR35902 用于负责处理中断的组件包含 IME 标志, IE 寄存器和 IF 寄存器等, 现介绍如下.

## IME 标志, IE 与 IF 寄存器

在前面介绍标准指令集的小节中, 已经了解到有 3 个指令 EI(0xfb), DI(0xf3) 与 RETI(0xd9) 可以分别启用和禁用中断. CPU 通过 IME(interrupt master enable) 标志用来保存中断是否被禁用的信息: EI 指令使 IME 置位, DI 指令使 IME 置零.

CPU 内有两个寄存器参与中断的逻辑控制, 它们分别是 IE 与 IF, 其具体说明如下.

**IE**

IE(Interrupt Enable)寄存器映射至地址 0xffff, 它同样控制中断的启用或禁用, 但不同的是它只负责某一具体类型的中断, 与 IME 之间的区别类似总控开关与普通开关的区别. Game Boy 总共会产生 5 种不同类型的中断, 它们分别是:

- V-Blank
- LCD STAT
- Timer
- Serial
- Joypad

这些中断请求分别来自于不同的外围硬件: GPU, 内部定时器, 串行接口与手柄等. IE 寄存器的低 5 位控制这些中断请求的启用或禁用.

位  |   名称   |                 说明
--- | -------- | -------------------------------------
0   | V-Blank  | Interrupt Enable (INT 40h) (1=Enable)
1   | LCD STAT | Interrupt Enable (INT 48h) (1=Enable)
2   | Timer    | Interrupt Enable (INT 50h) (1=Enable)
3   | Serial   | Interrupt Enable (INT 58h) (1=Enable)
4   | Joypad   | Interrupt Enable (INT 60h) (1=Enable)

**IF**

IF(Interrupt Flag)寄存器映射至地址 0xff0f, 负责保存当前已经产生的中断请求.

位  |   名称   |                  说明
--- | -------- | ---------------------------------------
0   | V-Blank  | Interrupt Request (INT 40h) (1=Request)
1   | LCD STAT | Interrupt Request (INT 48h) (1=Request)
2   | Timer    | Interrupt Request (INT 50h) (1=Request)
3   | Serial   | Interrupt Request (INT 58h) (1=Request)
4   | Joypad   | Interrupt Request (INT 60h) (1=Request)

当外围硬件的中断信号从低电平变为高电平时, IF 寄存器中的相应位置位. 例如, 当 LCD 控制器进入 V-Blank 周期时, 第 0 位置位.

## 中断请求与执行

当中断请求发生时, IF 寄存器中的相应位置位. 只有当 IME 标志和 IE 寄存器中的相应位都置位时, 才会发生实际的中断执行, 否则中断请求将"等待"直到 IME 和 IE 都允许其执行.

当中断执行时, IF 寄存器中的相应位将由 CPU 自动复位, 并且 IME 标志变为清零状态(在程序重新启用中断之前, 通常使用 RETI 指令取消任何进一步的中断). CPU 将调用中断请求对应的中断向量(即 0x0040-0x0060 范围内的地址, 如上面的 IE 和 IF 寄存器描述所示).
在以下三种情况下, 可能会发生 IF 寄存器中多个位置位的情况, 即同时请求多个中断:

- 多个中断信号同时从低电平变为高电平
- 在一段事件内请求了多个中断, 但 IME/IE 寄存器不允许其立即执行
- 用户手动向 IF 寄存器写入值

如果 IME 和 IE 允许执行多个请求的中断, 则首先执行具有最高优先级的中断. 优先级按 IE 和 IF 寄存器中的位排序, 具有最高优先级的是位 0(V-Blank), 具有最低优先级的位 4(Joypad).

## 代码实现

定义一个枚举类型表示 5 种不同类型的中断:

```rs
pub enum Flag {
    VBlank  = 0,
    LCDStat = 1,
    Timer   = 2,
    Serial  = 3,
    Joypad  = 4,
}
```

定义 IF 寄存器如下. 当 IF 寄存器收到不同的中断时, 其特定位可以被置位.

```rs
pub struct Intf {
    pub data: u8,
}

impl Intf {
    pub fn power_up() -> Self {
        Self { data: 0x00 }
    }

    pub fn hi(&mut self, flag: Flag) {
        self.data |= 1 << flag as u8;
    }
}
```

为 CPU 实现中断处理逻辑. 中断处理函数返回 CPU 机器周期, 因为 LR35902 中断处理固定消费 4 个机器周期, 所以中断处理函数的返回值为 0 或 4 之一.

```rs
impl Cpu {
    fn hi(&mut self) -> u32 {
        if !self.halted && !self.ei {
            return 0;
        }
        let intf = self.mem.borrow().get(0xff0f);
        let inte = self.mem.borrow().get(0xffff);
        let ii = intf & inte;
        if ii == 0x00 {
            return 0;
        }
        self.halted = false;
        if !self.ei {
            return 0;
        }
        self.ei = false;

        // Consumer an interrupter, the rest is written back to the register
        let n = ii.trailing_zeros();
        let intf = intf & !(1 << n);
        self.mem.borrow_mut().set(0xff0f, intf);

        self.stack_add(self.reg.pc);
        // Set the PC to correspond interrupt process program:
        // V-Blank: 0x40
        // LCD: 0x48
        // TIMER: 0x50
        // JOYPAD: 0x60
        // Serial: 0x58
        self.reg.pc = 0x0040 | ((n as u16) << 3);
        4
    }
}
```

最后, 每当 CPU 执行指令之前都需要做一次中断判断, 因此在 next 函数内写入中断处理函数如下:

```rs
impl Cpu {
    pub fn next(&mut self) -> u32 {
        let mac = {
            let c = self.hi();
            if c != 0 {
                c
            } else if self.halted {
                OP_CYCLES[0]
            } else {
                self.ex()
            }
        };
        mac * 4
    }
}
```
