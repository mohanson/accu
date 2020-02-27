# Cartridge Header

Cartridge 保存了游戏的汇编代码与全部二进制数据(图像, 音乐等), 它是一种结构化的数据存储格式. 与众多常用的文件存储格式类似, Cartridge 在文件开头也有一段特殊区域, 被称为 Header(文件头). Header 内包含了描述该 Cartridge 的信息以及关于引导 Game Boy 游戏机正常读取游戏数据的程序指令. Cartridge 的 Header 区位于 Cartridge 的 0x0100-0x0140(第 256 个字节到第 320 个字节)位置.

文件头是位于文件开头的一段承担一定任务的数据, 一般都在文件开头部分, 但也有一些位于文件结尾, 这取决于特定的文件格式. 文件头通常保存该文件的一些信息, 比如数据存储格式与压缩方式, 用于引导文件处理程序正确读取文件信息. 用一个简单的例子来说明, 比如一个 JPG 格式的图像文件, 图像浏览器无需读取文件的全部数据而仅仅需要读取 Header 中的一部分数据, 就能获知图形的长宽等信息.

# 0100-0103 程序执行入口

每当游戏卡带插入 Game Boy 游戏机后, 屏幕将显示任天堂的 LOGO. 在显示完成任天堂的 LOGO 后, Game Boy 内置的启动程序将会把程序计数器 PC 设置到 0x0100 地址, 之后, 该区段中包含的程序指令会使程序计数器跳转到 Cartridge 内的实际入口地址. 通常来讲, 这 4 个 Byte 包含一个 NOP 指令, 和一个 JP 0x0150 指令, 这两个指令会指示 CPU 跳转到 0x0150 的位置.

通常情况下这段区域的地址与其对应的值如下表所示.

|  Addr  | Data |
| ------ | ---- |
| 0x0100 | 0x00 |
| 0x0101 | 0xc3 |
| 0x0102 | 0x50 |
| 0x0103 | 0x01 |

其等价 ASM 表示为:

```
NOP
JUMP 0x0150
```

# 0104-0133 任天堂的 LOGO

该字节区域存储了任天堂的 LOGO 图标. 当 Game Boy 开机的时候, 首先会显示这部分内容, 之后验证该图像的内容. 如果这部分内容的字节不正确, 则会锁定自身并拒绝继续运行. 这部分内容的 16 进制格式如下所示.

```
CE ED 66 66 CC 0D 00 0B 03 73 00 83 00 0C 00 0D
00 08 11 1F 88 89 00 0E DC CC 6E E6 DD DD D9 99
BB BB 67 63 6E 0E EC CC DD DC 99 9F BB B9 33 3E
```

大部分情况下 Game Boy 只会验证前 0x18 字节, 但偶尔也会有验证全部 0x30 字节的情况.

任天堂之所以要求卡带内必须附带这部分信息是有历史原因的, 因为在互联网发展早期, 各个国家的版权法/著作权法并不完善, 并不都能非常权威的界定"在电脑上复制粘贴电子文件是否属于侵权", 因此有许多盗版商复制游戏卡带的内容并制作盗版卡带. 任天堂通过在卡带中加入商标图像并在 Game Boy 游戏机上强制去鉴定商标内容, 巧妙的将对版权或著作权的侵权转换为对公司商标的侵权--商标侵权在那时候已经有非常完善的法律去界定了. 当然另一个重要方面, 加入 LOGO 亦有助于提升公司的社会知名度, 比如现今比较有名的游戏开发引擎 Unity, 如果开发者使用的是其免费版, 其制作和发行的游戏在启动时则必须显示 Unity 的 LOGO.

![img](/img/gameboy/cartridge/cartridge_header/nintendo_logo.png)

# 0134-0143 标题

该字节区域存储了卡带的标题. 卡带的标题总是大写的 ASCII 英文字母. 如果标题长度小于 16 个字符, 剩余的存储空间则全部使用 0x00 填充. 在发明 Game Boy Color(CGB)前, 任天堂将这个区域的长度减少到 15 个字符, 几个月之后他们就又有了将它减少到 11 个字符的奇妙想法. 因此一个 Game Boy 仿真器总是首先需要判断这盒卡带是不是 CGB 卡带, 然后再选用正确的读取方式读取标题. CGB 模式的区段内容如下.

**013F-0142 制造商代码**

在非 CGB 卡带中, 这部分内容是标题的一部分. 在 CGB 卡带中, 这部分存储了制造商的代码. 暂时不明白如此这般做法有什么目的和深层次的意义.

**0143 CGB 标志**

在非 CGB 卡带中, 这部分内容是标题的一部分. 在 CGB 卡带中, 其高位表示该盒卡带已启用 CGB 功能. 对于 CGB 来说这是必需的, 否则 CGB 会将自身切换为非 CGB 模式. 典型值为:

- 0x80 - 该游戏支持 CGB 功能, 但同样能在非 CGB 游戏机上运行.
- 0xC0 - 该游戏仅能运行在 CGB 游戏机上.

