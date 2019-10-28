利用 HOG + SVM 训练一个简单的图像分类器. 项目地址: [https://github.com/mohanson/hogsvm](https://github.com/mohanson/hogsvm)

# HOG

HOG(Histogram of Oriented Gradient: 梯度直方图) 特征在目标检测算法中非常流行. 其主要思想是**在一副图像中, 局部目标的表象和形状能够被梯度或边缘的方向密度分布很好地描述(本质: 梯度的统计信息, 而梯度主要存在于边缘的地方).**

在 [https://www.learnopencv.com/histogram-of-oriented-gradients/](https://www.learnopencv.com/histogram-of-oriented-gradients/) 这篇文章中有对 HOG 算法的详细介绍, 推荐完整阅读.


1. 提取感兴趣图像区域, 进行灰度化
2. 计算 X 方向与 Y 方向的梯度
```py
import numpy as np
import skimage.color
import skimage.io

im = skimage.color.rgb2gray(skimage.io.imread('/img/jp.jpg'))
gy, gx = [np.ascontiguousarray(g) for g in np.gradient(im)]
```
3. 计算梯度幅值 $g$ 和方向 $\theta$
```py
g = np.sqrt(gy**2 + gx**2)
t = np.arctan2(gy, gx)
```
4. 将图像分割为 8x8 的 cells 并计算每一个 cells 的 9-bins 梯度直方图. 梯度方向决定属于哪个 bin, 梯度大小决定 bin 的高度.
5. 将每相邻的 4 个 cells 的梯度直方图压扁为 1 维数据(9 x 1), 串联为 (36 x 1) 的新数据并进行标准化
6. 串联第五步所有数据

比如有原图 64 * 128, 则垂直方向有 8 个 cell, 水平方向有 16 个 cell, 每相邻四个 cell 组合为一个 block, 则垂直方向有 7 个 block, 水平方向有 15 个 block, 因此最终求得的 HOG 特征向量有 7 * 15 * 9 * 4 = 3780 维度.

```py
# 计算图像的 HOG 特征
import matplotlib.pyplot as plt
import skimage.color
import skimage.data
import skimage.exposure
import skimage.feature

image = skimage.color.rgb2gray(skimage.data.astronaut())

fg, hog_image = skimage.feature.hog(image, orientations=8, pixels_per_cell=(16, 16),
                                   cells_per_block=(1, 1), visualise=True)
print('fg ndim:', len(fg))
hog_image_rescaled = skimage.exposure.rescale_intensity(hog_image, in_range=(0, 10))


_, (ax1, ax2) = plt.subplots(1, 2, figsize=(8, 4), sharex=True, sharey=True)
ax1.axis('off')
ax1.imshow(image, cmap='gray')
ax1.set_title('Raw image')
ax2.axis('off')
ax2.imshow(hog_image_rescaled, cmap='gray')
ax2.set_title('Histogram of Oriented Gradients')
plt.show()
```

![img](/img/daze/ml/hog/astronaut.png)

# SVM

SVM(支持向量机) 是一系列可用于分类, 回归和异常值检测的有监督学习方法. 利用 HOG + SVM 可以进行图像分类任务.

```py
import sklearn.svm

X = [[0, 0], [1, 1]]
Y = [0, 1]

clf = sklearn.svm.SVC()
# 训练
clf.fit(X, Y)
# 预测
p = clf.predict([[0.7, 0.7]])[0]
print('predict of [0.7, 0.7]:', p)
# predict of [0.7, 0.7]: 1
```

# 参考
- [1] 维基: 方向梯度直方图 [https://zh.wikipedia.org/zh-hans/%E6%96%B9%E5%90%91%E6%A2%AF%E5%BA%A6%E7%9B%B4%E6%96%B9%E5%9B%BE](https://zh.wikipedia.org/zh-hans/%E6%96%B9%E5%90%91%E6%A2%AF%E5%BA%A6%E7%9B%B4%E6%96%B9%E5%9B%BE)
- [2] scikit-image: Histogram of Oriented Gradients [http://scikit-image.org/docs/dev/auto_examples/features_detection/plot_hog.html](http://scikit-image.org/docs/dev/auto_examples/features_detection/plot_hog.html)
- [3] Learn Opencv: Histogram of Oriented Gradients [https://www.learnopencv.com/histogram-of-oriented-gradients/](https://www.learnopencv.com/histogram-of-oriented-gradients/)
