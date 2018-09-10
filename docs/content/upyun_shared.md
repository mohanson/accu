# 深度学习背后的数学原理 <small>--upyun 分享</small>

# 一些深度学习项目

**换脸**

![img](https://www.dailydot.com/wp-content/uploads/45d/39/98db94ea5c2e7ba0-2048x1024.jpg)

**强化学习**

![img](http://ss.csdn.net/p?http://mmbiz.qpic.cn/mmbiz_gif/BnSNEaficFAZhrJ7tmeibfY97h06f2ZOzgsibz0j1d2ahpTUt6bS79MaicnDozriaia1ESIfibKVmEZ3EibMSiaoRh6tgcg/0?wx_fmt=gif&wxfrom=5&wx_lazy=1)

**图像风格转移**

![img](/img/neural_style_transfer/jp.jpg)
![img](/img/neural_style_transfer/jp_maplewood.jpg)
![img](/img/neural_style_transfer/jp_starry_night.jpg)
![img](/img/neural_style_transfer/jp_greyrain.jpg)

# 本次分享大纲

我们将训练一个神经网络, 让其能识别一张图片是否是猫.

1. 什么是数字图像
2. 数据集介绍
3. 常用符号表示
4. 线性回归
5. 逻辑回归
6. 逻辑回归的代价函数
7. 梯度下降
8. 逻辑回归的导数计算
9. 开始写代码

<iframe id="embed_dom" name="embed_dom" frameborder="0" style="display:block;width:525px; height:245px;" src="https://www.processon.com/embed/5ab761f9e4b018c271c58cd6"></iframe>

# 什么是数字图像

**数字图像的本质是一个多维矩阵**.

以一张 960x540 的 RGBA 色彩空间图像为例, 编写如下代码

![img](/img/pil/channel/jp.jpg)

```py
import scipy.misc

mat = scipy.misc.imread('/img/jp.jpg')
print(mat.shape)

# (540, 960, 4)
```
说明这个图像有 540 行, 960 列, 以及在色彩上有 4 个分量.

如果我们期望在程序中表示这张图片, 以 C 语言为栗子, 表示方式为一个三维数组:

<div style="font-size: 32pt">uint8 img[540][960][4]</div>
<br>

进一步分解该图片得到 R, G, B 三个通道分量:

```py
import PIL.Image

im = PIL.Image.open('/img/jp.jpg')
r, g, b, _ = im.split()

r.show()
g.show()
b.show()
```
得到如下三张图片, 每个分量单独拿出来都是一个 [540, 960, 1] 的矩阵

![img](/img/pil/channel/jp_r.jpg)
![img](/img/pil/channel/jp_g.jpg)
![img](/img/pil/channel/jp_b.jpg)

**如你所见, 它们并不是彩色的，而是一幅灰度图像**

# 数据集介绍

我们大概有 100 多张已经标记好的图片. 有一些是喵, 有一些不是喵...

![img](/img/upyun_shared/dataset_overview.png)

# 常用符号表示

下面开始讲解一些简单的算法, 在讲算法之前, 先事先约定一些符号表示.

$$x$$: 输入特征向量, 如 `猫1`. 注意这里保存的是 `猫1` 的多维矩阵形式, 而不是原始图片文件.

$$y$$: 输出标签, 即 0 和 1. 我们约定 `0 代表不是猫, 1 代表是猫`

$$a$$: x 的预测值, 即 0 和 1. 我们约定 `0 代表不是猫, 1 代表是猫`

$$(x, y)$$: 一个单独的样本. $$x$$ 是 $$n_x$$ 维度的特征, $$y$$ 是标签

$$m$$: 样本个数

$$X$$: 输入特征向量的集合, 是一个数组, 如 `[猫1, 不是猫2, 猫3, ..., 猫m]`

$$Y$$: 输出标签的集合, 如 `[1, 0, 1, ..., 1]`

![img](/img/upyun_shared/dataset.png)


# 线性回归

线性模型(Linear Model)是机器学习中应用最广泛的模型, 指通过样本特征的线性组合来进行预测的模型(即回归). 其中目标值是输入变量 x 的线性组合. 在数学概念中:

$$
f(x, w) = w_0 + w_1x_1 + ... + w_px_p = w^Tx + b
$$

其中 $$x=[x_1, x_2, ..., x_p]$$, $$w=[w_1, w_2, ..., w_p]$$, $$b$$ 为常数.

**当 w 和 x 只有一个时, 退化为我们熟悉的一个函数**:

![img](https://gss0.bdstatic.com/94o3dSag_xI4khGkpoWK1HF6hhy/baike/c0%3Dbaike92%2C5%2C5%2C92%2C30/sign=ac5dde34252eb938f86072a0b40bee50/0e2442a7d933c89529f945aedb1373f083020064.jpg)

**举个栗子**

**题: 在 xy 坐标系中有一系列按某一规则生成的随机点, 请使用线性回归回归这些点. 并估计, 当 x=0.15 时, y 取值多少?**

使用 `sklearn.linear_model.LinearRegression` 拟合一系列一维数据.

```py
import matplotlib.pyplot as plt
import numpy as np
import sklearn.datasets
import sklearn.linear_model
import sklearn.metrics

diabetes = sklearn.datasets.load_diabetes()
diabetes_X = diabetes.data[:, np.newaxis, 2]
print('X.shape:', diabetes_X.shape)
print('Y.shape:', diabetes.target.shape)

diabetes_X_train = diabetes_X[:-20]
diabetes_X_test = diabetes_X[-20:]
diabetes_y_train = diabetes.target[:-20]
diabetes_y_test = diabetes.target[-20:]

regr = sklearn.linear_model.LinearRegression()
regr.fit(diabetes_X_train, diabetes_y_train)
print(f'w={regr.coef_}, b={regr.intercept_}')

diabetes_y_pred = regr.predict(diabetes_X_test)

print('Coefficients:', regr.coef_)
print('Mean squared error: %.2f' % sklearn.metrics.mean_squared_error(diabetes_y_test, diabetes_y_pred))
print('Variance score: %.2f' % sklearn.metrics.r2_score(diabetes_y_test, diabetes_y_pred))

plt.style.use('seaborn')

_, axes = plt.subplots(2)
axes[0].scatter(diabetes_X_train, diabetes_y_train, color='red', alpha=0.5)
axes[0].plot(diabetes_X_train, regr.predict(diabetes_X_train), color='blue', alpha=0.5, linewidth=3)
axes[1].scatter(diabetes_X_test, diabetes_y_test, color='red', alpha=0.5)
axes[1].plot(diabetes_X_test, diabetes_y_pred, color='blue', alpha=0.5, linewidth=3)
plt.show()
```

```
X.shape: (442, 1)
Y.shape: (442,)
w=[938.23786125], b=152.91886182616167
Coefficients: [938.23786125]
Mean squared error: 2548.07
Variance score: 0.47
```

![img](/img/daze/sklearn/liner_model/linear_regression/sample.png)

要注意的是, 线性回归的结果并不一定是一条**线**. 比如试图回归有两个特征点和一个输出标签的数据时, 其回归结果为一个二维面.

```py
import matplotlib.pyplot as plt
import sklearn.datasets
import sklearn.linear_model
import sklearn.metrics
import numpy as np
from mpl_toolkits.mplot3d import Axes3D

diabetes = sklearn.datasets.load_diabetes()
diabetes_x = diabetes.data[:, 2:4]
diabetes_y = diabetes.target

regr = sklearn.linear_model.Ridge()
regr.fit(diabetes_x, diabetes_y)
print(f'w={regr.coef_}, b={regr.intercept_}')

diabetes_y_pred = regr.predict(diabetes_x)
print('Coefficients:', regr.coef_)
print('Mean squared error: %.2f' % sklearn.metrics.mean_squared_error(diabetes_y, diabetes_y_pred))
print('Variance score: %.2f' % sklearn.metrics.r2_score(diabetes_y, diabetes_y_pred))

plt.style.use('seaborn')
axes = plt.subplot(projection='3d')
axes.scatter(diabetes_x[:, 0], diabetes_x[:, 1], diabetes_y, s=50, c='#FF0000', alpha=0.5)
axes.set_zlabel('Z')
axes.set_ylabel('Y')
axes.set_xlabel('X')

surface_x = np.linspace(-0.2, 0.2, 50)
surface_y = np.linspace(-0.2, 0.2, 50)
surface_x, surface_y = np.meshgrid(surface_x, surface_y)
surface_z = regr.predict(np.stack([surface_x.flatten(), surface_y.flatten()], axis=1))
surface_z = surface_z.reshape((50, 50))
axes.plot_surface(surface_x, surface_y, surface_z, rstride=1, cstride=1, cmap=plt.cm.coolwarm)
plt.show()
```

![img](/img/upyun_shared/lr_3d.png)


# 逻辑回归

考虑到线性回归 $$f(x, w) = w^Tx + b$$ 是在 $$[-oo, +oo]$$ 上连续的, 不符合概率的取值范围 0 ~ 1, 因此我们考虑使用广义线性模型, 最理想的是单位阶跃函数:

$$
P(z) = {
    (0, z < 0),
    (0.5, z = 0),
    (1, z > 0),
:}
$$

![img](https://upload.wikimedia.org/wikipedia/commons/thumb/d/d9/Dirac_distribution_CDF.svg/488px-Dirac_distribution_CDF.svg.png)

但是阶跃函数不满足单调可导的性质, 因此我们退而求其次, 使用逻辑函数(对数概率函数)替代:

$$P(z) = frac{1}{1+e^(-z)}$$

逻辑函数(Sigmod 函数)是一种常见的 S 函数, 特征是在初始阶段大致是指数增长, 然后随着开始变得饱和, 增加变慢; 最后, 达到成熟时增加停止.

![img](/img/dp_week2/logistic_curve.svg)

logistic回归本质上是线性回归, 只是在特征到结果的映射中加入了一层函数映射, 即先把特征线性求和, 然后使用函数 $$P(z) = frac{1}{1+e^(-z)}$$ 作为假设函数来预测. 逻辑函数可以将连续值映射到 0 和 1 上. logistic 回归用来分类 0/1 问题, 也就是预测结果属于 0 或者 1 的二值分类问题.

**到目前为止, 我们已经有了一个函数:**

$$f(x) = frac{1}{1+e^(-w^Tx + b)}$$

**我们希望当 x 为一张猫的图片时, f(x) 尽可能大, 最好为 1; 当 x 为一张不是猫的图片时, f(x) 尽可能小, 最好为 0**

**我们希望当 x 为一张猫的图片时, f(x) 尽可能大, 最好为 1; 当 x 为一张不是猫的图片时, f(x) 尽可能小, 最好为 0**

**我们希望当 x 为一张猫的图片时, f(x) 尽可能大, 最好为 1; 当 x 为一张不是猫的图片时, f(x) 尽可能小, 最好为 0**

# 逻辑回归的代价函数

为了训练逻辑回归模型的参数 $$w$$ 和 $$b$$, 需要定义一个代价函数(Cost function). 为了让模型通过学习来调整参数, 需要给予 m 个样本的训练集. 训练目的是使 $$a^(i) ~~ y^(i), i in [0, m]$$(一个单一训练样本 i 的预测值约等于真实值, 这里使用带圆括号的上标 i 来表示第几个样本).

**损失函数**(Loss function) 用来衡量预测值 $$a$$ 与 $$y$$ 的实际值有多接近. 一个直观的做法是使用 $$L(a, y) = frac{1}{2}(a - y)^2$$, 但在逻辑回归中通常不这样做, 这样会导致局部最优值而非全局最优值. 在逻辑回归中使用的损失函数如下, 它与误差平方有着相似的效果:

$$
L(a, y) = -(ylog{a} + (1-y)log{(1-a)})
$$

损失函数是在单个训练样本中定义的, 它衡量在单个样本上的训练效果如何. 现在定义一个**代价函数**(cost function), 来衡量在全体样本上的表现, 其**定义为损失函数的平均值**:

$$
J(w, b) = frac{1}{m}sum_{i=1}^{m}L(a^(i), y^(i))
$$

逻辑回归的目的是将 $$J(w, b)$$ 的值降低到最小.

**假设如下数据集的真实标签与预测结果如下(概率)**

![img](/img/upyun_shared/loss.png)

可知其**代价** 为

$$
J(w, b) = (0.105 + 0.223 + 0.223 + 0.223 + 0.105) / 5 = 0.1758
$$

# 梯度下降

**什么是梯度?**

![img](https://upload.wikimedia.org/wikipedia/commons/0/0f/Gradient2.svg)

![img](/img/upyun_shared/1042406-20161017221342935-1872962415.png)

梯度的本意是一个向量（矢量），表示某一函数在该点处的方向导数沿着该方向取得最大值，即函数在该点处沿着该方向（此梯度的方向）变化最快，变化率最大（为该梯度的模）。

梯度下降的目的是寻找 $$w$$ 和 $$b$$ 以使 $$J(w, b)$$ 最小. $$J(w, b)$$ 是一个凸函数. 梯度下降法以初始点开始, 然后朝最陡的下坡方向走一步. 重复上述过程, 直到到达最低点(全局最优点).

![img](/img/dp_week2/gradient_descent.png)

梯度下降的公式是:

$$
w := w - alpha*frac{dJ(w, b)}{d(w)}
$$

$$
b := b - alpha*frac{dJ(w, b)}{d(b)}
$$

其中 $$alpha$$ 表示学习速率, $$frac{dJ(w, b)}{d(w)}$$ 表示 $$J(w, b)$$ 在 $$w$$ 处的导数.

通常情况下, 我们给定一个很小的学习速率, 如 0.001, 进行上万次的梯度下降迭代.

# 逻辑回归的导数计算

先来求单个样本的导数.

到现在为止我们先看这三个公式:

$$
f(x, w) = w^Tx + b
$$

$$
sigma(z) = frac{1}{1+e^(-z)}
$$

$$
L(a, y) = -(ylog{a} + (1-y)log{(1-a)})
$$

现在要研究 $$w$$ 和 $$b$$ 对 $$L(a, y) = -(ylog{a} + (1-y)log{(1-a)})$$ 的影响, 将第1, 2 个公式带入第三个公式, 可求得 $$w$$ 和 $$b$$ 对 $$L(a, y)$$ 的偏导数:

$$
{:
    (d_(w1) = x_1 * (a - y)),
    (d_(w2) = x_2 * (a - y)),
    (d_(b) = a - y)
:}
$$

**多个样本的逻辑回归的导数等于单个样本逻辑回归的导数的和的平均. 将 dw1, dw2, db 代入梯度下降公式并进行迭代, 即可求得使 J(w, b) 最小的 w 和 b 的值**

# 开始写代码

在写代码的时候, 为了方便计算, 我们将会把图片压缩成一维数据. 比如一个 10 * 10 的黑白图片, 在程序中可直接保存为一个长度为 100 的一维数组而不是 [10, 10] 的二维数组. 同样, 因为长度为 100 的一维数组有 100 个元素, 即 100 个特征点, 因此 $$w$$ 也是一个长度为 100 的数组.


戳这里的 github: [https://github.com/mohanson/gist_deeplearning.ai/tree/master/week2](https://github.com/mohanson/gist_deeplearning.ai/tree/master/week2)

戳这里的 github: [https://github.com/mohanson/gist_deeplearning.ai/tree/master/week2](https://github.com/mohanson/gist_deeplearning.ai/tree/master/week2)

戳这里的 github: [https://github.com/mohanson/gist_deeplearning.ai/tree/master/week2](https://github.com/mohanson/gist_deeplearning.ai/tree/master/week2)
