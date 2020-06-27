# 对比拉伸

低对比度的图像可由照明不足, 成像传感器动态范围太小, 甚至在图像获取过程中透镜光圈设置错误引起. 对比拉伸的思想是提高图像处理时灰度级的动态范围.

# 转换函数

$$
T(x) = (x - r_{min})(r_{max} - r_{min}) \cdot 255
$$

该函数将原图像 $[r_{min}, r_{max}]$ 的像素取值范围拉伸至 $[0, 255]$.

# 代码实现

```py
import PIL.Image
import scipy.misc
import numpy as np


def convert_2d(r):
    rmin = np.min(r)
    rmax = np.max(r)
    if rmin == rmax:
        return r
    s = np.empty(r.shape, dtype=np.uint8)
    for j in range(r.shape[0]):
        for i in range(r.shape[1]):
            s[j][i] = (r[j][i] - rmin) / (rmax - rmin) * 255
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
im_converted_mat = convert_3d(im_mat)
im_converted = PIL.Image.fromarray(im_converted_mat)
im_converted.show()
```
