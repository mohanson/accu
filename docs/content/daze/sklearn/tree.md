# 概览

决策树(Decision Trees)是一个贪心算法, 它在特征空间上执行递归的二元分割. 决策树由节点和有向边组成, 内部节点表示一个特征或属性, 叶子节点表示一个分类. 决策树本质就是一系列的 if-then-else 语句.

构建决策树通常包含三个步骤:

1. 特征选择
2. 决策树生成
3. 决策树剪枝

构建决策树时通常将正则化的极大似然函数作为损失函数, 其学习目标是损失函数为目标函数的最小化. 构建决策树的算法通常是递归地选择最优特征, 并根据该特征对训练数据集进行分割, 其步骤如下:

1. 构建根节点，所有训练样本都位于根节点.
2. 选择一个最优特征. 通过该特征将训练数据分割成子集, 确保各个子集有最好的分类, 但要考虑下列两种情况:
    1. 若子集已能够被"较好地"分类, 则构建叶节点, 并将该子集划分到对应的叶节点去
    2. 若某个子集不能够被"较好地"分类, 则对该子集继续划分
3. 递归直至所有训练样本都被较好地分类, 或者没有合适的特征为止. 是否"较好地"分类, 可通过后面介绍的指标来判断.

通过该步骤生成的决策树对训练样本有很好的分类能力, 但是我们需要的是对未知样本的分类能力. 因此通常需要对已生成的决策树进行剪枝, 从而使得决策树具有更好的泛化能力. 剪枝过程是去掉过于细分的叶节点, 从而提高泛化能力.

特征选择主要基于以下几个指标: 熵, 基尼系数和方差.

# 熵

回忆一下信息论中有关熵(entropy)的定义. 设 X 是一个离散型随机变量, 其概率分布为

$$
P(X=x_i) = p_i, i=1, 2, 3, .., n
$$

则随机变量的熵为

$$
H(X) = - sum_(i=1)^np_ilogp_i
$$

其中, log 以 2 为底并定义 0log0 = 0.

**举个栗子**

例: 有变量 X, 它可能的取值有 0, 1, 2 三种, 其概率分别是 0.25, 0.5 和 0.25. 那么 X 的熵为: $$H(X) = -(1/4log{1/4} + 1/2log{1/2} + 1/4log{1/4}) = 1.5$$

**当随机变量只有两个取值时, 其概率与熵的关系**

```py
import math
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn')


def entropy(*c):
    return -sum([e * math.log2(e) if e != 0 else 0 for e in c])


p = np.linspace(0, 1, 50)
h = np.empty_like(p)

for i in range(50):
    h[i] = entropy(p[i], 1 - p[i])

plt.plot(p, h)
plt.ylabel('H')
plt.xlabel('P')
plt.show()
```

![img](/img/daze/sklearn/tree/ph.png)

可以看到, $$P=0.5$$ 时, 熵最大, 为 1.

对于数据集 D, 我们使用 $$H(D)$$ 刻画数据集 D 的熵. 给定特征 A, 定义**信息增益** $$g(D, A)=H(D) - H(D|A)$$. 信息增益刻画的时由于特征 A, 使得数据集 D 的不确定性减少的程度. 构建决策树时应选择信息增益最大的特征来划分数据集.

**例**: 有如下数据集 D, 求特征 A 的信息增益.

A | B | Y
- | - | -
0 | 0 | 0
0 | 1 | 0
1 | 0 | 0
1 | 1 | 1

**解**

$$
{
    (H(D) = -(0.75log0.75 + 0.25log0.25) = 0.81),
    (H(D|A=0) = -(1log1 + 0log0) = 0),
    (H(D|A=1) = -(0.5log0.5 + 0.5log0.5) = 1.0),
:}
$$

则: $$
H(D|A) = P(A=0) * H(D|A=0) + P(A=1) * H(D|A=0) = 0.5 * 0 + 0.5 * 1.0 = 0.5
$$

因此特征 A 的信息增益为 $$H(D) - H(D|A) = 0.81 - 0.5 = 0.31$$

# 决策树生成

基本的决策树的生成算法中, 典型的有 ID3, C4.5 和 CART 生成算法, 它们生成树的过程大致相似. ID3 是采用的信息增益作为特征选择的度量, 而 C4.5 则采用信息增益比, CART 与 C4.5 非常相似, 但它不同之处在于它支持数值目标变量(回归), 并且不计算规则集.

ID3 生成算法的步骤如下:

