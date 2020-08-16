# 概览

scikit-learn 是基于 Python 语言的机器学习工具.

- 简单高效的数据挖掘和数据分析工具
- 可供大家在各种环境中重复使用
- 建立在 NumPy ，SciPy 和 matplotlib 上
- 开源，可商业使用 - BSD许可证

一般来说, 一个学习问题通常会考虑一系列 n 个样本数据, 然后尝试预测未知数据的属性. 如果每个样本是多个属性的数据(比如说是一个多维记录), 就说它有许多"属性", 或称 features(特征).

我们可以将学习问题分为几大类:

- `监督学习`, 其中数据带有一个附加属性, 即我们想要预测的结果值. 这个问题可以是:
	- `分类`: 样本属于两个或更多个类, 我们想从已经标记的数据中学习如何预测未标记数据的类别. 分类问题的一个例子是手写数字识别, 其目的是将每个输入向量分配给有限数目的离散类别之一. 我们通常把分类视作监督学习的一个离散形式(区别于连续形式), 从有限的类别中, 给每个样本贴上正确的标签.
	- `回归`: 如果期望的输出由一个或多个连续变量组成, 则该任务称为回归. 回归问题的一个例子是预测鲑鱼的长度是其年龄和体重的函数.
- `无监督学习`, 其中训练数据由没有任何相应目标值的一组输入向量 x 组成. 这种问题的目标可能是在数据中发现彼此类似的示例所聚成的组, 这种问题称为`聚类`, 或者, 确定输入空间内的数据分布, 称为`密度估计` , 又或从高维数据投影数据空间缩小到二维或三维以进行可视化.

**训练集和测试集**

机器学习是从数据的属性中学习, 并将它们应用到新数据的过程. 这就是为什么机器学习中评估算法的普遍实践是把数据分割成训练集(我们从中学习数据的属性)和测试集(我们测试这些性质).

# 示例: 手写数字识别

下面使用一个简单的手写数字识别例子介绍 sklearn 的工作模式. 可以看到, 其训练过程依然遵循**载入数据-定义模型-训练-预测**这样的基本规则.

```py
import sklearn.datasets
import sklearn.externals.joblib
import sklearn.metrics
import sklearn.svm

# 载入手写数字识别数据, 并分割为训练集与测试集(9:1)
digits = sklearn.datasets.load_digits()
n_samples = len(digits.data)
split_index = n_samples // 10 * 9
Xtr = digits.data[:split_index]
Ytr = digits.target[:split_index]
Xte = digits.data[split_index:]
Yte = digits.target[split_index:]

# 训练
clf = sklearn.svm.SVC(gamma=0.001, C=100)
clf.fit(Xtr, Ytr)

# 预测. 该模型精度为 0.96, 召回为 0.95.
Yte_pred = clf.predict(Xte)
acc = sklearn.metrics.classification_report(Yte, Yte_pred)
print(acc)

# 保存模型. 可以使用 sklearn.externals.joblib.load 函数重载模型.
sklearn.externals.joblib.dump(clf, '/tmp/svm.pkl')
```

# 参考
- [1] sklearn: 使用 scikit-learn 介绍机器学习 [http://sklearn.apachecn.org/cn/0.19.0/tutorial/basic/tutorial.html](http://sklearn.apachecn.org/cn/0.19.0/tutorial/basic/tutorial.html)
