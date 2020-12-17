# 数字图像处理/通道

数字图像处理系列文章最开始创作于 2015 年, 也是 Mohanson 的第一个长篇连载系列, 共耗时 1.5 年完成. 文章中的所记载的算法, 大部分来自《冈萨雷斯: 数字图像处理》书中的数学公式.

## 数字图像的本质

数字图像的本质是一个多维矩阵.

以一张 480x270 的 RGB 色彩空间图像为例, 编写如下代码:

![img](/img/pil/channel/jp.jpg)

```py
import scipy.misc

mat = scipy.misc.imread('/img/jp.jpg')
print(mat.shape)

# (270, 480, 3)
```

说明这个图像有 270 行, 480 列, 以及在色彩上有 3 个分量. 进一步分解该图片得到 R, G, B 三个通道分量:

```py
import PIL.Image

im = PIL.Image.open('/img/jp.jpg')
r, g, b = im.split()

r.show()
g.show()
b.show()
```

可得到如下三张图片, 每个分量单独拿出来都是一个 [270, 480, 1] 的矩阵.

R 通道的灰度图像:

![img](/img/pil/channel/jp_r.jpg)

G 通道的灰度图像:

![img](/img/pil/channel/jp_g.jpg)

B 通道的灰度图像:

![img](/img/pil/channel/jp_b.jpg)

## 交换通道

如果我们交换一下分量放置的顺序, 把 B 分量放进红色通道里, 把 G 分量放进绿色通道里, R 分量放进蓝色通道里, 可以得到如下一副图像:

```py
import PIL.Image

im = PIL.Image.open('/img/jp.jpg')
r, g, b = im.split()
im = PIL.Image.merge('RGB', (b, g, r))
im.show()
```

![img](/img/pil/channel/jp_bgr.jpg)

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

![img](/img/pil/channel/jp_r255.jpg)
