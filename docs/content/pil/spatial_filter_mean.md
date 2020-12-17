# 数字图像处理/空间滤波/均值滤波

均值滤波器的输出是包含在滤波掩模领域内像素的简单平均值. 均值滤波器最常用的目的就是减噪. 然而, 图像边缘也是由图像灰度尖锐变化带来的特性, 所以均值滤波还是存在不希望的边缘模糊负面效应.

均值滤波还有一个重要应用, 即为了对感兴趣的图像得出一个粗略描述而模糊一幅图像. 这样, 那些较小物体的强度与背景揉合在一起了, 较大物体变得像斑点而易于检测. 掩模的大小由即将融入背景中的物体尺寸决定.

## 代码实现

使用一个 3*3 均值滤波器处理图像

```py
import numpy as np
import PIL.Image
import scipy.misc
import scipy.signal


def convert_2d(r):
    n = 3
    # 3*3 滤波器, 每个系数都是 1/9
    window = np.ones((n, n)) / n ** 2
    # 使用滤波器卷积图像
    # mode = same 表示输出尺寸等于输入尺寸
    # boundary 表示采用对称边界条件处理图像边缘
    s = scipy.signal.convolve2d(r, window, mode='same', boundary='symm')
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
