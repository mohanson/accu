一个关于图像猫的二分类深度学习.

# 常用符号表示

$$x$$: 输入特征向量

$$y$$: 输出标签, 即 0 和 1

$$a$$: x 的预测值, 即 0 和 1

$$n_x$$: $$x$$ 的大小, 有时简写为 $$n$$. 如果 $$x$$ 是 64\*64\*3 的矩阵, 则 $$n_x=12288$$

$$(x, y)$$: 一个单独的样本. $$x$$ 是 $$n_x$$ 维度的特征, $$y$$ 是标签

$$m$$: 样本个数

$$m_text(train)$$: 训练集的样本个数

$$m_text(test)$$: 测试集的样本个数

$$X$$: 输入特征向量的集合, shape 是 $$(n, m)$$

$$Y$$: 输出标签的集合, shape 是 $$(1, m)$$

# 逻辑函数

逻辑函数(Sigmod 函数)是一种常见的 S 函数, 特征是在初始阶段大致是指数增长, 然后随着开始变得饱和, 增加变慢; 最后, 达到成熟时增加停止.

标准**逻辑函数**:

$$
sigma(z) = frac{1}{1+e^(-z)}
$$

![img](/img/dp_week2/logistic_curve.svg)

# 逻辑回归

逻辑回归(Logistic regression)是一种深度学习算法, 通常使用在深度学习二分类任务中. 给定特征向量 $$x$$, 令 $$a$$ 为实际 $$y$$ 的估计. 即在给定输入特征 $$x$$ 的情况下, $$y=1$$ 的概率. 表示为:

$$
a = P(y=1|x), a in [0, 1]
$$

线性回归的一般形式为 $$w^Tx+b$$. 其中 $$x$$ 与 $$w$$ 均是 $$n_x$$维的向量, b 为常数. 线性回归的作用是将数据集中各个离散的点通过$$w^Tx+b$$ 映射到一条直线上(因为 1\*n 的矩阵与 n\*1 的矩阵相乘结果为实数). 由于 $$w^Tx+b$$ 范围为 [-oo, +oo], 因此对线性回归做 sigmod:

$$a = sigma(w^Tx+b)$$, where $$sigma(z) = frac{1}{1+e^(-z)}$$

可知当 $$z$$ 是一个很大的正数时, $$sigma(z)$$ = 1, 当 $$z$$ 是一个绝对值很大的负数时, $$sigma(z)$$ = 0.

# 逻辑回归的代价函数

为了训练逻辑回归模型的参数 $$w$$ 和 $$b$$, 需要定义一个代价函数(Cost function). 为了让模型通过学习来调整参数, 需要给予 m 个样本的训练集. 训练目的是使 $$a^(i) ~~ y^(i), i in [0, m]$$(一个单一训练样本 i 的预测值约等于真实值, 这里使用带圆括号的上标 i 来表示第几个样本).

损失函数(Loss function) 用来衡量预测值 $$a$$ 与 $$y$$ 的实际值有多接近. 一个直观的做法是使用 $$L(a, y) = frac{1}{2}(a - y)^2$$, 但在逻辑回归中通常不这样做, 这样会导致局部最优值而非全局最优值. 在逻辑回归中使用的**损失函数**如下, 它与误差平方有着相似的效果:

$$
L(a, y) = -(ylog{a} + (1-y)log{(1-a)})
$$

损失函数是在单个训练样本中定义的, 它衡量在单个样本上的训练效果如何. 现在定义一个**代价函数**(cost function), 来衡量在全体样本上的表现, 其**定义为损失函数的平均值**:

$$
J(w, b) = frac{1}{m}sum_{i=1}^{m}L(a^(i), y^(i))
$$

逻辑回归的目的是将 $$J(w, b)$$ 的值降低到最小.

# 梯度下降

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

# 单个样本逻辑回归的导数计算

![img](/img/dp_week2/logistic_regression_recap.png)

$$
{:
    (dw_1 = x_1 * (a - y)),
    (dw_2 = x_2 * (a - y)),
    (db = a - y)
:}
$$

# 多个样本逻辑回归的导数计算

多个样本的逻辑回归的导数等于单个样本逻辑回归的导数的和的平均.

$$
{:
    (dw = 1 / m * X @ (A-Y).T),
    (db = 1 / m * np.sum(A-Y)),
:}
$$

# 代码实现

[https://github.com/mohanson/gist_deeplearning.ai](https://github.com/mohanson/gist_deeplearning.ai)

# 参考

- [1] Andrew Ng: Neural Networks and Deep Learning [https://www.coursera.org/learn/neural-networks-deep-learning/home/week/2](https://www.coursera.org/learn/neural-networks-deep-learning/home/week/2)
- [2] 维基: 逻辑函数 [https://zh.wikipedia.org/wiki/%E9%82%8F%E8%BC%AF%E5%87%BD%E6%95%B8](https://zh.wikipedia.org/wiki/%E9%82%8F%E8%BC%AF%E5%87%BD%E6%95%B8)
- [3] 维基: 逻辑回归 [https://en.wikipedia.org/wiki/Logistic_regression](https://en.wikipedia.org/wiki/Logistic_regression)
- [4] 维基: 导数 [https://zh.wikipedia.org/wiki/%E5%AF%BC%E6%95%B0](https://zh.wikipedia.org/wiki/%E5%AF%BC%E6%95%B0)
