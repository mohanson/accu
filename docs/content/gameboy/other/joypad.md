# 游戏手柄

Game Boy 有一个内置的游戏手柄, 带有 8 个按钮. 有 4 个方向按钮(上, 下, 左和右)和 4 个标准按钮(开始, 选择, A 和 B).

这八个按钮共用一个寄存器, 位于内存地址 0xff00 处. 寄存器其分解方式如下.

# FF00 Joypad

|  位   |                        说明                         |
| ----- | --------------------------------------------------- |
| Bit 7 | Not used                                            |
| Bit 7 | Not used                                            |
| Bit 6 | Not used                                            |
| Bit 5 | P15 Select Button Keys      (0=Select)              |
| Bit 4 | P14 Select Direction Keys   (0=Select)              |
| Bit 3 | P13 Input Down  or Start    (0=Pressed) (Read Only) |
| Bit 2 | P12 Input Up    or Select   (0=Pressed) (Read Only) |
| Bit 1 | P11 Input Left  or Button B (0=Pressed) (Read Only) |
| Bit 0 | P10 Input Right or Button A (0=Pressed) (Read Only) |

仿真器将第 0-3 位设置为显示游戏手柄的状态. 如上所示, 方向按钮和标准按钮共享此位范围. 那么游戏假设当前第 3 位是 0, 那么游戏如何知道是方向向下按钮还是标准启动按钮? 这种情况下, 需要观察第 4-5 位, 它们可以告诉游戏开发者具体是哪个按钮被按下.

# 代码实现

```rs
// The eight gameboy buttons/direction keys are arranged in form of a 2x4 matrix. Select either button or direction
// keys by writing to this register, then read-out bit 0-3.
//
// FF00 - P1/JOYP - Joypad (R/W)
//
// Bit 7 - Not used
// Bit 6 - Not used
// Bit 5 - P15 Select Button Keys      (0=Select)
// Bit 4 - P14 Select Direction Keys   (0=Select)
// Bit 3 - P13 Input Down  or Start    (0=Pressed) (Read Only)
// Bit 2 - P12 Input Up    or Select   (0=Pressed) (Read Only)
// Bit 1 - P11 Input Left  or Button B (0=Pressed) (Read Only)
// Bit 0 - P10 Input Right or Button A (0=Pressed) (Read Only)
//
// Note: Most programs are repeatedly reading from this port several times (the first reads used as short delay,
// allowing the inputs to stabilize, and only the value from the last read actually used).
use super::intf::{Flag, Intf};
use super::memory::Memory;
use std::cell::RefCell;
use std::rc::Rc;

#[rustfmt::skip]
#[derive(Clone)]
pub enum JoypadKey {
    Right  = 0b0000_0001,
    Left   = 0b0000_0010,
    Up     = 0b0000_0100,
    Down   = 0b0000_1000,
    A      = 0b0001_0000,
    B      = 0b0010_0000,
    Select = 0b0100_0000,
    Start  = 0b1000_0000,
}

pub struct Joypad {
    intf: Rc<RefCell<Intf>>,
    matrix: u8,
    select: u8,
}

impl Joypad {
    pub fn power_up(intf: Rc<RefCell<Intf>>) -> Self {
        Self {
            intf,
            matrix: 0xff,
            select: 0x00,
        }
    }
}

impl Joypad {
    pub fn keydown(&mut self, key: JoypadKey) {
        self.matrix &= !(key as u8);
        self.intf.borrow_mut().hi(Flag::Joypad);
    }

    pub fn keyup(&mut self, key: JoypadKey) {
        self.matrix |= key as u8;
    }
}

impl Memory for Joypad {
    fn get(&self, a: u16) -> u8 {
        assert_eq!(a, 0xff00);
        if (self.select & 0b0001_0000) == 0x00 {
            return self.select | (self.matrix & 0x0f);
        }
        if (self.select & 0b0010_0000) == 0x00 {
            return self.select | (self.matrix >> 4);
        }
        self.select
    }

    fn set(&mut self, a: u16, v: u8) {
        assert_eq!(a, 0xff00);
        self.select = v;
    }
}
```

之后, 我们需要借助 minifb 库捕获用户的键盘输入, 并调用 Joypad 的 keydown 和 keyup 函数.

```rs
func main() {
    ......
    // Handling keyboard events
    if window.is_key_down(minifb::Key::Escape) {
        break;
    }
    let keys = vec![
        (minifb::Key::Right, gameboy::joypad::JoypadKey::Right),
        (minifb::Key::Up, gameboy::joypad::JoypadKey::Up),
        (minifb::Key::Left, gameboy::joypad::JoypadKey::Left),
        (minifb::Key::Down, gameboy::joypad::JoypadKey::Down),
        (minifb::Key::Z, gameboy::joypad::JoypadKey::A),
        (minifb::Key::X, gameboy::joypad::JoypadKey::B),
        (minifb::Key::Space, gameboy::joypad::JoypadKey::Select),
        (minifb::Key::Enter, gameboy::joypad::JoypadKey::Start),
    ];
    for (rk, vk) in &keys {
        if window.is_key_down(*rk) {
            mbrd.mmu.borrow_mut().joypad.keydown(vk.clone());
        } else {
            mbrd.mmu.borrow_mut().joypad.keyup(vk.clone());
        }
    }
}
```

PC 键盘上的按键与 Game Boy JoyPad 的映射关系如下:

| PC 键盘 | 对应的 Game Boy 按钮 |
| ------- | -------------------- |
| ↑       | ↑                    |
| ↓       | ↓                    |
| ←       | ←                    |
| →       | →                    |
| Z       | A                    |
| X       | B                    |
| Space   | Select               |
| Enter   | Start                |
