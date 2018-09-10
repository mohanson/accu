# 多重共线性的概念

对于模型 $$f(x, w) = w_0 + w_1x_1 + ... + w_px_p = w^Tx + b$$ 其基本假设之一是解释变量是互相独立的. 如果某两个或多个解释变量之间出现了相关性, 则称为**多重共线性**(Multicollinearity).

如果存在 $$c_1x_1 + c_2x_2 + … + c_px_p=0$$, 其中: $$c_p$$ 不全为0, 则称为解释变量间存在**完全共线性**. 如果存在 $$c_1x_1 + c_2x_2 + … + c_px_p + v = 0$$, $$v$$ 为随机误差项, 则称为**近似共线性**. 完全共线性指: $$X$$ 至少有一列向量可由其他列向量线性表示. 如 $$X_2 = lambdaX_1$$, 则 $$X_2$$ 对 $$Y$$ 的作用可由 $$X_1$$ 替代.

注意: 完全共线性情况并不多见. 一般出现的是在一定程度上的共线性, 即近似共线性. 引发多重共线性的原因例如经济变量相关的共同趋势, 在经济繁荣期, 收入, 消费, 投资, 价格都趋于增长; 在经济衰退期, 又同时趋于下降.

# 岭回归

岭回归通过对系数的大小施加惩罚来解决多重共线性问题. **当输入变量存在强相关性, 或者输入变量过多, 我们不想一一验证其是否存在相关性时, 适用岭回归**.

使用 `sklearn.linear_model.Ridge` 拟合一系列一维数据. 其中, $$alpha$$ 是控制系数收缩量的复杂性参数: $$alpha$$ 的值越大, 收缩量越大, 这样系数对共线性的鲁棒性也更强.

```py
import sklearn.datasets
import sklearn.linear_model
import sklearn.metrics

x = [
    [7, 26, 6, 60],
    [1, 29, 15, 52],
    [11, 56, 8, 20],
    [11, 31, 8, 47],
    [7, 52, 6, 33],
    [11, 55, 9, 22],
    [3, 71, 17, 6],
    [1, 31, 22, 44],
    [2, 54, 18, 22],
    [21, 47, 4, 26],
    [1, 40, 23, 34],
    [11, 66, 9, 12]
]
y = [78.5, 74.3, 104.3, 87.6, 95.9, 109.2, 102.7, 72.5, 93.1, 115.9, 83.8, 113.3]

regr = sklearn.linear_model.Ridge(alpha=1.0)
regr.fit(x, y)
y_pred = regr.predict(x)
print('Coefficients:', regr.coef_)
print('Mean squared error: %.2f' % sklearn.metrics.mean_squared_error(y, y_pred))
print('Variance score: %.2f' % sklearn.metrics.r2_score(y, y_pred))
```

```r
Coefficients: [ 1.55978657  0.58092437  0.10491954 -0.0957913 ]
Mean squared error: 3.40
Variance score: 0.98
```
