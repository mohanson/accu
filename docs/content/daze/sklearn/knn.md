# kNN 算法

k 近邻法 (k-Nearest Neighbor, kNN) 是机器学习所有算法中理论最简单, 最好理解的算法. 它是一种基本的分类与回归方法, 它的输入为实例的特征向量, 通过计算新数据与训练数据特征值之间的距离, 然后选取 k(k>=1) 个距离最近的邻居进行分类判断(投票法)或者回归. 如果 k=1, 那么新数据被简单地分配给其近邻的类.

对于分类问题: 输出为实例的类别. 分类时, 对于新的实例, 根据其 k 个最近邻的训练实例的类别, 通过多数表决等方式进行预测.

对于回归问题: 输出为实例的值. 回归时, 对于新的实例, 取其 k 个最近邻的训练实例的平均值为预测值.

k 近邻法分类的直观理解: 给定一个训练数据集, 对于新的输人实例, 在训练集中找到与该实例最邻近的 k 个实例. 这 k 个实例的多数属于某个类别, 则该输人实例就划分为这个类别. k 近邻法不具有显式的学习过程, 它是直接预测. 实际上它是利用训练数据集对特征向量空间进行划分, 并且作为其分类的"模型".

![img](/img/daze/sklearn/knn/KnnClassification.svg)

k 近邻算法例子. 测试样本(绿色圆形)应归入要么是第一类的蓝色方形或是第二类的红色三角形. 如果 k=3(实线圆圈) 它被分配给第二类, 因为有 2 个三角形和只有 1 个正方形在内侧圆圈之内. 如果 k=5(虚线圆圈) 它被分配到第一类(3 个正方形与 2 个三角形在外侧圆圈之内).

# 距离度量

kNN 算法要求数据的所有特征都可以做可比较的量化. 为了公平, 样本参数必须做一些归一化处理. 特征空间中两个实例点的距离是两个实例点相似度的反映. 一般取欧式距离. np 中使用 `np.linalg.norm(x1 - x2)` 计算欧式距离.

# 分类

实现一个 k=3 的手写数字分类器, 最后的测试精度达到 97%.

```py
import numpy as np
import sklearn.datasets
import sklearn.metrics
import sklearn.model_selection
import sklearn.neighbors

digits = sklearn.datasets.load_digits()
x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(
    digits.data, digits.target, test_size=0.25, random_state=0, stratify=digits.target)
print('x_train.shape', x_train.shape)
print('y_train.shape', y_train.shape)


def classify(x_train, y_train, k, x):
    sources = np.empty(y_train.shape)
    for i, e in enumerate(x_train):
        d = np.linalg.norm(e - x)  # 欧式距离
        sources[i] = d
    indices = np.argsort(sources)[:k]

    knn = {}
    for i in indices:
        l = y_train[i]
        if l in knn:
            knn[l] += 1
        else:
            knn[l] = 1
    return max(knn)


y_pred = np.empty(y_test.shape)
for i, e in enumerate(x_test):
    y_pred[i] = classify(x_train, y_train, 3, e)

acc = sklearn.metrics.classification_report(y_test, y_pred)
print(acc)
```

```
             precision    recall  f1-score   support

          0       1.00      1.00      1.00        45
          1       0.98      0.96      0.97        46
          2       0.98      0.98      0.98        44
          3       0.93      0.93      0.93        46
          4       1.00      0.96      0.98        45
          5       0.98      0.98      0.98        46
          6       0.98      1.00      0.99        45
          7       1.00      1.00      1.00        45
          8       0.95      0.91      0.93        43
          9       0.88      0.96      0.91        45

avg / total       0.97      0.97      0.97       450
```

原始 kNN 实现的搜索方式简单粗暴: 线性扫描. 通过计算输入样本与每个训练样本的距离, 找到距离最近的 k 个点. 当训练数据较大时, 非常耗费时间. sklean 中实现了三种搜索方式, 分别是 `BallTree`, `KDTree`, `brute-force`. `KDTree` 是一颗二叉树, `BallTree` 是 `KDTree` 的优化版本, 而 `brute-force` 就是原始的暴力线性扫描. 这里要着重说明的是, `KDTree` 与 `BallTree` 虽然优化了搜索速度, 但牺牲了精确度. 因此对于小数据集(如 n < 30), 使用 `brute-force` 仍然是一个最佳选择.

使用 sklearn 提供的代码使用过程如下:

```py
import sklearn.datasets
import sklearn.metrics
import sklearn.model_selection
import sklearn.neighbors

digits = sklearn.datasets.load_digits()
x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(
    digits.data, digits.target, test_size=0.25, random_state=0, stratify=digits.target)

# 参数 algorithm 可以是 ['auto', 'ball_tree', 'kd_tree', 'brute'] 其中的一个
# 此处使用默认值 'auto'
# 参数 weights 可以是 ['uniform', 'distance'] 其中的一个.
# uniform 为每个近邻分配统一的权重, 而 distance 分配权重与查询点的距离成反比.
# 此处使用默认值 'uniform'
nbrs = sklearn.neighbors.KNeighborsClassifier(n_neighbors=3)
nbrs.fit(x_train, y_train)

y_pred = nbrs.predict(x_test)

acc = sklearn.metrics.classification_report(y_test, y_pred)
print(acc)
```

# 回归

```py
import numpy as np
import matplotlib.pyplot as plt
import sklearn.neighbors

plt.style.use('seaborn')

np.random.seed(0)
X = np.sort(5 * np.random.rand(40, 1), axis=0)
T = np.linspace(0, 5, 500)[:, np.newaxis]
y = np.sin(X).ravel()
# Add noise to targets
y[::5] += 1 * (0.5 - np.random.rand(8))

n_neighbors = 5
for i, weights in enumerate(['uniform', 'distance']):
    knn = sklearn.neighbors.KNeighborsRegressor(n_neighbors, weights=weights)
    y_ = knn.fit(X, y).predict(T)

    plt.subplot(2, 1, i + 1)
    plt.scatter(X, y, c='k', label='data')
    plt.plot(T, y_, c='g', label='prediction')
    plt.axis('tight')
    plt.legend()
    plt.title("KNeighborsRegressor (k = %i, weights = '%s')" % (n_neighbors,
                                                                weights))
plt.show()
```

![img](/img/daze/sklearn/knn/regr.png)

# 参考

- [1] wiki: 最近邻居法 [https://zh.wikipedia.org/wiki/%E6%9C%80%E8%BF%91%E9%84%B0%E5%B1%85%E6%B3%95](https://zh.wikipedia.org/wiki/%E6%9C%80%E8%BF%91%E9%84%B0%E5%B1%85%E6%B3%95)
- [2] 华校专/王正林: Python大战机器学习.第四章.k 近邻法
- [3] sklearn: 最近邻 [http://sklearn.apachecn.org/cn/0.19.0/modules/neighbors.html](http://sklearn.apachecn.org/cn/0.19.0/modules/neighbors.html)
