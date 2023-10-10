# 数字图像处理/通道

数字图像处理系列文章最开始创作于 2015 年, 也是 Mohanson 的第一个长篇连载系列, 共耗时 1.5 年完成. 文章中的所记载的算法, 大部分来自《冈萨雷斯: 数字图像处理》书中的数学公式.

## 数字图像的本质

我们几乎每天都在互联网上浏览各种类型的图像. 但关于图像是如何存储和展现的问题, 我认为并不是每个人都很清楚. 我决定开始做一些简单的工作, 来揭开数字图像的本质. 与大多数人写文章的方式不同, 我喜欢先给出结论: 数字图像的本质是一个多维矩阵. 如果你对矩阵这个单词感到很陌生的话, 那么可以使用"多维数组"进行脑海中等价的替换, 它们本质上没有什么区别. 只不过前者是数学意义上的, 后者是计算机科学上的名词.

让我们正式开始吧.

以一张 480x270 的 RGB 色彩空间图像为例, 编写如下代码:

![img](../../img/pil/channel/jp.jpg)

```py
import numpy
import PIL.Image

im = PIL.Image.open('/img/jp.jpg')
im_mat = numpy.array(im)

print(im_mat.shape)
```

```text
(270, 480, 3)
```

我们首先使用 PIL 库从文件系统读取图片, 然后将之转换为 numpy 内的矩阵, 最后打印出矩阵的大小. 打印出来的数据说明这个图像有 270 行, 480 列, 以及在色彩上有 3 个分量. 换句话说, 是一个 [270, 480, 3] 大小的矩阵.

进一步分解该图片可以得到 R, G, B 三个通道分量:

```py
import PIL.Image

im = PIL.Image.open('/img/jp.jpg')
r, g, b = im.split()

r.show()
g.show()
b.show()
```

上述代码会在你的计算机上展示三个窗口, 每个窗口会显示如下的三张图片. 如果你将每个分量转换为矩阵并打印矩阵的大小(就像我们开始时做的那样), 会发现每个分量都是一个 [270, 480, 1] 的矩阵.

R 通道的灰度图像:

![img](../../img/pil/channel/jp_r.jpg)

G 通道的灰度图像:

![img](../../img/pil/channel/jp_g.jpg)

B 通道的灰度图像:

![img](../../img/pil/channel/jp_b.jpg)

## 交换通道

如果我们交换一下通道分量放置的顺序, 例如把 B 分量放进红色通道里, 把 G 分量放进绿色通道里, R 分量放进蓝色通道里, 可以得到如下一副图像:

```py
import PIL.Image

im = PIL.Image.open('/img/jp.jpg')
r, g, b = im.split()
im = PIL.Image.merge('RGB', (b, g, r))
im.show()
```

![img](../../img/pil/channel/jp_bgr.jpg)

除了交换通道顺序外, 甚至可以传入自己定义的通道分量.

```py
import PIL.Image

im = PIL.Image.open('/img/jp.jpg')
_, g, b = im.split()
# 创建一个新的 r 通道分量, 注意 mode 值为 'L'
r = PIL.Image.new('L', im.size, color=255)

im = PIL.Image.merge('RGB', (r, g, b))
im.show()
```

![img](../../img/pil/channel/jp_r255.jpg)

## 色彩模式

有三种常见的图像色彩模式, 它们分别是:

- 单通道, 即灰度图.
- 三通道, 即 RGB 色彩模式, 每个像素点都存了 3 个无符号 8 位数字, 分别代表红绿蓝.
- 四通道, 即 RGBA 色彩模式, 它们在 RGB 的基础上加了一个透明度通道.

通常不同的文件封装格式对应不同的色彩模式, 例如 .jpg 是三通道, 而 .png 是四通道. 但唯一相同的是, 无论任何封装格式, 都必须先将图像还原为矩阵才能在计算机上显示.
