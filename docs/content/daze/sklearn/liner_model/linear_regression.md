# 概览

最小二乘法(又称最小平方法)是一种数学优化技术. 它通过最小化**残差平方和**寻找数据的最佳函数匹配. 利用最小二乘法可以简便地求得未知的数据, 并使得这些求得的数据与实际数据之间误差的平方和为最小.

注: 真实值与预测值之间的误差称为残差, 误差的平方和称为残差平方和

# 示例

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

注意: 最小二乘法对 $$w$$ 的估计, 是基于模型中变量之间相互独立的基本假设的, 即输入向量 $$x$$ 中的任意两项 $$x_i$$ 和 $$x_j$$ 之间是相互独立的. 如果输入矩阵 $$X$$ 中存在线性相关或者近似线性相关的列, 那么输入矩阵 $$X$$ 就会变成或者近似变成奇异矩阵(singular matrix). 这是一种病态矩阵, 矩阵中任何一个元素发生一点变动, 整个矩阵的行列式的值和逆矩阵都会发生巨大变化. 这将导致最小二乘法对观测数据的随机误差极为敏感, 进而使得最后的线性模型产生非常大的方差, 这个在数学上称为**多重共线性**(multicollinearity).

# 参考
- [1] 维基: 最小二乘法 [https://zh.wikipedia.org/wiki/%E6%9C%80%E5%B0%8F%E4%BA%8C%E4%B9%98%E6%B3%95](https://zh.wikipedia.org/wiki/%E6%9C%80%E5%B0%8F%E4%BA%8C%E4%B9%98%E6%B3%95)
- [2] 于淼: 最小二乘法?为神马不是差的绝对值 [http://blog.sciencenet.cn/blog-430956-621997.html](http://blog.sciencenet.cn/blog-430956-621997.html)
