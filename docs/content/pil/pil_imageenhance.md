# 数字图像处理/PIL/ImageEnhance

`PIL.ImageEnhance` 包含一系列的图像增强算法.

## 色彩平衡度

`PIL.ImageEnhance.Color`

```py
import PIL.Image
import PIL.ImageEnhance

im = PIL.Image.open('jp.jpg')
enhancer = PIL.ImageEnhance.Color(im)
# 从灰度图逐渐恢复到原图
for i in range(11):
    enhancer.enhance(i / 10.0).show()
```

![img](../../img/pil/pil_imageenhance/color.gif)

## 对比度

`PIL.ImageEnhance.Contrast`

```py
import PIL.Image
import PIL.ImageEnhance

im = PIL.Image.open('jp.jpg')
enhancer = PIL.ImageEnhance.Contrast(im)
enhancer.enhance(0.5).show()
enhancer.enhance(2.0).show()
```

## 亮度

`PIL.ImageEnhance.Brightness`

```py
import PIL.Image
import PIL.ImageEnhance

im = PIL.Image.open('jp.jpg')
enhancer = PIL.ImageEnhance.Brightness(im)
enhancer.enhance(0.5).show()
enhancer.enhance(2.0).show()
```

## 锐化

`PIL.ImageEnhance.Sharpness`

```py
import PIL.Image
import PIL.ImageEnhance

im = PIL.Image.open('jp.jpg')
enhancer = PIL.ImageEnhance.Sharpness(im)
# 低于 1 时模糊, 高于 1 时锐化
enhancer.enhance(0.5).show()
enhancer.enhance(2.0).show()
```
