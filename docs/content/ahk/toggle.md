# AHK/在一个热键上开启或关闭

我们可以在一个热键上绑定一个切换功能. 使用这个热键可以打开或关闭某个功能, 例如触发热键时, 脚本开始连点, 一旦"切换"开关，连点动作就会停止.

有两种写法都可以满足要求.

**第一种**

```ahk
F1::
    flag := !flag
    if flag  {
        SetTimer, F1Function, 100
    } else {
        SetTimer, F1Function, Off
    }
    return

F1Function() {
    Send A
}
```

**第二种**

```ahk
#MaxThreadsPerHotkey 2
F1::
    flag := !flag
    While flag {
        Send A
        Sleep 100
    }
    return
```
