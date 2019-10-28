# 高通滤波

在[低通滤波](/content/pil/frequency_filter_lpf/)中我们说明了通过衰减图像傅里叶变换的高频信号可以平滑图像. 因为边缘和其他灰度急剧变化的区域与高频分量有关, 所以图像的锐化可以通过在频率域的高通滤波实现.

一个高通滤波器是从给定的低通滤波器用下式得到:

$$
H_{HP}(u, v) = 1 - H_{LP}(u, v)
$$

其中 $H_{LP}(u, v)$ 是低通滤波器的传递函数. 同样的, 高通滤波器也有理想(IHPF), 巴特沃斯(BHPF)和高斯高通滤波器(GHPF). 三种高通滤波器传递函数如下表所示:

\ | 理想 | 巴特沃斯 | 高斯
- | --- | --- | ---
H | $$H(u, v) = \begin{cases} 0 & D(u, v) \le D_0 \\\ 1 & D(u, v) > D_0 \\\ \end{cases}$$ | $$H(u, v) = \frac{1}{1 + [D_0 / D(u, v)]^{2n}}$$ | $$H(u, v) = 1 - e^{-D^2(u, v) / 2D_0^2}$$

# 实验结果

使用 $n=2$ 阶, 截止频率为 20 的巴特沃斯高通滤波器处理后的结果如下:

![img](/img/pil/frequency_filter_hpf/sample.jpg)

```py
# 实验代码
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

    # 截止频率为 20
    d0 = 20
    # 2 阶巴特沃斯
    n = 2
    # 频率域中心坐标
    center = (r_ext_fu.shape[0] // 2, r_ext_fu.shape[1] // 2)
    h = np.empty(r_ext_fu.shape)
    # 绘制滤波器 H(u, v)
    for u in range(h.shape[0]):
        for v in range(h.shape[1]):
            duv = ((u - center[0]) ** 2 + (v - center[1]) ** 2) ** 0.5
            if duv == 0:
                h[u][v] = 0
            else:
                h[u][v] = 1 / ((1 + (d0 / duv)) ** (2*n))

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
im_mat = scipy.misc.fromimage(im)
im_converted_mat = convert_3d(im_mat)
im_converted = PIL.Image.fromarray(im_converted_mat)
im_converted.show()
```
