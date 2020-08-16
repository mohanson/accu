# 按行读取文件

逐行读取文本文件的内容. 内置变量 `A_LoopReadLine` 存在于任何文件读取循环中. 它包含了已去除行尾的回车换行符(\r\n)的当前行内容. 如果一个内层文件读取循环包含在一个外层文件读取循环中, 则最内层循环的文件行将具有优先权.

```ahk
F1::
Loop, Read, C:\Database Export.txt
{
    SendRaw, %A_LoopReadLine%`n
}
Return
```
