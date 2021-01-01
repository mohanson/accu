# 杂项/Matplotlib

为了告诉别人自己的工作有多重要, 这时候有张图就好了呢!

![img](/img/misc/matplotlib/zhangyuge.jpg)

## 折线

```py
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn')

x = np.linspace(-np.pi, np.pi, 256)
ax = plt.subplot()
ax.plot(x, np.sin(x))

plt.show()
```

![img](/img/misc/matplotlib/line_1.png)

**样式**

```py
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn')

x = np.linspace(-np.pi, np.pi, 256)
ax = plt.subplot()

# 设置颜色 color
# 如下的 color 值是被支持的
# ==========  ========
# character   color
# ==========  ========
# 'b'         blue
# 'g'         green
# 'r'         red
# 'c'         cyan
# 'm'         magenta
# 'y'         yellow
# 'k'         black
# 'w'         white
# ==========  ========
# 另外, 可以使用全名('green'), 16 进制('#008000'), RGB 或 RGBA 元组(0,1,0,1) 或
# 灰度值(0.8)

# 设置样式 linestyle
# ================    ===============================
# character           description
# ================    ===============================
# ``'-'``             solid line style
# ``'--'``            dashed line style
# ``'-.'``            dash-dot line style
# ``':'``             dotted line style
# ``'.'``             point marker
# ``','``             pixel marker
# ``'o'``             circle marker
# ``'v'``             triangle_down marker
# ``'^'``             triangle_up marker
# ``'<'``             triangle_left marker
# ``'>'``             triangle_right marker
# ``'1'``             tri_down marker
# ``'2'``             tri_up marker
# ``'3'``             tri_left marker
# ``'4'``             tri_right marker
# ``'s'``             square marker
# ``'p'``             pentagon marker
# ``'*'``             star marker
# ``'h'``             hexagon1 marker
# ``'H'``             hexagon2 marker
# ``'+'``             plus marker
# ``'x'``             x marker
# ``'D'``             diamond marker
# ``'d'``             thin_diamond marker
# ``'|'``             vline marker
# ``'_'``             hline marker

# 设置曲线宽度 linewidth
ax.plot(x, np.sin(x), color='pink', linewidth=2, linestyle='--')

plt.show()
```

![img](/img/misc/matplotlib/line_2.png)

**坐标范围**

```py
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn')

x = np.linspace(-np.pi, np.pi, 256)
ax = plt.subplot()
ax.plot(x, np.sin(x))
# 设置 x 轴坐标宽度; 默认情况下, 左右会各保留一小段空白区间
ax.set_xlim(x.min(), x.max())

plt.show()
```

![img](/img/misc/matplotlib/line_3.png)

**填充**

```py
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn')

x = np.linspace(-np.pi*2, np.pi*2, 256)
ax = plt.subplot()
# 参数以 .plot 相似, 区别是会填充曲线的面积, 填充分界线为 y=c(c 为 x = 0 时的数)
# alpha 为透明度
ax.fill(x, np.sin(x), alpha=0.5)

# 当需要自定义分界线时, 使用 .fill_between 函数
ax.fill_between(x, 0, np.sin(x - np.pi / 4), alpha=0.5)

plt.show()
```

![img](/img/misc/matplotlib/line_4.png)

**坐标位置与坐标样式**

```py
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn')

x = np.linspace(-np.pi, np.pi, 256)
ax = plt.subplot()
ax.plot(x, np.sin(x))

# 移动坐标轴与设置坐标轴样式
ax.spines['bottom'].set_color('#646882')
ax.spines['bottom'].set_linewidth(1)
ax.spines['bottom'].set_position(('data', 0))
ax.spines['left'].set_color('#646882')
ax.spines['left'].set_linewidth(1)
ax.spines['left'].set_position(('data', 0))

plt.show()
```

![img](/img/misc/matplotlib/line_5.png)

**坐标刻度**

```py
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn')

x = np.linspace(-np.pi, np.pi, 256)
ax = plt.subplot()
ax.plot(x, np.sin(x))
# 手工指定坐标轴上的刻度
ax.set_xticks([-np.pi, -np.pi / 2, 0, np.pi / 2, np.pi])
ax.set_yticks([])

plt.show()
```

![img](/img/misc/matplotlib/line_6.png)

**函数名称**

```py
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn')

x = np.linspace(-np.pi, np.pi, 256)
ax = plt.subplot()
# 为曲线添加名称
ax.plot(x, np.sin(x), label='sin(x)')
ax.legend(loc='lower right')

plt.show()
```

![img](/img/misc/matplotlib/line_7.png)

## 散点图

```py
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn')

ax = plt.subplot()
x = np.linspace(-np.pi, np.pi, 16)
y = np.sin(x)

# s: 散点大小, 默认 20
# c: 颜色
# alpha: 透明度
ax.scatter(x, y, s=50, c='#FF0000', alpha=0.5)
plt.show()
```

![img](/img/misc/matplotlib/scatter_sample.png)

**样式**

```py
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn')

ax = plt.subplot()
x = np.linspace(-np.pi, np.pi, 16)
y = np.sin(x)

# marker: 散点样式. 全部可支持散点样式见 matplotlib.markers 模块
ax.scatter(x, y, s=50, c='#FF0000', marker='+', alpha=0.5)
plt.show()
```

![img](/img/misc/matplotlib/scatter_sample_mark.png)

**三维坐标**

```py
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D
import numpy as np

plt.style.use('seaborn')

ax = plt.subplot(projection='3d')

x = np.linspace(-np.pi, np.pi, 16)
y = np.sin(x)
z = np.linspace(-np.pi, np.pi, 16)

ax.scatter(x, y, z, s=50, c='#FF0000', alpha=0.5)

ax.set_zlabel('Z')
ax.set_ylabel('Y')
ax.set_xlabel('X')
plt.show()
```

![img](/img/misc/matplotlib/scatter_3d.png)

## 柱状图

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

![img](/img/misc/matplotlib/bar_1.png)

**颜色**

axes.bar 函数的 color 参数可以设置颜色; color 可以接受一个颜色, 也可以接受一个颜色数组

```py
ax.bar(X, Y, tick_label=['I', 'II', 'III', 'IV', 'V'], color=['pink', 'purple'])
```

![img](/img/misc/matplotlib/bar_2.png)

**填充**

axes.bar 函数的 hatch 参数可以填充样式, 可取值为: `/`, `\`, `|`, `-`, `+`, `x`, `o`, `O`, `.`, `*`

```py
ax.bar(X, Y, tick_label=['I', 'II', 'III', 'IV', 'V'], hatch='/')
```

![img](/img/misc/matplotlib/bar_3.png)

**堆叠柱状图**

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

![img](/img/misc/matplotlib/bar_4.png)

**柱状图并列**

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

![img](/img/misc/matplotlib/bar_5.png)

**条状图**

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

![img](/img/misc/matplotlib/bar_6.png)

## 饼图

```py
import matplotlib.pyplot as plt
plt.style.use('seaborn')

X = [15, 30, 45, 10]
labels = 'I', 'II', 'III', 'IV'

ax = plt.subplot()
ax.pie(X, labels=labels, autopct='%1.1f%%', startangle=90)

plt.show()
```

![img](/img/misc/matplotlib/pie_1.png)

**正圆**

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

![img](/img/misc/matplotlib/pie_2.png)

**强调**

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

![img](/img/misc/matplotlib/pie_3.png)
