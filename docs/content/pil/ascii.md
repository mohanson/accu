# 数字图像处理/字符画

## 效果展示

![img](/img/pil/ascii/jp.jpg)
![img](/img/pil/ascii/jp_ascii.jpg)

## 改变色彩模式至灰度图

字符画的第一步是将彩色图片转变为灰度图. 对于彩色转灰度图, 有一个著名公式 ITU-R 601-2 luma. 因为人眼对 RGB 颜色的感知并不相同, 所以转换的时候需要给予不同的权重:

```
L = R * 299/1000 + G * 587/1000 + B * 114/1000
```

在 PIL 中, 使用 `.convert('F')` 将任意图像转换为 256 阶灰度图.

```py
import PIL.Image

im = PIL.Image.open('/img/jp.jpg')
im = im.convert('F')
```

## 图像均值

图像均值即图像的主题色. 在 PIL 中, 使用如下方式获取图像均值:

```py
import PIL.Image
import PIL.ImageStat

im = PIL.Image.open('/img/jp.jpg')
mean = PIL.ImageStat.Stat(im).mean
print(mean)
# [98.61, 97.29, 100.91, 255.0], 每一项分别代表 RGBA
```

## 字符介绍

**字符占空比**: 在单个字符的显示范围内, 填充像素点的个数与总像素点的比值. 这里使用 `#`, `=`, `-`, `空格` 四个占空比逐步下降的  ASCII 字符作为字符画的基础元素. 同时约定灰度高于均值的像素点采用 `#` 与 `=`, 灰度低于均值的像素点采用 `-`, `空格`.

**字符宽高比**: 14 号字体大小的宽高比为 8:14. 因此假设需要将 100x100 的图片转换为由 14 号字体大小的 `#`, `=`, `-`, `空格` 构成的字符画, 则需要使用 100x100 个字符填充至大小为 800x1400 的画布上.

## 在画卷上写一首诗

下面介绍如何新建一副图像, 并在图像上书写名诗作 "The Zen of Python".

```py
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont

zen = """The Zen of Python, by Tim Peters

Beautiful is better than ugly.
Explicit is better than implicit.
Simple is better than complex.
Complex is better than complicated.
Flat is better than nested.
Sparse is better than dense.
Readability counts.
Special cases aren't special enough to break the rules.
Although practicality beats purity.
Errors should never pass silently.
Unless explicitly silenced.
In the face of ambiguity, refuse the temptation to guess.
There should be one-- and preferably only one --obvious way to do it.
Although that way may not be obvious at first unless you're Dutch.
Now is better than never.
Although never is often better than *right* now.
If the implementation is hard to explain, it's a bad idea.
If the implementation is easy to explain, it may be a good idea.
Namespaces are one honking great idea -- let's do more of those!"""

font = PIL.ImageFont.truetype('consola', 14)

im = PIL.Image.new('RGB', (552, 294), '#FFFFFF')
dr = PIL.ImageDraw.Draw(im)
dr.text((0, 0), zen, '#000000', font)

im.show()
```

最终能得到如下一副白底黑字的图片

![img](/img/pil/ascii/zen.jpg)

## 合并代码

对上述技巧的简单组合, 很容易便能得到如下字符画生成方案, 运行下面的程序会打开一个图片预览窗口显示生成的字符画图像

```py
import PIL.Image
import PIL.ImageDraw
import PIL.ImageFont
import PIL.ImageStat

font = PIL.ImageFont.truetype('consola', 14)

im = PIL.Image.open('/img/jp.jpg')
im = im.convert('F')
size = im.size

rx = im.size[0]
ry = int(rx / size[0] * size[1] * 8 / 14)
im = im.resize((rx, ry), PIL.Image.NEAREST)

mean = PIL.ImageStat.Stat(im).mean[0]

words = []
for y in range(im.size[1]):
    for x in range(im.size[0]):
        p = im.getpixel((x, y))
        if p < mean / 2:
            c = '#'
        elif mean / 2 <= p < mean:
            c = '='
        elif mean <= p < mean + (255 - mean) / 2:
            c = '-'
        elif mean + (255 - mean) / 2 <= p:
            c = ' '
        else:
            raise ValueError(p)
        words.append(c)
    words.append('\n')

im.close()

im = PIL.Image.new('RGB', (im.size[0] * 8, im.size[1] * 14), '#FFFFFF')
dr = PIL.ImageDraw.Draw(im)
dr.text((0, 0), ''.join(words), '#000000', font)
im = im.resize(size, PIL.Image.LANCZOS)
im.show()
```
