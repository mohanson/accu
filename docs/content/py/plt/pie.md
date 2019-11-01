# 饼图

```py
import matplotlib.pyplot as plt
plt.style.use('seaborn')

X = [15, 30, 45, 10]
labels = 'I', 'II', 'III', 'IV'

ax = plt.subplot()
ax.pie(X, labels=labels, autopct='%1.1f%%', startangle=90)

plt.show()
```

![img](/img/py/plt/pie/pie_1.png)

# 正圆

```py
import matplotlib.pyplot as plt
plt.style.use('seaborn')

X = [15, 30, 45, 10]
labels = 'I', 'II', 'III', 'IV'

ax = plt.subplot()
ax.pie(X, labels=labels, autopct='%1.1f%%', startangle=90)
# 设置 x 轴与 y 轴相等
ax.axis('equal')

plt.show()
```

![img](/img/py/plt/pie/pie_2.png)

# 强调

```py
import matplotlib.pyplot as plt
plt.style.use('seaborn')

X = [15, 30, 45, 10]
labels = 'I', 'II', 'III', 'IV'
explode = [0, 0.1, 0, 0]

ax = plt.subplot()
# explode 参数可以强调数据
ax.pie(X, explode=explode, labels=labels, autopct='%1.1f%%', startangle=90)
ax.axis('equal')

plt.show()
```

![img](/img/py/plt/pie/pie_3.png)
