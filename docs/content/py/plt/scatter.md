# 散点图

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

![img](/img/py/plt/scatter/sample.png)

# 样式

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

![img](/img/py/plt/scatter/sample_mark.png)

# 三维坐标

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

![img](/img/py/plt/scatter/3d.png)