在 Game Boy 实机上, 如果设置了第 7 位, 以及第 2 或第 3 位, 会切换到特殊的非 CGB 模式, 该模式下系统调色盘未初始化. 目的未知, 但猜测最终这应该用于着色单色游戏上, 这些单色游戏可能在卡带的某个部分自己设定了调色盘数据.

# 0144-0145 许可协议代码

使用两个字节存储许可协议的代码, 这些代码和游戏公司或发布者相关. 一些典型的例子如下:

```
00  none                01  Nintendo R&D1   08  Capcom
13  Electronic Arts     18  Hudson Soft     19  b-ai
20  kss                 22  pow             24  PCM Complete
25  san-x               28  Kemco Japan     29  seta
30  Viacom              31  Nintendo        32  Bandai
33  Ocean/Acclaim       34  Konami          35  Hector
37  Taito               38  Hudson          39  Banpresto
41  Ubi Soft            42  Atlus           44  Malibu
46  angel               47  Bullet-Proof    49  irem
50  Absolute            51  Acclaim         52  Activision
53  American sammy      54  Konami          55  Hi tech entertainment
56  LJN                 57  Matchbox        58  Mattel
59  Milton Bradley      60  Titus           61  Virgin
64  LucasArts           67  Ocean           69  Electronic Arts
70  Infogrames          71  Interplay       72  Broderbund
73  sculptured          75  sci             78  THQ
79  Accolade            80  misawa          83  lozc
86  tokuma shoten i*    87  tsukuda ori*    91  Chunsoft
92  Video system        93  Ocean/Acclaim   95  Varie
96  Yonezawa/s'pal      97  Kaneko          99  Pack in soft
A4  Konami (Yu-Gi-Oh!)
```

# 0146 SGB 标志

该字节告知游戏是否支持 Super Game Boy(SGB)功能, 常见值为:

- 0x00: 游戏不支持 SGB 功能.
- 0x03: 游戏支持 SGB 功能.

如果此字节设置为 0x03 以外的其他值, 则视为不支持 SGB 功能. SGB 是 Game Boy 的周边产品, 玩家可以把 SGB 插到 SFC 上然后在 SGB 上插上一张 GB 卡带, 这样玩家就可以在电视上玩 GB 游戏了.

![img](/img/gameboy/cartridge/cartridge_header/sgb.png)

# 0147 卡带类型

该字节告知游戏卡带所使用的 Memory Bank Controller 类型(缩写为 MBC, 下一节将会对此进行详细讨论), 以及游戏卡带中是否使用了其它外部硬件, 比如电池, 红外线感光器, 相机等. 通常来讲有以下几种常见硬件:

- ROM: 不可变存储, 用来存储游戏本体数据
- RAM: 可变存储, 通常用来存储游戏记录, 关闭 Game Boy 后数据清空
- BATTERY: 电池, 用来持久化存储 RAM 中的内容, 关闭 Game Boy 后可向 RAM 供电从而保持 RAM 内的数据不变.
- TIMER: 内部时钟, 用于记录时间.

值与其含义的对照如下所示:

```
0x00  ROM ONLY                 0x19  MBC5
0x01  MBC1                     0x1A  MBC5+RAM
0x02  MBC1+RAM                 0x1B  MBC5+RAM+BATTERY
0x03  MBC1+RAM+BATTERY         0x1C  MBC5+RUMBLE
0x05  MBC2                     0x1D  MBC5+RUMBLE+RAM
0x06  MBC2+BATTERY             0x1E  MBC5+RUMBLE+RAM+BATTERY
0x08  ROM+RAM                  0x20  MBC6
0x09  ROM+RAM+BATTERY          0x22  MBC7+SENSOR+RUMBLE+RAM+BATTERY
0x0B  MMM01
0x0C  MMM01+RAM
0x0D  MMM01+RAM+BATTERY
0x0F  MBC3+TIMER+BATTERY
0x10  MBC3+TIMER+RAM+BATTERY   0xFC  POCKET CAMERA
0x11  MBC3                     0xFD  BANDAI TAMA5
0x12  MBC3+RAM                 0xFE  HuC3
0x13  MBC3+RAM+BATTERY         0xFF  HuC1+RAM+BATTERY
```

# 0148 ROM 大小

该字节标明该卡带的 ROM 大小. 通常是 32KB 的整数倍. 常用的值与其实际表示的容量大小对应如下:

```
0x00 -  32KByte (no ROM banking)
0x01 -  64KByte (4 banks)
0x02 - 128KByte (8 banks)
0x03 - 256KByte (16 banks)
0x04 - 512KByte (32 banks)
0x05 -   1MByte (64 banks)  - only 63 banks used by MBC1
0x06 -   2MByte (128 banks) - only 125 banks used by MBC1
0x07 -   4MByte (256 banks)
0x08 -   8MByte (512 banks)
0x52 - 1.1MByte (72 banks)
0x53 - 1.2MByte (80 banks)
0x54 - 1.5MByte (96 banks)
```

# 0149 RAM 大小