1. 使用所有没有使用的属性并计算与之相关的信息增益
2. 选取其中信息增益最大的属性
3. 生成包含该属性的节点

# 实战

`sklearn` 中有两类决策树, 它们均采用优化的 CART 决策树生成算法. CART(分类回归树)是一棵二叉树, 且每个非叶子节点都有两个孩子, 所以对于第一棵子树其叶子节点数比非叶子节点数多1. <del>我靠, 我已经写不动了.</del>

`sklearn` 中有两类决策数, 分别是 `DecisionTreeClassifier` 和 `DecisionTreeRegressor`, 分别用与解决分类和回归问题. 首先看一下应用 `DecisionTreeClassifier` 解决 iris 数据集**分类**:

```py
import sklearn.datasets
import sklearn.metrics
import sklearn.model_selection
import sklearn.tree

iris = sklearn.datasets.load_iris()

x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(
    iris.data, iris.target, test_size=0.25, random_state=0, stratify=iris.target)

clf = sklearn.tree.DecisionTreeClassifier()
clf.fit(x_train, y_train)

y_pred = clf.predict(x_test)  # 预测样本分类, 也可以使用 predict_proba 预测每个类的概率
acc = sklearn.metrics.classification_report(y_test, y_pred)
print(acc)
```

```
             precision    recall  f1-score   support

          0       1.00      1.00      1.00        13
          1       0.93      1.00      0.96        13
          2       1.00      0.92      0.96        12

avg / total       0.98      0.97      0.97        38
```

`DecisionTreeClassifier` 包含一系列可配置的参数, 详细参见: [http://sklearn.apachecn.org/cn/0.19.0/modules/generated/sklearn.tree.DecisionTreeClassifier.html#sklearn.tree.DecisionTreeClassifier](http://sklearn.apachecn.org/cn/0.19.0/modules/generated/sklearn.tree.DecisionTreeClassifier.html#sklearn.tree.DecisionTreeClassifier)

使用 `DecisionTreeRegressor` 解决**回归**问题. 下例回归一个带有随机噪声的正弦波:

```py
import matplotlib.pyplot as plt
import numpy as np
import sklearn.tree

rng = np.random.RandomState(1)
x = np.sort(5 * rng.rand(80, 1), axis=0)
y = np.sin(x).ravel()
y[::5] += 3 * (0.5 - rng.rand(16))

# 使用 min_samples_leaf=5 控制叶节点的样本数量, 防止过拟合.
# 这个值很小时意味着生成的决策树将会过拟合，然而当这个值很大
# 时将会不利于决策树的对样本的学习. 所以尝试 min_samples_leaf=5 作为初始值.
regr = sklearn.tree.DecisionTreeRegressor(max_depth=5, min_samples_leaf=5)
regr.fit(x, y)

x_test = np.arange(0.0, 5.0, 0.01)[:, np.newaxis]
y_test = np.sin(x_test).ravel()
y_pred = regr.predict(x_test)

print('Training score:', regr.score(x, y))
print('Testing score:', regr.score(x_test, y_test))

plt.figure()
plt.scatter(x, y, s=20, edgecolor='black', c='darkorange', label='data')
plt.plot(x_test, y_pred, color='cornflowerblue', label='max_depth=5', linewidth=2)
plt.xlabel('data')
plt.ylabel('target')
plt.title('Decision Tree Regression')
plt.legend()
plt.show()
```

```
Training score: 0.8062057896011524
Testing score: 0.9328689437179793
```

![img](/img/daze/sklearn/tree/regr.png)

# 可视化

经过训练, 我们可以使用 `export_graphviz` 导出器以 Graphviz 格式导出决策树. 以 iris 数据集分类为例:

```py
sklearn.tree.export_graphviz(clf, '/tmp/clf.graphviz')
```

然后使用 `dot -Tpng clf.phz -o /tmp/clf.png` 获得 png 格式的可视化图片(需要安装 graphviz 软件).

![img](/img/daze/sklearn/tree/clf.png)

# 参考

- [1] sklearn: 决策树 [http://sklearn.apachecn.org/cn/0.19.0/modules/tree.html](http://sklearn.apachecn.org/cn/0.19.0/modules/tree.html)
- [2] 华校专/王正林: Python大战机器学习.第二章.决策树
- [3] wiki: ID3 algorithm [https://en.wikipedia.org/wiki/ID3_algorithm](https://en.wikipedia.org/wiki/ID3_algorithm)
