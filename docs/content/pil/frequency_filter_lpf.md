# 数字图像处理/频域滤波/低通滤波

一幅图像的边缘和其他尖锐的灰度转换对其傅里叶变换的高频信号有贡献. 因此, 在频域平滑(模糊)可通过对高频信号的衰减来达到. 因为 F(u, v) 的中心部分为低频信号, 边缘部分为高频信号, 如果将 F(u, v) 边缘部分屏蔽, 那么就相当于进行了低通滤波.

考虑三种滤波器: 理想滤波器, 巴特沃斯滤波器和高斯滤波器.

## 理想低通滤波器

在以原点为圆心, D₀ 为半径的圆内, 无衰减的通过所有频率, 而在该圆外阻断所有频率的滤波器称为理想低通滤波器(ILPF). 它由下面的函数所决定:

```text
H(u, v) = 1; D(u, v) <  D₀
        = 0; D(u, v) <= D₀
```

其中, D₀ 为一个正常数(称为截止频率), D(u, v) 是频率域中心点 (u, v) 与频率矩形中心的距离.

```py
# 理想低通滤波器代码实现
import numpy as np
import PIL.Image
import scipy.misc


def convert_2d(r):
    r_ext = np.zeros((r.shape[0] * 2, r.shape[1] * 2))
    for i in range(r.shape[0]):
        for j in range(r.shape[1]):
            r_ext[i][j] = r[i][j]

    r_ext_fu = np.fft.fft2(r_ext)
    r_ext_fu = np.fft.fftshift(r_ext_fu)

    # 截止频率为 100
    d0 = 100
    # 频率域中心坐标
    center = (r_ext_fu.shape[0] // 2, r_ext_fu.shape[1] // 2)
    h = np.empty(r_ext_fu.shape)
    # 绘制滤波器 H(u, v)
    for u in range(h.shape[0]):
        for v in range(h.shape[1]):
            duv = ((u - center[0]) ** 2 + (v - center[1]) ** 2) ** 0.5
            h[u][v] = duv < d0

    s_ext_fu = r_ext_fu * h
    s_ext = np.fft.ifft2(np.fft.ifftshift(s_ext_fu))
    s_ext = np.abs(s_ext)
    s = s_ext[0:r.shape[0], 0:r.shape[1]]

    for i in range(s.shape[0]):
        for j in range(s.shape[1]):
            s[i][j] = min(max(s[i][j], 0), 255)

    return s.astype(np.uint8)


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
im_converted_mat = convert_3d(im_mat)
im_converted = PIL.Image.fromarray(im_converted_mat)
im_converted.show()
```

![img](../../img/pil/frequency_filter_lpf/ilpf_sample.jpg)

如上图所示, 使用理想低通滤波器可以看到明显的振铃状波纹, 因此应用中很少采用理想低通滤波器.

## 巴特沃斯低通滤波器

截止频率位于距原点 D₀ 处的 n 阶巴特沃斯低通滤波器(BLPF)的传递函数为

```text
H(u, v) = 1 / [1 + [D(u, v) / D₀]²ⁿ]
```

与 ILPF 不同, BLPF 传递函数并没有在通过频率与滤除频率之间给出明显截止的尖锐的不连续性. 对于具有平滑传递函数的滤波器, 可在这样一点上定义截止频率, 即使 H(u, v) 下降为其最大值的某个百分比的点(如 50%).

```py
# 将理想低通滤波器的 convert_2d 函数修改一下
def convert_2d(r):
    r_ext = np.zeros((r.shape[0] * 2, r.shape[1] * 2))
    for i in range(r.shape[0]):
        for j in range(r.shape[1]):
            r_ext[i][j] = r[i][j]

    r_ext_fu = np.fft.fft2(r_ext)
    r_ext_fu = np.fft.fftshift(r_ext_fu)

    # 截止频率为 100
    d0 = 100
    # 2 阶巴特沃斯
    n = 2
    # 频率域中心坐标
    center = (r_ext_fu.shape[0] // 2, r_ext_fu.shape[1] // 2)
    h = np.empty(r_ext_fu.shape)
    # 绘制滤波器 H(u, v)
    for u in range(h.shape[0]):
        for v in range(h.shape[1]):
            duv = ((u - center[0]) ** 2 + (v - center[1]) ** 2) ** 0.5
            h[u][v] = 1 / ((1 + (duv / d0)) ** (2*n))

    s_ext_fu = r_ext_fu * h
    s_ext = np.fft.ifft2(np.fft.ifftshift(s_ext_fu))
    s_ext = np.abs(s_ext)
    s = s_ext[0:r.shape[0], 0:r.shape[1]]

    for i in range(s.shape[0]):
        for j in range(s.shape[1]):
            s[i][j] = min(max(s[i][j], 0), 255)

    return s.astype(np.uint8)
```

![img](../../img/pil/frequency_filter_lpf/blpf_sample.jpg)

归功于这种滤波器在低频到高频之间的平滑过渡, BLPF 没有产生可见的振铃效果.

## 高斯低通滤波器

高斯低通滤波器(GLPF)的传递函数为

```text
H(u, v) = e ^ [-D²(u, v) / 2D₀²]
```

其中, D₀ 是截止频率, 当 D(u, v) = D₀ 时候, GLPF 下降到最大值的 0.607 处.

```py
# 将理想低通滤波器的 convert_2d 函数修改一下
def convert_2d(r):
    r_ext = np.zeros((r.shape[0] * 2, r.shape[1] * 2))
    for i in range(r.shape[0]):
        for j in range(r.shape[1]):
            r_ext[i][j] = r[i][j]

    r_ext_fu = np.fft.fft2(r_ext)
    r_ext_fu = np.fft.fftshift(r_ext_fu)

    # 截止频率为 100
    d0 = 100
    # 频率域中心坐标
    center = (r_ext_fu.shape[0] // 2, r_ext_fu.shape[1] // 2)
    h = np.empty(r_ext_fu.shape)
    # 绘制滤波器 H(u, v)
    for u in range(h.shape[0]):
        for v in range(h.shape[1]):
            duv = ((u - center[0]) ** 2 + (v - center[1]) ** 2) ** 0.5
            h[u][v] = np.e ** (-duv**2 / d0 ** 2)

    s_ext_fu = r_ext_fu * h
    s_ext = np.fft.ifft2(np.fft.ifftshift(s_ext_fu))
    s_ext = np.abs(s_ext)
    s = s_ext[0:r.shape[0], 0:r.shape[1]]

    for i in range(s.shape[0]):
        for j in range(s.shape[1]):
            s[i][j] = min(max(s[i][j], 0), 255)

    return s.astype(np.uint8)
```
