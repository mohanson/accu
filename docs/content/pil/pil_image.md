# 数字图像处理/PIL/Image

## 合并图像

合并图像可以使用 `PIL.Image.alpha_composite`, `PIL.Image.blend` 和 `PIL.Image.composite`, 这里简单演示下第一种方式:

```py
import PIL.Image
import numpy as np

im = PIL.Image.open('jp.jpg')
im = im.convert('RGBA')

mask_mat = np.zeros((im.size[1], im.size[0], 4), dtype=np.uint8)
mask_mat[:, :, 0] = np.ones((im.size[1], im.size[0]), dtype=np.uint8) * 0xFF
mask_mat[:, :, 1] = np.ones((im.size[1], im.size[0]), dtype=np.uint8) * 0xCC
mask_mat[:, :, 2] = np.ones((im.size[1], im.size[0]), dtype=np.uint8) * 0x33
mask_mat[:, :, 3] = np.ones((im.size[1], im.size[0]), dtype=np.uint8) * 80
mask = PIL.Image.fromarray(mask_mat)

# 为原图像添加 (0xFF, 0xCC, 0x33, 80) 的蒙版
im = PIL.Image.alpha_composite(im, mask)
im.show()
```

![img](/img/pil/pil_image/alpha_composite.jpg)

## 对每个像素点进行操作

`PIL.Image.eval` 将指定的函数应用在图像的每一个像素点之上.

```py
import PIL.Image

im = PIL.Image.open('jp.jpg')
# 使用 lambda x: 255-x 取反色
im = PIL.Image.eval(im, lambda x: 255-x)
im.show()
```

![img](/img/pil/pil_image/invert_color.jpg)

## 分离与合并通道

```py
import PIL.Image

im = PIL.Image.open('jp.jpg')
# 分离每个通道, 返回 Image 元组
r, g, b = im.split()
# 合并多个通道, 参数 Image 元组
im = PIL.Image.merge('RGB', (r, g, b))

# 如果你只期望获得一个通道的 Image, 则可以使用 getchannel()
r = im.getchannel('R')
r.show()

# 获取图像像素数据
mat = list(im.getdata())
print(mat[0]) # (84, 70, 59)
# 获取图像一个通道的像素数据
mat = list(im.getdata(0))
print(mat[0]) # 84
```

## 创建新的图像

```py
import PIL.Image

im = PIL.Image.new('RGB', (480, 270), color=(0xFF, 0xCC, 0x33))
im.show()
```

## 获取与更新像素点

使用两个方法: `getpixel` 与 `putpixel`.

```py
import PIL.Image

im = PIL.Image.open('jp.jpg')

# 获取其中一个像素点
print(im.getpixel((40, 40)))
# (87, 84, 77)

# 更新其中一个像素点
im.putpixel((40, 40), (0, 0, 0))
```

## 直方图

```py
import matplotlib.pyplot as plt
import numpy as np
import PIL.Image

im = PIL.Image.open('jp.jpg')
im = im.convert('L')

ax = plt.subplot()
ax.bar(np.arange(0, 256), im.histogram())
plt.show()
```

![img](/img/pil/pil_image/histogram.jpg)

## 应用滤波器

```py
import PIL.Image
import PIL.ImageFilter

im = PIL.Image.open('jp.jpg')
im = im.filter(PIL.ImageFilter.GaussianBlur) # 高斯滤波
im.show()
```

## 属性

```py
import PIL.Image

im = PIL.Image.open('jp.jpg')
print(im.filename)  # jp.jpg
print(im.format)  # JPEG
print(im.mode)  # RGB
print(im.size)  # (480, 270)
print(im.width)  # 480
print(im.height)  # 270
print(im.palette) # None
print(im.info) # {'jfif': 257, 'jfif_version': (1, 1), 'jfif_unit': 0, 'jfif_density': (1, 1)}
```
