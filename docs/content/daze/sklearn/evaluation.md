# 训练集与测试集

学习预测函数的参数, 并在相同数据集上进行测试是一种错误的做法: 一个仅给出测试用例标签的模型将会获得极高的分数, 但对于尚未出现过的数据它则无法预测出任何有用的信息. 这种情况称为 overfitting(过拟合). 为了避免这种情况, 在进行(监督)机器学习实验时, 通常取出部分可利用数据作为 test set(测试数据集).

利用 scikit-learn 包中的 `train_test_split` 辅助函数可以很快地将实验数据集划分为任何训练集和测试集.

```py
import sklearn.model_selection
import sklearn.datasets

iris = sklearn.datasets.load_iris()

x_train, x_test, y_train, y_test = sklearn.model_selection.train_test_split(
    iris.data, iris.target, test_size=0.4, random_state=0)
print(x_train.shape, y_train.shape, x_test.shape, y_test.shape)
# (90, 4) (90,) (60, 4) (60,)
```

# 交叉验证

将数据集分为训练集和测试机, 大大减少了可用于训练的数据量的大小. 我们可以通过交叉验证解决. 交叉验证将数据集划分为 k 个子集, 然后使用 k-1 个子集用于模型训练, 剩下一个用于模型验证, 并重复 k 次. 交叉验证得出的性能指标是循环计算中每个值的平均值. 该方法虽然计算代价很高, 但是它不会浪费太多的数据, 在处理样本数据集较少的问题(例如, 逆向推理)时比较有优势.

![img](/img/daze/sklearn/evaluation/cross_validation_diagram.png)

使用交叉验证最简单的方法是在估计器和数据集上调用 `cross_val_score` 辅助函数.

```py
import sklearn.datasets
import sklearn.model_selection
import sklearn.svm

iris = sklearn.datasets.load_iris()

clf = sklearn.svm.SVC(kernel='linear', C=1)
scores = sklearn.model_selection.cross_val_score(clf, iris.data, iris.target, cv=5)
print('Accuracy: %0.2f (+/- %0.2f)' % (scores.mean(), scores.std() * 2))
# Accuracy: 0.98 (+/- 0.03)
```

交叉验证的主要作用如下:

1. 用于模型选择. 如评估 kNN, SVM 在同一数据集下的表现.
2. 用于模型调参.
3. 用于特征选择. 如评估应使用数据集中的哪些特征用于模型训练.

# 超参数与网格搜索

超参数, 即不直接在估计器内学习的参数. 在 scikit-learn 包中, 它们作为估计器类中构造函数的参数进行传递. 典型的例子有: 用于支持向量分类器的 C, kernel 和 gamma, 用于 Lasso 的 alpha 等. `sklearn.model_selection.GridSearchCV` 网格搜索通过穷尽所给出的所有超参数候选的排列组合, 自动选择最优参数组合. 网格法是目前最广泛使用的参数优化方法.

```py
import sklearn.datasets
import sklearn.model_selection
import sklearn.svm

iris = sklearn.datasets.load_iris()

# kernal 参数从 ['linear', 'rbf'] 选择, C 参数从 [1, 10] 选择,
# 因此总计 4 组候选参数
parameters = {'kernel': ('linear', 'rbf'), 'C': [1, 10]}
svc = sklearn.svm.SVC()
clf = sklearn.model_selection.GridSearchCV(svc, parameters)
clf.fit(iris.data, iris.target)

print(clf.best_params_) # 打印最优参数
# {'C': 1, 'kernel': 'linear'}
```

# 模型评估

通常情况下, 使用以下指标评估训练后的模型.

分类指标: [http://sklearn.apachecn.org/cn/0.19.0/modules/model_evaluation.html#classification-metrics](http://sklearn.apachecn.org/cn/0.19.0/modules/model_evaluation.html#classification-metrics)
