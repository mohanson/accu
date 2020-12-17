# 数字图像处理/PIL/ImageColor

`PIL.ImageColor` 包含两个将字符串转换为颜色值的函数 `getrgb()` 与 `getcolor()`.

```py
import PIL.ImageColor

# getrgb(color) 返回 (red, green, blue[, alpha])
print(PIL.ImageColor.getrgb('#FFCC33'))
print(PIL.ImageColor.getrgb('rgb(255, 204, 51)'))
print(PIL.ImageColor.getrgb('rgb(100%,0%,0%)'))
print(PIL.ImageColor.getrgb('hsl(0,100%,50%)'))
# 颜色名称作为参数传入, 允许的名称定义在 PIL.ImageColor.colormap 中
print(PIL.ImageColor.getrgb('pink'))

# getcolor(color, mode) 返回 (graylevel [, alpha]) 或 (red, green, blue[, alpha])
print(PIL.ImageColor.getcolor('#FFCC33', 'L'))
```
