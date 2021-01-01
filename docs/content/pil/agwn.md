# 数字图像处理/加性高斯白噪声与去噪

加性高斯白噪声(Additive white Gaussian noise，AWGN)在通信领域中指的是一种功率谱函数是常数(即白噪声), 且幅度服从高斯分布的噪声信号. 这类噪声通常来自感光元件, 且无法避免.

## 加噪

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
im_mat = np.asarray(im)
im_converted_mat = convert_3d(im_mat)
im_converted = PIL.Image.fromarray(im_converted_mat)
im_converted.show()
```

加噪后的图像

![img](/img/pil/agwn/jp_agwn.jpg)

## 去噪

考虑一幅将噪声 η 加入到原始图像 f 形成的带有噪声的图像 g, 即:

```text
g = f + η
```

这里假设原始图像 f 每个坐标点上的噪声都不相关且均值为 0. 我们处理的目标就是通过人为加入一系列噪声图像来减少噪声. 我们创建 k 个不同的噪声 η0, η1, ... ηk, 将之加入原始图像, 得到目标图像 g0, g1, ... gk. 则对 k 幅带有不同噪声的图像取平均值, 即

```text
r = (g0 + g1 + ... +gk) / k = f + (η0 + η1 + ... + ηk) / k
```

当 k 足够大时, (η0 + η1 + ... + ηk) / k 趋向于 0, 因此

```text
r = f
```

下面尝试对上述图片取 k=128 进行去噪

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
im_mat = np.asarray(im)

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

去噪后的图像

![img](/img/pil/agwn/jp_denoise.jpg)

可以看到去噪后的图像已经十分接近原始图像了. 读者可以自由选取 k=4, k=16 等不同值查看去噪效果.
