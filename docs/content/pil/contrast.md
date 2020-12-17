# 数字图像处理/对比增强

图像的对比度反应了图片上亮区域和暗区域的层次感. 而反应到图像编辑上, 调整对比度就是在保证平均亮度不变的情况下, 扩大或缩小亮的点和暗的点之间的差异.

## 幂次变换

假设原图像为 r, 目标图像为 s, 转换函数为 T, 可以使用形式如下的表达式表示图像的处理过程.

s = T(r)

幂次变换转换函数的基本形式为 s = cr^λ, 其中 c 和 λ 为正常数. 幂次变换是常用的图像对比度调整算法中的一种.

![img](/img/pil/contrast/power_law.jpg)

由图可以看出, 当 λ < 1 时, 幂次变换将窄带输入暗值映射到宽带输出, 将宽带输入亮值映射到窄带输出值; 当 λ > 1 时, 幂次变换将宽带输入暗值映射到窄带输出值, 将窄带输入亮值映射到宽带输出值; 当 λ = 1 时, 即为正比变换.

## 代码实现

当原图像在暗处细节较多, 并且希望忽略一部分亮处细节时, 可取 c = 1, λ = 0.67.

```py
import PIL.Image
import scipy.misc
import numpy as np


def convert_3d(r):
    s = np.empty(r.shape, dtype=np.uint8)
    for j in range(r.shape[0]):
        for i in range(r.shape[1]):
            s[j][i] = (r[j][i] / 255) ** 0.67 * 255
    return s


im = PIL.Image.open('/img/jp.jpg')
im_mat = np.asarray(im)
im_converted_mat = convert_3d(im_mat)
im_converted = PIL.Image.fromarray(im_converted_mat)
im_converted.show()
```

## 效果展示

原图整体较为昏暗, 且在图像暗处有较多细节

![img](/img/pil/contrast/sample1.jpg)

经过 c = 1, λ = 0.67 幂次变换后, 暗处的细节清晰的展现

![img](/img/pil/contrast/sample2.jpg)

原图整体较为明亮, 且在图像亮处有较多细节

![img](/img/pil/contrast/sample3.jpg)

经过 c = 1, λ = 1.5 幂次变换后, 亮处的细节清晰的展现(观察图像左侧的花与女孩发梢)

![img](/img/pil/contrast/sample4.jpg)
