首先初始化一下运行环境. 在该例程中使用一张 (270, 480, 4) 的 RGBA 图像作为原数据:

```py
import skimage.io
import numpy as np

im = skimage.io.imread('jp.jpg')
print(im.shape)
# (270, 480, 4)
```

# 图像分割与合并

```py
# 纵向分割为相等两份
r = np.split(im, 2, axis=1)
# 将两份图像纵向合并
im = np.concatenate(r, axis=1)
```

![img](/img/py/np/split/splits.png)

```py
# 横向分割为相等两份
r = np.split(im, 2, axis=0)
# 将两份图像横向合并
im = np.concatenate(r, axis=0)
```

```py
# 纵向分割为 0-50, 50-430, 430-480 三部分
r = np.split(im, [50, 430], axis=1)
```

# 通道分割与合并

```py
# 可以使用下标直接访问 RGBA 通道
r = im[:, :, 0]
g = im[:, :, 1]
b = im[:, :, 2]
a = im[:, :, 3]

# 或者使用 split 函数, 并调用 squeeze 移除最后一个维度
splits = np.split(im, 4, axis=2)
r = np.squeeze(splits[0], 2)
g = np.squeeze(splits[1], 2)
b = np.squeeze(splits[2], 2)
a = np.squeeze(splits[3], 2)


# 使用 stack 重建原始图像
im = np.stack((r, g, b, a), axis=2)

# 美美哒展示出来
import matplotlib.pyplot as plt
plt.style.use('seaborn')

_, axes = plt.subplots(2, 2)
axes[0][0].imshow(im)
axes[0][0].axis('off')
axes[0][1].imshow(r, cmap='Reds')
axes[0][1].axis('off')
axes[1][0].imshow(g, cmap='Greens')
axes[1][0].axis('off')
axes[1][1].imshow(b, cmap='Blues')
axes[1][1].axis('off')

plt.show()
```

![img](/img/py/np/split/channels.png)
