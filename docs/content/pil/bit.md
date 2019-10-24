# 位图切割

设一幅灰度图像中的每一个像素都由 8 比特表示, 则图像转换为由 8 张 1 比特平面组成, 其范围从最低有效位的位平面 0 到最高有效位的位平面 7. 在 8 比特字节中, 平面 0 包含图像中像素的最低有效位, 而平面 7 则包含最高有效位. 较高阶位(尤其是前 4 位)包含了大多数在视觉上很重要的数据.

# 代码实现

```py
import PIL.Image
import scipy.misc
import numpy as np


flat = 7


def convert_2d(r):
    s = np.empty(r.shape, dtype=np.uint8)
    for j in range(r.shape[0]):
        for i in range(r.shape[1]):
            bits = bin(r[j][i])[2:].rjust(8, '0')
            fill = int(bits[-flat - 1])
            s[j][i] = 255 if fill else 0
    return s


im = PIL.Image.open('/img/jp.jpg')
im = im.convert('L')
im_mat = scipy.misc.fromimage(im)
im_conveted_mat = convert_2d(im_mat)

im_conveted = PIL.Image.fromarray(im_conveted_mat)
im_conveted.show()
```

# 实验结果
原图

![img](/img/pil/bit/jp.jpg)

第 7 个位平面

![img](/img/pil/bit/jp_bit7.jpg)

第 6 个位平面

![img](/img/pil/bit/jp_bit6.jpg)

第 5 个位平面

![img](/img/pil/bit/jp_bit5.jpg)

第 4 个位平面

![img](/img/pil/bit/jp_bit4.jpg)

第 3 个位平面

![img](/img/pil/bit/jp_bit3.jpg)

第 2 个位平面

![img](/img/pil/bit/jp_bit2.jpg)

第 1 个位平面

![img](/img/pil/bit/jp_bit1.jpg)

第 0 个位平面

![img](/img/pil/bit/jp_bit0.jpg)
