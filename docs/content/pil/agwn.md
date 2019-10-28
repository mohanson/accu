# 加性高斯白噪声

加性高斯白噪声(Additive white Gaussian noise，AWGN)在通信领域中指的是一种功率谱函数是常数(即白噪声), 且幅度服从[高斯分布](/content/math_normal_distribution/)的噪声信号. 这类噪声通常来自感光元件, 且无法避免.

# 加噪

numpy 中使用 `numpy.random.normal()` 函数生成正态分布数据.

```py
import numpy as np
import matplotlib.pyplot as plt

# 生成均值为 0, 标准差为 64 的正态分布数据
data = np.random.normal(0, 64, 1024 * 8)

# 在 plt 中画出直方图
plt.hist(data, 256, normed=1)
plt.show()
```

为图像添加高斯白噪声. 注意到添加完噪声的图像, 像素值可能低于 0 或高于 255, 此时应该对转换后的图像做一次对比拉伸.

```py
import PIL.Image
import scipy.misc
import numpy as np


def convert_2d(r):
    # 添加均值为 0, 标准差为 64 的加性高斯白噪声
    s = r + np.random.normal(0, 64, r.shape)
    if np.min(s) >= 0 and np.max(s) <= 255:
        return s
    # 对比拉伸
    s = s - np.full(s.shape, np.min(s))
    s = s * 255 / np.max(s)
    s = s.astype(np.uint8)
    return s


def convert_3d(r):
    s_dsplit = []
    for d in range(r.shape[2]):
        rr = r[:, :, d]
        ss = convert_2d(rr)
        s_dsplit.append(ss)
    s = np.dstack(s_dsplit)
    return s


im = PIL.Image.open('/img/jp.jpg')
im = im.convert('RGB')
im_mat = scipy.misc.fromimage(im)
im_converted_mat = convert_3d(im_mat)
im_converted = PIL.Image.fromarray(im_converted_mat)
im_converted.show()

```

**加噪后的图像**

![img](/img/pil/agwn/jp_agwn.jpg)

# 去噪

考虑一幅将噪声 $\eta(x, y)$ 加入到原始图像 $f(x, y)$ 形成的带有噪声的图像 $g(x, y)$, 即:

$$
g(x, y) = f(x, y) + \eta(x, y)
$$

这里假设每个坐标点 $(x, y)$ 上的噪声都不相关且均值为 0. 我们处理的目标就是通过人为加入一系列噪声图像 $g_i(x, y)$ 来减少噪声.如果对 K 幅带有不同噪声的图像取平均值, 即

$$
\bar g(x, y) = \frac{1}{K}\sum_{i=1}^Kg_i(x, y) = f(x, y) + \frac{1}{K}\sum_{i=1}^K\eta_i(x, y)
$$

当 K 足够大时, $\frac{1}{K}\sum_{i=1}^K\eta_i(x, y)$ 趋向于 0, 因此

$$
\bar g(x, y) = f(x, y)
$$

下面尝试对上述图片取 K=128 进行去噪

```py
import PIL.Image
import scipy.misc
import numpy as np


def convert_2d(r):
    # 添加均值为 0, 标准差为 64 的加性高斯白噪声
    s = r + np.random.normal(0, 64, r.shape)
    if np.min(s) >= 0 and np.max(s) <= 255:
        return s
    # 对比拉伸
    s = s - np.full(s.shape, np.min(s))
    s = s * 255 / np.max(s)
    s = s.astype(np.uint8)
    return s


def convert_3d(r):
    s_dsplit = []
    for d in range(r.shape[2]):
        rr = r[:, :, d]
        ss = convert_2d(rr)
        s_dsplit.append(ss)
    s = np.dstack(s_dsplit)
    return s


im = PIL.Image.open('/img/jp.jpg')
im_mat = scipy.misc.fromimage(im)

k = 128

im_converted_mat = np.zeros(im_mat.shape)
for i in range(k):
    im_converted_mat += convert_3d(im_mat)

im_converted_mat = im_converted_mat / k
im_converted_mat = im_converted_mat - np.full(im_converted_mat.shape, np.min(im_converted_mat))
im_converted_mat = im_converted_mat * 255 / np.max(im_converted_mat)
im_converted_mat = im_converted_mat.astype(np.uint8)

im_converted = PIL.Image.fromarray(im_converted_mat)
im_converted.show()
```

**去噪后的图像**

![img](/img/pil/agwn/jp_denoise.jpg)

可以看到去噪后的图像已经十分接近原始图像了. 读者可以自由选取 K=4, K=16 等不同值查看去噪效果.
