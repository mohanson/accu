# 中值滤波

中值滤波是一种非线性空间滤波器, 它的响应基于图像滤波器包围的图像区域中像素的统计排序, 然后由统计排序结果的值代替中心像素的值. 中值滤波器将其像素邻域内的灰度中值代替代替该像素的值. 中值滤波器的使用非常普遍, 这是因为对于一定类型的随机噪声, 它提供了一种优秀的去噪能力, 比小尺寸的均值滤波器模糊程度明显要低. 中值滤波器对处理脉冲噪声(也称椒盐噪声)非常有效, 因为该噪声是以黑白点叠加在图像上面的.

与中值滤波相似的还有最大值滤波器和最小值滤波器.

# 代码实现

10 * 10 的中值滤波器实现

```py
import numpy as np
import PIL.Image
import scipy.misc
import scipy.ndimage


def convert_2d(r):
    n = 10
    s = scipy.ndimage.median_filter(r, (n, n))
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

# 效果展示

中值滤波能产生类似油彩一样的效果, 如下是使用 10 * 10 中值滤波器处理后的图像

![img](/img/pil/spatial_filter_medium/sample1.jpg)

如下是使用中值滤波去除椒盐噪声的示例. 从左至右分别为**原始图像**, 加入**椒盐噪声**后的图像, **均值滤波**后的图像与**中值滤波**后的图像

![img](/img/pil/spatial_filter_medium/sample2.jpg)
