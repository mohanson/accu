# 遗传算法简述

遗传算法(英语: Genetic Algorithm (GA)) 是计算数学中用于解决最佳化的搜索算法, 是进化算法的一种. 进化算法最初是借鉴了进化生物学中的一些现象而发展起来的, 这些现象包括遗传, 突变, 自然选择以及杂交等.

遗传算法通常实现方式为一种计算机模拟. 对于一个最优化问题, 一定数量的候选解(称为个体)可抽象表示为染色体, 使种群向更好的解进化. 传统上, 解用二进制表示(即 0 和 1 的串), 但也可以用其他表示方法. 进化从完全随机个体的种群开始, 之后一代一代发生. 在每一代中评价整个种群的适应度, 从当前种群中随机地选择多个个体(基于它们的适应度), 通过自然选择和突变产生新的生命种群, 该种群在算法的下一次迭代中成为当前种群.

- 选择(select): 根据各个个体的适应度, 按照一定规则或方法, 从第 t 代个体 P(t) 中选取一些优良个体遗传到下一代 P(t+1) 中
- 交叉(crossover): 将群体 P(t) 内的个体随机搭配成对, 对每一个个体, 以一定概率 pc 交换它们之间的部分染色体
- 变异(mutate): 对群体 P(t) 中的每一个个体, 以某一概率 pm 改变某一个或某一些基因座上的基因值为其他的等位基因

遗传算法的运算过程:
```
群体 P(t) -> 选择运算 -> 交叉运算 -> 变异运算 -> 群体 P(t+1) -> 解码 -> 解集合 -> 个体评价
```

# 基本遗传算法(SGA)的构成要素

基本遗传算法提供三个算子: 选择, 交叉和变异

- 染色体编码方法: 基本遗传算法使用固定长度的二进制符号串表示群体中的个体, 其等位基因由 0, 1 组成. 初始群体中的每个个体的基因值可用均匀分布的随机数产生.
- 个体适应度评价: 基本遗传算法按与个体适应度成正比的概率来决定当前群体中每个个体遗传到下一代群体中的机会的多少. 为正确计算这个概率, 这要求个体适应度大于等于 0.
- 遗传算子
    - 选择算子使用比例选择算子
    - 交叉算子使用单点交叉算子
    - 变异算子使用基本位变异算子或均匀变异算子
- 基本遗传算法的运行参数
    - M: 种群大小, 一般取 20-100
    - T: 终止进化代数, 一般取 100-500
    - PC: 交叉概率, 一般取 0.4-0.99
    - PM: 变异概率, 一般取 0.0001-0.1

**比例选择算子**

个体被选中并遗传到下一代的概率与其适应度大小成正比, 其运算过程为

1. 计算群体中所有个体的适应度总和
2. 计算每个个体的相对适应度大小, 它即为各个个体被遗传到下一代的概率
3. 确定被遗传到下一代的个体

**单点交叉算子**

单点交叉算子是最基本的交叉算子, 其运算过程为

1. 对群体中的个体进行两两随机配对
2. 对每一对配对的个体, 设置其某一基因座之后的位置为交叉点
3. 依设定交叉概率, 交换交叉点之后的基因, 从而产生两个新的个体

单点交叉示意运算如下:

```
A: 10110111|00  crossover  A': 10110111|11
B: 00011100|11  -------->  B': 00011100|00
```

**基本位变异算子**

依照变异概率, 将基因座上的基因变为随机等位基因

# 基本遗传算法在函数优化方面的应用举例

**例**: 求 $f(x)=sin(10x) \times x + cos(2x) \times x$ 在 [0, 5] 区间内的最大值.

**解**:

1. 确定决策变量和约束条件
2. 确定优化模型
3. 确定编码方式. 此处使用 10 位二进制编码表示 $x \in [0, 5]$ 范围
4. 确定解码方式. 即如何将 10 位二进制编码还原为变量 $x$
5. 确定个体评价方法. 此处直接使用 $f(x)$ 作为个体适应度评价.
6. 设计遗传算子
7. 设定遗传算子运行参数

Python 实现:

```py
import matplotlib.animation
import matplotlib.pyplot as plt
import numpy as np

plt.style.use('seaborn')


class GA:
    def __init__(self):
        self.pop_size = 80
        self.max_iter = 20
        self.pc = 0.6
        self.pm = 0.001
        self.dna_size = 10
        self.x_bound = [0, 5]

    def f(self, x):
        return np.sin(10 * x) * x + np.cos(2 * x) * x

    def encode(self, x):
        a = x / (self.x_bound[1] - self.x_bound[0]) * (2 ** self.dna_size - 1)
        a = int(a)
        return np.array(list(np.binary_repr(a).zfill(self.dna_size))).astype(np.uint8)

    def decode(self, per):
        return per.dot(1 << np.arange(self.dna_size)[::-1]) / (2**self.dna_size - 1) * self.x_bound[1]

    def perfit(self, per):
        x = self.decode(per)
        return self.f(x)

    def getfit(self, pop):
        x = self.decode(pop)
        r = self.f(x)
        return r

    def select(self, pop, fit):
        fit = fit - np.min(fit)
        fit = fit + np.max(fit) / 2 + 0.001
        idx = np.random.choice(np.arange(self.pop_size), size=self.pop_size, replace=True, p=fit / fit.sum())
        pop = pop[idx]
        return pop

    def crosso(self, pop):
        for i in range(0, self.pop_size, 2):
            if np.random.random() < self.pc:
                a = pop[i]
                b = pop[i + 1]
                p = np.random.randint(1, self.dna_size)
                a[p:], b[p:] = b[p:], a[p:]
                pop[i] = a
                pop[i + 1] = b
        return pop

    def mutate(self, pop):
        mut = np.random.choice(np.array([0, 1]), pop.shape, p=[1 - self.pm, self.pm])
        pop = np.where(mut == 1, 1 - pop, pop)
        return pop

    def evolve(self):
        pop = np.random.randint(2, size=(self.pop_size, self.dna_size))
        pop_fit = self.getfit(pop)
        yield pop, pop_fit
        for _ in range(self.max_iter - 1):
            chd = self.select(pop, pop_fit)
            chd = self.crosso(chd)
            chd = self.mutate(chd)
            chd_fit = self.getfit(chd)
            yield chd, chd_fit
            pop = chd
            pop_fit = chd_fit


ga = GA()
gaiter = ga.evolve()

fig, ax = plt.subplots()
ax.set_xlim(-0.2, 5.2)
ax.set_ylim(-10, 7.5)
x = np.linspace(*ga.x_bound, 200)
ax.plot(x, ga.f(x))
sca = ax.scatter([], [], s=200, c='#CF6FC1', alpha=0.5)


def update(*args):
    pop, _ = next(gaiter)
    fx = ga.decode(pop)
    fv = ga.f(fx)
    sca.set_offsets(np.column_stack((fx, fv)))
    # plt.savefig(f'/tmp/img/{args[0]+1:0>2}.png')


ani = matplotlib.animation.FuncAnimation(fig, update, interval=200, repeat=False)
plt.show()
```

![img](/img/daze/ga/sga/calc_max.gif)
