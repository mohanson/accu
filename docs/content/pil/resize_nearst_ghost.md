# 数字图像处理/缩放/最近邻插值法的幽灵事件

当通过近邻取样插值法对图片进行缩放的时候, 目标图像的每个像素都来源于原图像的对应位置像素. 这可能会造成意想不到的后果.考虑如下图片, 该图像似乎并没有什么特别, 但对该图像进行缩放时:

![img](/img/pil/resize_nearst_ghost/jp_ghost.bmp)

```py
import PIL.Image

im = PIL.Image.open('/img/jp_ghost.bmp')
im = im.resize((im.size[0] // 2, im.size[1] // 2), PIL.Image.NEAREST)
im.show()
```

长宽均缩放 1/2 后的图片如下:

![img](/img/pil/resize_nearst_ghost/jp_ghost_resized.jpg)

原图变成了一张颜色为 (99, 97, 101) 的纯色图片.

在使用近邻取样插值法缩放的时候, 原图中特定的像素点将组合成新的图片. 因此只需要控制原图中的特定位置的像素点, 就能控制缩放后生成的图像.

将原图放大, 观察到如下结构, 可以看到大量规则排列的 (99, 97, 101) 像素点覆盖了整个原图. 当缩放至 1/2 时, 这些像素点被取出并组合成了新的图像. 其中 (99, 97, 101) 是原图的图像均值.

![img](/img/pil/resize_nearst_ghost/jp_ghost_stats.jpg)

注: 生成幽灵图片的代码如下:

```py
import PIL.Image
import PIL.ImageStat

im = PIL.Image.open('/img/jp.jpg')
mean = PIL.ImageStat.Stat(im).mean
mean = tuple(int(e) for e in mean)

for x in range(im.size[0] // 2):
    for y in range(im.size[1] // 2):
        im.putpixel((2 * x + 1, 2 * y + 1), mean)

im.show()
```
