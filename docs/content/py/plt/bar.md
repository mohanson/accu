# 柱状图

```py
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn')

X = np.arange(5) + 1
Y = np.array([0.5, 0.67, 0.71, 0.56, 0.8])

ax = plt.subplot()
ax.bar(X, Y, tick_label=['I', 'II', 'III', 'IV', 'V'])
# 在柱状图上标记 y 轴大小
for x, y in zip(X, Y):
    ax.text(x, y, f'{y:.2}', ha='center', va='bottom')

plt.show()
```

![img](/img/py/plt/bar/bar_1.png)

# 颜色

axes.bar 函数的 color 参数可以设置颜色; color 可以接受一个颜色, 也可以接受一个颜色数组

```py
ax.bar(X, Y, tick_label=['I', 'II', 'III', 'IV', 'V'], color=['pink', 'purple'])
```

![img](/img/py/plt/bar/bar_2.png)

# 填充

axes.bar 函数的 hatch 参数可以填充样式, 可取值为: `/`, `\`, `|`, `-`, `+`, `x`, `o`, `O`, `.`, `*`

```py
ax.bar(X, Y, tick_label=['I', 'II', 'III', 'IV', 'V'], hatch='/')
```

![img](/img/py/plt/bar/bar_3.png)

# 堆叠柱状图

使用 bottom 参数堆叠柱状图

```py
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn')

X = np.arange(5) + 1
Y1 = np.array([0.5, 0.67, 0.71, 0.56, 0.8])
Y2 = np.random.random(5)

ax = plt.subplot()
ax.bar(X, Y1, tick_label=['I', 'II', 'III', 'IV', 'V'], label='Y1')
ax.bar(X, Y2, bottom=Y1, label='Y2')

plt.legend()
plt.show()
```

![img](/img/py/plt/bar/bar_4.png)

# 柱状图并列

设置柱状图的 bar_width 实现柱状图并列

```py
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn')

bar_width = 0.8 / 2

X1 = np.arange(5) + 1
Y1 = np.random.random(5)
X2 = X1 + bar_width
Y2 = np.random.random(5)

plt.bar(X1, Y1, bar_width)
plt.bar(X2, Y2, bar_width)
plt.xticks(X1+bar_width / 2, ['I', 'II', 'III', 'IV', 'V'])
plt.show()
```

![img](/img/py/plt/bar/bar_5.png)

# 条状图

条状图与柱状图基本类似.

```py
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn')

X = np.arange(5) + 1
Y = np.random.random(5)

ax = plt.subplot()
ax.barh(X, Y)
ax.set_yticks(X)
ax.set_yticklabels(['I', 'II', 'III', 'IV', 'V'])

plt.show()
```

![img](/img/py/plt/bar/bar_6.png)
