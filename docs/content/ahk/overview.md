# AHK

AutoHotkey 是面向普通电脑用户的自由开源的自动化软件工具, 它让用户能够快捷或自动执行重复性任务. 与同类工具比较(比如抄袭的 x 键精灵), AutoHotkey 体积小巧, 语法简明使其易学易用, 同时在热键, 热字符串实现的快捷, 高效(同时也强大, 这点其他语言也能做到)方面没有其他语言能超越, 不过缺点同样明显, 即没有官方自带或第三方实现的完善的标准库, 这样需要实现未内置的功能时通常需要直接调用 Windows API 或寻找别人封装好的函数(注: 命令行命令或 COM 等与 Windows API 在功能全面性上相差太远). 换句话说, 普通人极容易使用, 但熟悉后要提升以实现更强大的功能时困难重重, 这点从大量用户选择该语言入手而后一些需求较高的用户则转向其他语言容易看的出来.

# 安装

下载地址: [https://autohotkey.com/download/](https://autohotkey.com/download/), 选择 Download AutoHotkey.zip, 解压文件. 注意此时还不能直接使用, 找到 Installer.ahk 并将此文件拖拽至 AutoHotkeyU64.exe 上, 即可打开安装界面. 一路下一步安装完成后在目录下生成 AutoHotKey.exe 二进制文件, 此时安装完成.

# 脚本

每个脚本都是需由程序 AutoHotkey.exe 执行的包含命令的纯文本. 脚本中还可以包含"热键"和"热字串"或者甚至完全由它们组成. 不过, 在不包含热键和热字串时, 脚本会在启动后从上往下按顺序执行其中的命令.

使用一个简单的例子测试一下: 将 `#n::Run www.google.com` 保存为 `run.ahk` 并在命令行中运行 `autohotkey run.ahk`, 可以发现托盘处出现一个绿色小图标, 使用 Win+N 即可在浏览器中打开 google.

# 参考
- [1] AutoHotKey: AutoHotKey [http://ahkcn.github.io/docs/AutoHotkey.htm](http://ahkcn.github.io/docs/AutoHotkey.htm)
- [2] AutoHotKey: 命令和函数索引 [http://ahkcn.github.io/docs/commands/index.htm](http://ahkcn.github.io/docs/commands/index.htm)
