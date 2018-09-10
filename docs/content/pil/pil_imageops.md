`PIL.ImageOps` 包含一些预定义的图像处理操作, 大多数只工作于 `L` 和 `RGB` 模式下.

# 自动调整对比度

```py
im = PIL.ImageOps.autocontrast(image, cutoff=0, ignore=None)
```

该函数计算图像的直方图, 移除最大和最小的 `cutoff` 百分比像素, 并将像素范围拉伸到 0 - 255.

# 灰度图着色

```py
im = PIL.ImageOps.colorize(image, black, white)
```

着色一幅灰度图. 参数中的 `black` 和 `white` 需要为 RGB 颜色.


# 移除或添加指定像素的边框

```py
# 移除边框
im = PIL.ImageOps.crop(image, border=0)

# 添加边框
im = PIL.ImageOps.expand(image, border=0, fill=0)
```

移除图像上下左右 `border` 像素.

# 直方图均衡化

```py
im = PIL.ImageOps.equalize(image, mask=None)
```

# 翻转图像

```py
# 上下翻转
im =  PIL.ImageOps.flip(image)

# 左右翻转
im = PIL.ImageIps.mirror(image)
```

# 反色

```py
im = PIL.ImageOps.invert(image)
```

# 降低颜色位数

```py
im = PIL.ImageOps.posterize(image, bits)
```

`bits` 为每个通道保留的颜色位数, 范围 (1-8).


