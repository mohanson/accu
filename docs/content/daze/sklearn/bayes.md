贝叶斯分类器用于解决分类问题. sklearn 中实现了三种不同的贝叶斯分类器, 分别是 `GaussianNB`, `MultinomialNB` 和 `BernoulliNB`.

# 高斯贝叶斯分类器

```py
import sklearn.datasets
import sklearn.naive_bayes
import sklearn.metrics

iris = sklearn.datasets.load_iris()
gnb = sklearn.naive_bayes.GaussianNB()
gnb.fit(iris.data, iris.target)

y_pred = gnb.predict(iris.data)
acc = sklearn.metrics.classification_report(iris.target, y_pred)
print(acc)
```

# partial_fit

如果训练集数据过大, 无法一次性读入内存, 贝叶斯分类器提供了 `partial_fit` 函数, 以进行动态数据加载, 用与递增式学习. 要注意的是, 第一次调用 `partial_fit` 时需要将 classes 全部传入.

```py
import numpy as np
import sklearn.datasets
import sklearn.metrics
import sklearn.naive_bayes

iris = sklearn.datasets.load_iris()
indices = np.arange(len(iris.data), dtype=np.int)
np.random.shuffle(indices)
x = iris.data[indices]
y = iris.target[indices]

indices = np.linspace(0, len(x), 4).astype(np.int)
x1 = x[indices[0]:indices[1]]
y1 = y[indices[0]:indices[1]]
x2 = x[indices[1]:indices[2]]
y2 = y[indices[1]:indices[2]]
x3 = x[indices[2]:indices[3]]
y3 = y[indices[2]:indices[3]]

gnb = sklearn.naive_bayes.GaussianNB()
gnb.partial_fit(x1, y1, classes=[0, 1, 2])
gnb.partial_fit(x2, y2)
gnb.partial_fit(x3, y3)

y_pred = gnb.predict(iris.data)
acc = sklearn.metrics.classification_report(iris.target, y_pred)
print(acc)
```

```
             precision    recall  f1-score   support

          0       1.00      1.00      1.00        50
          1       0.94      0.94      0.94        50
          2       0.94      0.94      0.94        50

avg / total       0.96      0.96      0.96       150
```
