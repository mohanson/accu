# 数字图像处理/PIL/概览

PIL 库系列文章大部分翻译自官方文档: [https://pillow.readthedocs.io](https://pillow.readthedocs.io), 使用的 PIL 版本号为 **4.3.x**. 这是个人的笔记记录.

## 使用 Image 对象

```py
import PIL.Image

im = PIL.Image.open('jp.jpg')
im.show()
```

## 保存图像

```py
im.save('jp.png')
```

PIL 在保存图像时, 会自动根据文件后缀名进行格式转化.

## 缩略图

```py
im.thumbnail((160, 120))
im.show()
```

`thumbnail` 方法会将图像转换为缩略图. 此方法修改图像为本身的缩略图版本, 缩略图不大于给定大小.

## 属性

```py
print(im.format, im.size, im.mode)
# JPEG (960, 540) RGB
```

## 裁剪, 粘贴与合并图像

```py
# 裁剪
box = (100, 100, 400, 400)
region = im.crop(box)

# 旋转裁剪的图像, 并粘贴回原位置
region = region.transpose(PIL.Image.ROTATE_180)
im.paste(region, box)
im.show()
```

当将子图像粘贴至父原图时, 子图像的大小必须与给定区域完全匹配. 此外, 该区域不能扩展到父图像之外. 但是, 子图像和父图像的模式(mode)不需要匹配. 在粘贴之前, 子图像会自动转换至父图像的模式.

## 滚动图像

```py
def roll(image, delta):
    """Roll an image sideways.
    """
    xsize, ysize = image.size

    delta = delta % xsize
    if delta == 0:
        return image

    part1 = image.crop((0, 0, delta, ysize))
    part2 = image.crop((delta, 0, xsize, ysize))
    part1.load()
    part2.load()
    image.paste(part2, (0, 0, xsize - delta, ysize))
    image.paste(part1, (xsize - delta, 0, xsize, ysize))

    return image

roll(im, 100).show()
```

![img](../../img/pil/pil_tutorial_overview/roll.gif)

请注意, 当从 `crop()` 操作中将其粘贴回时, 将首先调用 `load()`. 这是因为裁剪是一个惰性操作. 如果未调用 `load()`, 则在粘贴命令中使用图像之前, 将不会执行裁剪操作. 这将意味着 part1 将从已由第一个粘贴修改的图像版本中裁剪出来.

## 分离与合并通道

```py
r, g, b = im.split()
im = PIL.Image.merge('RGB', (b, g, r))
im.show()
```

## 简单几何变换

```py
out = im.resize((128, 128))
out = im.rotate(45) # degrees counter-clockwise
```

`resize` 与 `rotate` 方法会返回一个新的 Image 对象.

## 模式转换

```py
out = im.convert(mode='L')
```

可选的模式包括:

- `1` (1-bit pixels, black and white, stored with one pixel per byte)
- `L` (8-bit pixels, black and white)
- `P` (8-bit pixels, mapped to any other mode using a color palette)
- `RGB` (3x8-bit pixels, true color)
- `RGBA` (4x8-bit pixels, true color with transparency mask)
- `CMYK` (4x8-bit pixels, color separation)
- `YCbCr` (3x8-bit pixels, color video format) Note that this refers to the JPEG, and not the ITU-R BT.2020, standard
- `LAB` (3x8-bit pixels, the L\*a\*b color space)
- `HSV` (3x8-bit pixels, Hue, Saturation, Value color space)
- `I` (32-bit signed integer pixels)
- `F` (32-bit floating point pixels)

## 滤镜

```py
import PIL.ImageFilter

out = im.filter(PIL.ImageFilter.DETAIL)
```

可选的滤镜包括:

- BLUR
- CONTOUR
- DETAIL
- EDGE_ENHANCE
- EDGE\_ENHANCE\_MORE
- EMBOSS
- FIND_EDGES
- SMOOTH
- SMOOTH_MORE
- SHARPEN

## 像素操作

使用 `point()` 方法对图像的每一个像素做相应操作.

```py
# 反色: 所有像素点 i 会被 255 - i 替换
out = im.point(lambda i: 255-i)
out.show()
```

## 图像增强

```py
import PIL.ImageEnhance

# 对比度调整
enh = PIL.ImageEnhance.Contrast(im)
enh.enhance(1.3).show()
```

## 读取 GIF 动画

```py
im = PIL.Image.open('sample.gif')
im.seek(20)
im.show()
```

使用迭代器读取

```py
import PIL.ImageSequence

im = PIL.Image.open('sample.gif')
for frame in PIL.ImageSequence.Iterator(im):
    print(frame)
```

## 关于读取图像的更多说明

大多数时候, 通过传入文件名至 `open()` 函数读取一张图像. 但同时你也可以使用其他方式读取图像:

```py
import io
import PIL.Image
import numpy as np

# 从 fp 中读取
with open('jp.jpg', 'rb') as fp:
    im = PIL.Image.open(fp)

# 从字符串中读取
im = PIL.Image.open(io.StringIO('...'))

# 从矩阵中读取
im = PIL.Image.fromarray(255 * np.ones((100, 100)))
```

## 采样器

PIL 支持如下 6 种采样器, 均位于 `PIL.Image` 包内.

- `NEAREST`
- `BOX`
- `BILINEAR`
- `HAMMING`
- `BICUBIC`
- `LANCZOS`

## 显示图像

在调试过程中, 使用 `im.show()` 可以方便的展示图像, 但同时也可以借助一些其他方式展示图像, 如 `matplotlib` 和 `opencv`

```py
import PIL.Image

im = PIL.Image.new('RGB', (480, 270), color=(0xFF, 0xCC, 0x33))
im.show()

import matplotlib.pyplot as plt
plt.imshow(im)
plt.axis('off')
plt.show()

import cv2
import scipy.misc
cv2.imshow("im", scipy.misc.fromimage(im))
cv2.waitKey(0)
cv2.destroyAllWindows()
```
