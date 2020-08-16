# 一些重要噪声的概率密度函数

![img](/img/pil/noise/probability_density_of_noises.png)

**高斯噪声**

$$
p(z) = \frac{1}{\sqrt{2\pi}\sigma}e^{-(z - \bar z)^2 / 2\sigma^2}
$$

其中 $z$ 表示灰度值, $\bar z$ 表示 $z$ 的均值, $\sigma$ 表示 $z$ 的标准差. 当 $z$ 服从高斯分布时, 其值有 68% 落在范围 $[(\bar z - \sigma), (\bar z + \sigma)]$ 内, 有 95% 落在范围 $[(\bar z - 2\sigma), (\bar z + 2\sigma)]$ 内,

**瑞利噪声**

$$
p(z) = 
\begin{cases}
    \frac{2}{b}(z-a)e^{-(z-a)^2 / b} & z \ge a \\\
    0 & z < a
\end{cases}
$$

概率密度的均值和方差为 $\bar z = a + \sqrt{\pi b/4}$, $\sigma^2 = \frac{b(4-\pi)}{4}$

**伽马(爱尔兰)噪声**

$$
p(z) = 
\begin{cases}
    \frac{a^bz^{b-1}}{(b-1)!}e^{-az} & z \ge a \\\
    0 & z < a
\end{cases}
$$

概率密度的均值和方差为 $\bar z = \frac{b}{a}$, $\sigma^2 = \frac{b}{a^2}$

**指数噪声**

$$
p(z) = 
\begin{cases}
    ae^{-az} & z \ge a \\\
    0 & z < a
\end{cases}
$$

概率密度的均值和方差为 $\bar z = \frac{1}{a}$, $\sigma^2 = \frac{1}{a^2}$

**均匀噪声**

$$
p(z) = 
\begin{cases}
    \frac{1}{b-a} & a \le z \le b \\\
    0 & \text else
\end{cases}
$$

概率密度的均值和方差为 $\bar z = \frac{a+b}{2}$, $\sigma^2 = \frac{(b-a)^2}{12}$

**脉冲(椒盐)噪声**

$$
p(z) = 
\begin{cases}
    P_a & z = a \\\
    P_b & z = b \\\
    1-P_a-P_b & \text else
\end{cases}
$$

如果 b > a, 则灰度级 b 在图像中将显示一个亮点, 反之, 灰度级 a 在图像中将显示一个暗点. 若 $P_a$ 或 $P_b$ 为 0, 则脉冲噪声称为**单极脉冲**. 如果 $P_a$ 和 $P_b$ 两者均不为 0, 尤其是它们近似相等时, 称**双极脉冲**, 也称为**椒盐脉冲**(因为图像酷似被随机撒了胡椒颗粒和盐粉颗粒).

# 使用 numpy.random 生成指定类型的噪声

```py
import matplotlib.pyplot as plt
import numpy as np

# 高斯噪声: 均值为 0, 标准差为 64
x1 = np.random.normal(loc=0, scale=64, size=(256, 256))

# 瑞利噪声: (2 / b) ** 0.5 为 1
x2 = np.random.rayleigh(scale=64, size=(256, 256))

# 伽马噪声: (b-1) / a 为 2, 放大 32 倍
x3 = np.random.gamma(shape=2, scale=32, size=(256, 256))

# 指数噪声: a = 1/32
x4 = np.random.exponential(scale=32, size=(256, 256))

# 均匀噪声
x5 = np.random.uniform(low=0, high=1.0, size=(256, 256))

# 脉冲噪声
x6 = np.random.random_integers(low=0.1, high=2.0, size=(256, 256))

for i, x in enumerate([x1, x2, x3, x4, x5, x6]):
    ax = plt.subplot(23 * 10 + i + 1)
    ax.hist(x.reshape(x.size), 64, normed=True)
    ax.set_yticks([])
    ax.set_xticks([])
plt.show()
```

输出结果:

![img](/img/pil/noise/hist_of_noises.png)

# 使用噪声退化原图

代码大致与[数字图像处理-加性高斯白噪声与去噪](/content/pil/agwn/)一致.
