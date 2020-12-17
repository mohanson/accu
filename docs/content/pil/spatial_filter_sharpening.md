# 数字图像处理/空间滤波/锐化滤波

图像锐化是补偿图像的轮廓, 增强图像的边缘及灰度跳变的部分, 使图像变得清晰, 分为空间域处理和频域处理两类. 图像锐化是为了突出图像上地物的边缘和轮廓, 或某些线性目标要素的特征. 这种滤波方法提高了地物边缘与周围像元之间的反差, 因此也被称为边缘增强.

## 拉普拉斯算子

在数学中, 微分是对函数的局部变化率的一种线性描述. 微分可以近似地描述当函数自变量的取值作足够小的改变时, 函数的值是怎样改变的. 最简单的各向同性微分算子是拉普拉斯算子. 一个二元图像函数 f(x, y) 的拉普拉斯变换定义为

![img](/img/pil/spatial_filter_sharpening/laplace.svg)

因为任意阶微分都是线性操作, 所以拉普拉斯变换也是一个线性操作.

为了更适合于图像处理, 这一方程必须表现为离散形式. 考虑到有两个变量, 因此, 我们在 x 方向上对二阶偏微分采用下列定义:

```text
f(x+1, y) + f(x-1, y) - 2f(x, y)
```

类似的, 在 y 方向上为

```text
f(x, y+1) + f(x, y-1) - 2f(x, y)
```

因此

```text
△f = f(x+1, y) + f(x-1, y) + f(x, y+1) + f(x, y-1) - 4f(x, y)
```

因此, 执行这一新定义的掩膜如下

```text
[[ 0, 1, 0],
 [ 1,-4, 1],
 [ 0, 1, 0]]
```

由于拉普拉斯算子是一种微分算子, 它的应用强调图像中灰度的突变和降低灰度慢变化的区域. 这将产生一幅把图像中的浅灰色边线和突变点叠加到暗背景中的图像. 将原始图像和拉普拉斯图像叠加在一起的简单方法可以保护拉普拉斯锐化后的效果, 同时又能复原背景信息.

除上述的掩膜外, 常见拉普拉斯算子还有

```text
[[ 0,-1, 0],
 [-1, 4,-1],
 [ 0,-1, 0]]
```

```text
[[-1,-1,-1],
 [-1, 8,-1],
 [-1,-1,-1]]
```

```text
[[ 1, 1, 1],
 [ 1,-8, 1],
 [ 1, 1, 1]]
```

使用拉普拉斯算子对图像进行增强的基本表示方法如下

```text
g(x, y)= f(x, y) - △f; 拉普拉斯算子中心系数为负
       = f(x, y) + △f; 拉普拉斯算子中心系数为正
```

## 代码实现

在机理中, 我们首先使用拉普拉斯算子过滤图像, 然后, 从原图像中减去该图像. 但在实际使用中, 通常使用单一掩膜扫描来实现. 假设使用 2 号拉普拉斯算子, 代入机理最后一步, 得到

```text
g(x, y) = f(x, y) - △f = 5f(x, y) - [f(x+1, y) + f(x-1, y) + f(x, y+1) + f(x, y-1)]
```

因此, g(x, y) 可以视为 f(x, y) 经过

```text
[[ 0,-1, 0],
 [-1, 5,-1],
 [ 0,-1, 0]]
```

过滤得到.

```py
import numpy as np
import PIL.Image
import scipy.misc
import scipy.signal


def convert_2d(r):
    # 滤波掩模
    window = np.array([
        [0, -1, 0],
        [-1, 5, -1],
        [0, -1, 0]
    ])
    s = scipy.signal.convolve2d(r, window, mode='same', boundary='symm')
    # 像素值如果大于 255 则取 255, 小于 0 则取 0
    for i in range(s.shape[0]):
        for j in range(s.shape[1]):
            s[i][j] = min(max(0, s[i][j]), 255)
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
im_converted_mat = convert_3d(im_mat)
im_converted = PIL.Image.fromarray(im_converted_mat)
im_converted.show()
```

## 效果展示

使用拉普拉斯算子对图像进行滤波, 得到图像像素突变部分(边缘)信息

![img](/img/pil/spatial_filter_sharpening/sample1.jpg)

将经过拉普拉斯过滤的图像与原图叠加, 就能得到原图的锐化

![img](/img/pil/spatial_filter_sharpening/sample2.jpg)
