# 逻辑函数

线性模型除了进行回归, 还可以进行分类. 考虑到 $$f(x, w) = w^Tx + b$$ 是在 $$[-oo, +oo]$$ 上连续的, 不符合概率的取值范围 0 ~ 1, 因此我们考虑使用广义线性模型, 最理想的是单位阶跃函数:

$$
P(z) = {
    (0, z < 0),
    (0.5, z = 0),
    (1, z > 0),
:}
$$

但是阶跃函数不满足单调可导的性质, 因此我们退而求其次, 使用逻辑函数(对数概率函数)替代:

$$P(z) = frac{1}{1+e^(-z)}$$

```py
# 逻辑函数曲线
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn')

x = np.linspace(-10, 10, 100)
y = 1 / (1 + np.power(np.e, -1 * x))
plt.plot(x, y, label='1 / (1 + e^-z)')
plt.scatter([0], [0.5])
plt.legend(loc='lower right')
plt.show()
```

![img](/img/daze/sklearn/liner_model/logistic_regression/logistic_function.png)

# 代码示例

在 sklearn 中, `sklearn.linear_model.LogisticRegression` 实现了逻辑回归模型. 下面来实现以下 iris 数据集的分类. 注意我们使用了参数 `penalty='l1'` 和 `solver='saga'`. 对于大多数任务而言, 这两个参数均为最佳选择.

```py
import sklearn.datasets
import sklearn.linear_model
import sklearn.metrics
import sklearn.model_selection

iris = sklearn.datasets.load_iris()

x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(
    iris.data, iris.target, test_size=0.25, random_state=0, stratify=iris.target)

regr = sklearn.linear_model.LogisticRegression(penalty='l1', solver='saga', max_iter=100)
regr.fit(x_train, y_train)

y_pred = regr.predict(x_test)
acc = sklearn.metrics.classification_report(y_test, y_pred)
print(acc)
```

```
             precision    recall  f1-score   support

          0       1.00      1.00      1.00        13
          1       1.00      1.00      1.00        13
          2       1.00      1.00      1.00        12

avg / total       1.00      1.00      1.00        38
```
