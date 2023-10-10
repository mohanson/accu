# AHK/AHK

AutoHotkey 是面向普通电脑用户的自由开源的自动化软件工具, 它让用户能够快捷或自动执行重复性任务. 与同类工具比较(比如抄袭的 x 键精灵), AutoHotkey 体积小巧, 语法简明使其易学易用, 同时在热键, 热字符串实现的快捷, 高效(同时也强大, 这点其他语言也能做到)方面没有其他语言能超越, 不过缺点同样明显, 即没有官方自带或第三方实现的完善的标准库, 这样需要实现未内置的功能时通常需要直接调用 Windows API 或寻找别人封装好的函数(注: 命令行命令或 COM 等与 Windows API 在功能全面性上相差太远). 换句话说, 普通人极容易使用, 但熟悉后要提升以实现更强大的功能时困难重重, 这点从大量用户选择该语言入手而后一些需求较高的用户则转向其他语言容易看的出来.

笔者最常使用 AHK 是在各种即时策略游戏和 MOBA 游戏中, 它能帮助我做出人类不可能做出的操作. 第一次使用是在 Dota 中, 我让我的流浪剑客装备上了跳刀, 疯脸, 鬼手, 勇气勋章, 然后在 0.1 秒的时间内开启全部装备(打上兴奋剂)并使用技能吼叫, 大招, 扔锤, 然后在之后的几秒内秒掉对手. 那是一去不复回的青春啊.

## 安装

下载地址: [https://autohotkey.com/download/](https://autohotkey.com/download/), 选择 Download AutoHotkey.zip, 解压文件. 注意此时还不能直接使用, 找到 Installer.ahk 并将此文件拖拽至 AutoHotkeyU64.exe 上, 即可打开安装界面. 一路下一步安装完成后在目录下生成 AutoHotKey.exe 二进制文件, 此时安装完成.

每个脚本都是需由程序 AutoHotkey.exe 执行的包含命令的纯文本. 脚本中还可以包含"热键"和"热字串"或者甚至完全由它们组成. 不过, 在不包含热键和热字串时, 脚本会在启动后从上往下按顺序执行其中的命令.

使用一个简单的例子测试一下: 将 `#n::Run www.google.com` 保存为 `run.ahk` 并在命令行中运行 `autohotkey run.ahk`, 可以发现托盘处出现一个绿色小图标, 使用 Win+N 即可在浏览器中打开 google.

关于 ahk 语法可参考文档 [https://www.autohotkey.com/docs/](https://www.autohotkey.com/docs/), 这里直接使用几个例子来演示 ahk 的功能.

## 鼠标连点器

当按下 F1 时鼠标左键连点, 松开 F1 时停止连点.

```ahk
F1::   ; 把 F1 键设置为热键.
Loop   ; 由于没有指定数字, 所以这是个无限循环, 直到遇到内部的 "break" 或 "return".
{
    if not GetKeyState("F1", "P")  ; 如果此状态为 true, 那么用户实际已经释放了 F1 键.
        break                      ; 中断循环.
                                   ; 否则 (由于上面没有 "中断"), 继续点击鼠标.
    Click                          ; 在当前指针位置点击鼠标左键.
}
return
```

## 屏幕取色器

屏幕取色器, 键入 F1 显示并返回 16 进制 RGB, 同时将结果存入剪贴板内.

```ahk
F1::
MouseGetPos x, y
PixelGetColor rgb, x, y, RGB
ToolTip %rgb%
Clipboard=%rgb%               ; 将 16 进制颜色放入剪贴板
SetTimer, RemoveToolTip, 2000 ; 2 秒后取消展示 ToolTip
return

RemoveToolTip:
SetTimer, RemoveToolTip, Off
ToolTip
return
```

执行效果:

![img](../../img/ahk/overview/color.jpg)

## 长按

判断按键是否长按. 短按 F1 时输出 single, 长按 F1 时输出 lpress.

```ahk
F1::
KeyWait, F1, T0.3
If ErrorLevel {
    Send, lpress
    KeyWait, F1
} else {
    Send, single
}
Return
```

## 按行读取文件

逐行读取文本文件的内容. 内置变量 `A_LoopReadLine` 存在于任何文件读取循环中. 它包含了已去除行尾的回车换行符(\r\n)的当前行内容. 如果一个内层文件读取循环包含在一个外层文件读取循环中, 则最内层循环的文件行将具有优先权.

```ahk
F1::
Loop, Read, C:\Database Export.txt
{
    SendRaw, %A_LoopReadLine%`n
}
Return
```
