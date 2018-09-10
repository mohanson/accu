# 屏幕取色器

屏幕取色器, 键入 F1 显示并返回 16 进制 RGB, 同时将结果存入剪贴板内.

```ahk
F1::
MouseGetPos x, y
PixelGetColor rgb, x, y, RGB
ToolTip %rgb%
Clipboard=%rgb% ; 将 16 进制颜色放入剪贴板
SetTimer, RemoveToolTip, 2000 ; 2 秒后取消展示 ToolTip
return

RemoveToolTip:
SetTimer, RemoveToolTip, Off
ToolTip
return
```

执行效果:

![img](/img/ahk/color/color.png)
