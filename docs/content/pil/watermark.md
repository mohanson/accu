# 数字图像处理/水印

这里只介绍两种简单的水印算法: 简单可见水印与 LSB 不可见水印. 更加复杂的水印算法通常需要对图像做傅里叶变换.

## 简单可见水印

简单可见水印可由如下公式生成

$$
f_w = (1 - \alpha)f + \alpha w
$$

其中 $\alpha$ 控制水印和衬底的相对可见性, $f$ 为衬底, $w$ 为水印图片. 特别的, 当 $w$ 为 RGBA 模式时, 参与计算的 $\alpha$ 需要乘以水印的 A 通道与 255 的比值.

```py
import PIL.Image
import scipy.misc


im = scipy.misc.imread('/img/jp.jpg', mode='RGBA')
im_water = scipy.misc.imread('/img/watermark.jpg', mode='RGBA')

for x in range(im_water.shape[0]):
    for y in range(im_water.shape[1]):
        a = 0.3 * im_water[x][y][-1] / 255
        im[x][y][0:3] = (1 - a) * im[x][y][0:3] + a * im_water[x][y][0:3]

PIL.Image.fromarray(im).show()
```

以下图片是上述代码使用 $\alpha=0.3$ 的运行结果, 其中左上角为水印图片.

![img](/img/pil/watermark/sample01.png)

## LSB 不可见水印

在 [数字图像处理-位图切割](/content/pil/bit/) 一文中, 已经知晓了 8 比特位图像的最低阶比特对人眼感知几乎没有影响, 因此, 可以将水印图像的高阶比特位"插入"在衬底的低阶比特位中.

$$
f_w = 4(\frac{f}{4}) + \frac{w}{64}
$$

上述公式将原图使用无符号整数除以 4 并乘以 4, 来置最低两个比特位为 0, 并用 64 除 $w$, 将 $w$ 的两个最高比特位移到衬底的最低比特位上.

```py
import PIL.Image
import numpy as np
import scipy.misc

im = scipy.misc.imread('/img/jp.jpg', mode='RGBA')
im_water = scipy.misc.imread('/img/water.jpg', mode='RGBA')

# LSB 水印的第一步是滤除衬底最后 2 个低阶比特位
im = im // 4 * 4

for x in range(im_water.shape[0]):
    for y in range(im_water.shape[1]):
        im[x][y] += im_water[x][y] // 64

# 显示加水印后的图像
PIL.Image.fromarray(im.astype(np.uint8)).show()

im = im % 4 / 3 * 255
# 显示提取的水印图像
PIL.Image.fromarray(im.astype(np.uint8)).show()
```

显示加水印后的图像

![img](/img/pil/watermark/sample02.png)

显示提取的水印图像

![img](/img/pil/watermark/sample03.png)

要说明的是, LSB 水印非常脆弱, 诸如裁剪, 旋转, 缩放, 图像压缩等操作可以轻易破坏该水印.