该字节标明该卡带中外部 RAM 的大小. 常用的值与其实际表示的容量大小对应如下:

```
0x00 - None
0x01 - 2 KBytes
0x02 - 8 Kbytes
0x03 - 32 KBytes (4 banks of 8KBytes each)
0x04 - 128 KBytes (16 banks of 8KBytes each)
0x05 - 64 KBytes (8 banks of 8KBytes each)
```

需要注意的是, 当使用的是 MBC2 卡带时, 该位置必须设置为 0x00, 即使 MBC2 本身包含一个内置的容量为 512 x 4bits 的 RAM.


# 014A 发售地代码

该字节标明该卡带是否在非日本地区销售. 只有两个可选值:

```
0x00 - Japanese
0x01 - Non-Japanese
```


早期 Game Boy 和其游戏卡带只在日本国内市场有销售, 但随着它的扩张, 其发售地逐渐扩张到了美国, 欧洲, 台湾等国家和地区. 仅仅用一个"是/否日本地区发售"的标记显然已经无法满足需要, 因此该字节实际上处于一个没什么用处的尴尬地位. 在 0x014a 之后的 0x014b(旧的许可协议代码) 和 0x014c(版本号) 其实都处于一种半废弃状态, 因此不再过多笔墨进行介绍.

# 014D 标题校验和

该字节包含卡带标题(0134-014C)的 8 位校验和. 校验和计算伪代码如下:

```
x=0:FOR i=0134h TO 014Ch:x=x-MEM[i]-1:NEXT
```

其对应的 Rust 代码可以用如下一个简短函数表示:

```rs
fn check_checksum(rom: &[u8]) -> bool {
    let mut v: u8 = 0;
    for i in 0x0134..0x014d {
        v = v.wrapping_sub(rom[i]).wrapping_sub(1);
    }
    rom[0x014d] == v
}
```

返回结果的低 8 位必须与此条目中的值相同. 如果此校验和不正确, 则游戏将不会被执行.

# 014E-014F 全局校验和

该字节区域包含一个 16 位校验和, 此校验和校验卡带的全部数据内容. Game Boy 并不会主动去验证该校验和.

由于缺乏相关的直接技术资料, 全局校验和的计算过程是从开源的 Game Boy 引擎 GBDK 的源代码中反推而来的, 其 C 语言源代码如下.

```c
chk = 0;
cart[0x014E/SEGSIZE][0x014E%SEGSIZE] = 0;
cart[0x014F/SEGSIZE][0x014F%SEGSIZE] = 0;
for(i = 0; i < NBSEG; i++)
    for(pos = 0; pos < SEGSIZE; pos++)
        chk += cart[i][pos];
cart[0x014E/SEGSIZE][0x014E%SEGSIZE] = (chk>>8)&0xFF;
cart[0x014F/SEGSIZE][0x014F%SEGSIZE] = chk&0xFF;
```

其中变量 chk(checksum) 为一个 unsigned long 类型, 在开始计算全局校验和之前, 首先设置 0x014e 与 0x014f 为 0, 然后逐字节读取 cartridge 中的数据并与 chk 相加. 循环结束后, ckh 的值被保存在地址 0x014e 与 0x014f 中.

# 示例代码

本节将会编写一段简单的程序, 用来解析 Cartridge Header 的部分信息. 用作测试的游戏 ROM 是《Boxes》游戏, 读者可以在 [https://github.com/mohanson/gameboy/tree/master/res](https://github.com/mohanson/gameboy/tree/master/res) 下载到该游戏 ROM. 程序的目的是读取游戏的标题, 并确认其标题校验和正确.

```rs
use std::io::Read;

// 获取游戏卡带的标题
fn rom_name(rom: &[u8]) -> String {
    let mut buf = String::new();
    let ic = 0x0134;
    let oc = if rom[0x0143] == 0x80 { 0x013e } else { 0x0143 };
    for i in ic..oc {
        match rom[i] {
            0 => break,
            v => buf.push(v as char),
        }
    }
    buf
}

// 验证标题校验和
fn check_checksum(rom: &[u8]) -> bool {
    let mut v: u8 = 0;
    for i in 0x0134..0x014d {
        v = v.wrapping_sub(rom[i]).wrapping_sub(1);
    }
    rom[0x014d] == v
}

fn main() -> Result<(),  Box<std::error::Error>> {
    let mut f = std::fs::File::open("/src/gameboy/res/boxes.gb")?;
    let mut rom = Vec::new();
    f.read_to_end(&mut rom).unwrap();
    assert!(rom.len() >= 0x0150);
    assert!(check_checksum(&rom[..]));

    let rom_name = rom_name(&rom[..]);
    println!("{}",  rom_name); // BOXES
    Ok(())
}
```

运行上述代码, 此游戏的标题被成功打印至标准输出. 同时, 注意到代码中使用了一个 asset 语言来对标题校验和进行断言.

![img](/img/gameboy/cartridge/cartridge_header/output.png)

除了获取标题之外, 读者可以自行去完善这部分代码来尝试获取软件开发商, 发售地等信息.
