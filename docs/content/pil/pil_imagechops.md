# 数字图像处理/PIL/ImageChops

`PIL.ImageChops` 包含一系列的图像算术操作.

## 加法

```py
import PIL.Image
import PIL.ImageChops

im1 = PIL.Image.new('RGB', (480, 270), (0, 255, 0))
im2 = PIL.Image.new('RGB', (480, 270), (255, 0, 0))

# out = ((image1 + image2) / scale + offset)
im = PIL.ImageChops.add(im1, im2)
im.show()

# out = ((image1 + image2) % MAX)
im = PIL.ImageChops.add_modulo(im1, im2)
im.show()
```

## 减法

```py
# out = ((image1 - image2) / scale + offset)
im = PIL.ImageChops.subtract(im1, im2)
im.show()

# out = ((image1 - image2) % MAX)
im = PIL.ImageChops.subtract_modulo(im1, im2)
im.show()
```

## 乘法

```py
# out = image1 * image2 / MAX
im = PIL.ImageChops.multiply(im1, im2)
im.show()
```

## 最大值

```py
# out = max(image1, image2)
im = PIL.ImageChops.lighter(im1, im2)
im.show()
```

## 最小值

```py
# out = min(image1, image2)
im = PIL.ImageChops.darker(im1, im2)
im.show()
```

## 差异

```py
# out = abs(image1 - image2)
im = PIL.ImageChops.difference(im1, im2)
im.show()
```

## 反色

```py
# out = MAX - image
im = PIL.ImageChops.invert(im1)
im.show()
```

## 逻辑操作

```py
# out = ((image1 and image2) % MAX)
im = PIL.ImageChops.logical_and(im1, im2)
im.show()

# out = ((image1 or image2) % MAX)
im = PIL.ImageChops.logical_or(im1, im2)
im.show()
```

逻辑操作的参数图像模式必须是 `1`.
