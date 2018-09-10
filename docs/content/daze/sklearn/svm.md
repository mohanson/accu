# SVM

SVM(支持向量机)可用与分类, 回归与异常检测.

对于二维数据的二分类问题而言, 一个普通的 SVM 就是一条直线，用来完美划分两类. 但是, 能同时划分两类数据的直线有无数多条, 我们需要的是恰好在两类数据的中间, 距离两个类的点一样远的直线. 我们称它为 **最优分类超平面**. 对于二维数据而言, 最优分类超平面是一条直线, 但是对三维数据而言, 最优分类超平面是一个面(即 N 维数据的最优分类超平面为 N-1 维).

**什么是 SVM**

![img](/img/daze/sklearn/svm/appear1.jpg)

寻找一条离苹果和香蕉之间距离(margin)最大的直线. 其中距离, 即点到直线的距离; 约束条件为所有苹果和香蕉到直线的距离大于等于 margin.
用数学表达式表示:

$$
y_i(w^Tx_i+b) >= 1, AAi
$$

**如果香蕉和苹果不能用直线分割呢?**

![img](/img/daze/sklearn/svm/appear2.jpg)

低维非线性的分界线其实在高维是可以线性分割. 设想在二维空间中的如果样本向量 v 距离原点(0, 0)的距离为 1 以内分类被标记为 0, 其余都是1, 同样是在二维的情况下是线性不可分得, 此时可以构造一个这样的函数:

$$
f(x, y) = {
    (1, x^2+y^2>=1),
    (0, x^2+y^2<1),
:}
$$

即 $$z=x^2+y^2$$, 此时二维空间线性不可分的点在三维空间中线性可分. 这个构造的过程 SVM 有通用的方法可以解决, 就是使用核函数进行构造. 几个常用的核函数如线性核函数, 多项式核函数, 径向基核函数, 高斯核函数等.

核函数的目的很明确: 就是在当前维度空间中的样本线性不可分的就一律映射到高维中去, 在高维空间中找到超平面, 得到超平面方程. 而在更高维的超平面上的方程实际上并没有增加更多的维度变量. 例如, 在研究二维空间上的向量分类问题时, 经过核函数映射, 最后得到的超平面变成了二维空间中的曲线(但同时也是三维空间中的一次方程).

**如果香蕉和苹果有交集呢?**

![img](/img/daze/sklearn/svm/appear3.jpg)

即使做了升维, 香蕉与苹果依然不能线性分割. 我们需要调整模型, 以使得在保证不可分的情况下, 尽量找到最优分类超平面. 通常状态下, 一个离群点(可能是噪声)可以造成超平面的移动, 间隔缩小, 以前的模型对噪声非常敏感. 再有甚者, 如果离群点在另外一个类中, 那么这时候就是线性不可分了.

这时候我们应该允许一些点游离并在在模型中违背限制条件(函数间隔大于 1). 通过引入**松弛变量**允许错误的分类.

$$
y_i(w^Tx_i+b) >= 1-xi_i, AAi
$$

$$xi_i$$ 为允许 $$x_i$$ 偏移分类平面的距离.

**如果还有梨呢?**

![img](/img/daze/sklearn/svm/appear4.jpg)

可以每个类别做一次SVM: 是苹果还是不是苹果? 是香蕉还是不是香蕉? 是梨子还是不是梨子? 从中选出可能性最大的. 这是 **one-versus-the-rest approach**.

也可以两两做一次SVM: 是苹果还是香蕉? 是香蕉还是梨子? 是梨子还是苹果? 最后三个分类器投票决定. 这是 **one-versus-one approace**.

# 代码实现

```py
import matplotlib.pyplot as plt
import sklearn.datasets
import sklearn.svm
import sklearn.metrics
import sklearn.model_selection
import numpy as np
plt.style.use('seaborn')

# 生成 512 个数据点, 所有数据以高斯分布形式分布在两个中心附近
x, y = sklearn.datasets.make_blobs(n_samples=512, centers=2, random_state=170)

# 分别测试核函数为 ['linear', 'poly', 'rbf', 'sigmoid']
for i, kernel in enumerate(['linear', 'poly', 'rbf', 'sigmoid']):
    plt.subplot(221 + i)

    clf = sklearn.svm.SVC(kernel=kernel)
    clf.fit(x, y)

    h = 0.02
    x_min, x_max = x[:, 0].min() - 1, x[:, 0].max() + 1
    y_min, y_max = x[:, 1].min() - 1, x[:, 1].max() + 1
    xx, yy = np.meshgrid(np.arange(x_min, x_max, h), np.arange(y_min, y_max, h))
    z = clf.predict(np.c_[xx.ravel(), yy.ravel()])
    z = z.reshape(xx.shape)

    plt.pcolormesh(xx, yy, z, cmap='Paired', alpha=0.5)
    plt.scatter(x[:, 0], x[:, 1], c=y, cmap='Paired', edgecolors='k')
    plt.axis('off')

plt.show()
```

![img](/img/daze/sklearn/svm/kernels.png)

# 后记

最近渐渐感到力不从心, 越深入发现涉及到的数学推导越多, 奈何精力有限, 往往只能浅尝辄止, 很多时候更是懒的看. 啊, 我已经是只废叶子了.

# 参考

- [1] sklearn: 支持向量机 [http://sklearn.apachecn.org/cn/0.19.0/modules/svm.html](http://sklearn.apachecn.org/cn/0.19.0/modules/svm.html)
- [2] 靠靠靠谱: 支持向量机(SVM)是什么意思? [https://www.zhihu.com/question/21094489/answer/117246987](https://www.zhihu.com/question/21094489/answer/117246987)
