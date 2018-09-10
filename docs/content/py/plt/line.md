# 折线

```py
import numpy as np
import matplotlib.pyplot as plt
plt.style.use('seaborn')

x = np.linspace(-np.pi, np.pi, 256)
ax = plt.subplot()
ax.plot(x, np.sin(x))

plt.show()
```

![img](/img/py/plt/line/line-1.png)

# 折线样式

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

![img](/img/py/plt/line/line-2.png)

# 坐标范围

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

![img](/img/py/plt/line/line-3.png)

# 填充曲线

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

![img](/img/py/plt/line/line-4.png)

# 坐标位置与坐标样式

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

![img](/img/py/plt/line/line-5.png)

# 坐标刻度

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

![img](/img/py/plt/line/line-6.png)

# 函数名称

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

![img](/img/py/plt/line/line-7.png)
