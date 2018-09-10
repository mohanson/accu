# 长按

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
