# 数字图像处理/PIL/ImageDraw

`PIL.ImageDraw` 提供简单的 2D 绘图功能. 你可以使用它创建新的图像或修改已有的图像.

## 绘制线段

```py
import PIL.Image
import PIL.ImageDraw

im = PIL.Image.new('RGB', (480, 270), '#333333')
draw = PIL.ImageDraw.Draw(im)
draw.line((0, 0) + im.size, fill='#FFFFFF')
draw.line((0, im.size[1], im.size[0], 0), fill='#FFFFFF')
im.show()
```

![img](/img/pil/pil_imagedraw/line.jpg)

## 绘制离散的点

```py
draw.point([(x1, y1), (x2, y2), (x3, y3)...], fill='#FFFFFF')
```

## 绘制圆弧

`PIL.ImageDraw.Draw.arc` 方法可以在给定的矩形选框内绘制一段(内切)圆弧. 绘制起点为 3 点钟位置.

```py
import PIL.Image
import PIL.ImageDraw

im = PIL.Image.new('RGB', (480, 270), '#333333')
draw = PIL.ImageDraw.Draw(im)
draw.arc((100, 50, 379, 219), 0, 180, fill='#FFFFFF')
im.show()
```

![img](/img/pil/pil_imagedraw/arc.jpg)

`PIL.ImageDraw.Draw.chord` 方法与 `PIL.ImageDraw.Draw.arc` 类似, 不同的是会填充圆弧.

```py
import PIL.Image
import PIL.ImageDraw

im = PIL.Image.new('RGB', (480, 270), '#333333')
draw = PIL.ImageDraw.Draw(im)
draw.chord((100, 50, 379, 219), 0, 180, fill='#FFFFFF')
im.show()
```

![img](/img/pil/pil_imagedraw/chord.jpg)

`PIL.ImageDraw.Draw.ellipse` 方法绘制并填充椭圆.

```py
import PIL.Image
import PIL.ImageDraw

im = PIL.Image.new('RGB', (480, 270), '#333333')
draw = PIL.ImageDraw.Draw(im)
draw.ellipse((100, 50, 379, 219), fill='#FFFFFF')
im.show()
```

![img](/img/pil/pil_imagedraw/ellipse.jpg)

`PIL.ImageDraw.Draw.pieslice` 方法绘制并填充扇形.

```py
import PIL.Image
import PIL.ImageDraw

im = PIL.Image.new('RGB', (480, 270), '#333333')
draw = PIL.ImageDraw.Draw(im)
draw.pieslice((100, 50, 379, 219), 0, 90, fill='#FFFFFF')
im.show()
```

![img](/img/pil/pil_imagedraw/pieslice.jpg)

## 绘制矩形

```py
import PIL.Image
import PIL.ImageDraw

im = PIL.Image.new('RGB', (480, 270), '#333333')
draw = PIL.ImageDraw.Draw(im)
draw.rectangle((100, 50, 379, 219), fill='#FFFFFF')
im.show()
```

![img](/img/pil/pil_imagedraw/rectangle.jpg)

## 绘制多边形

```py
import PIL.Image
import PIL.ImageDraw

im = PIL.Image.new('RGB', (480, 270), '#333333')
draw = PIL.ImageDraw.Draw(im)
draw.polygon([(100, 50), (380, 50), (240, 250)], fill='#FFFFFF')
im.show()
```

![img](/img/pil/pil_imagedraw/polygon.jpg)

## 绘制文字

```py
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

font = PIL.ImageFont.truetype('consola', 14)
im = PIL.Image.new('RGB', (480, 270), '#333333')
draw = PIL.ImageDraw.Draw(im)
print(draw.textsize('Hello World!', font)) # (96, 10), 返回字符串将要占用的像素区域大小
draw.text((192, 130), 'Hello World!', '#FFFFFF', font)
im.show()
```

![img](/img/pil/pil_imagedraw/text.jpg)

与 `draw.text` 类似的还有一个 `draw.multiline_text` 方法, 不多做介绍.
