# 最优保留策略

最优保留策略指**将群体中最优的一部分个体不经过选择, 交叉和变异操作, 直接进入下一代**, 以避免优秀个体损失.

最优保留策略的执行过程如下:

1. 找出当前群体中适应度最高和最低的个体
2. 若当前群体中最优个体比历史最优个体适应度还高, 则以当前群体最优个体作为历史最优个体; 否则使用历史最优个体替换当前群体最差个体
3. 执行后续遗传算子(选择, 交叉, 变异等)

# 代码实现

- 复制上节代码, 增加作用于 evolve 函数的 optret 装饰器
- 调整种群大小为 4, 变异概率为 0.5

```py
import matplotlib.animation
import matplotlib.pyplot as plt
import numpy as np

plt.style.use('seaborn')


class GA:
    def __init__(self):
        self.pop_size = 4
        self.max_iter = 20
        self.pc = 0.6
        self.pm = 0.5
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

    def optret(self, f):
        def mt(*args, **kwargs):
            opt = None
            opf = None
            for pop, fit in f(*args, **kwargs):
                max_idx = np.argmax(fit)
                min_idx = np.argmax(fit)
                if opf is None or fit[max_idx] >= opf:
                    opt = pop[max_idx]
                    opf = fit[max_idx]
                else:
                    pop[min_idx] = opt
                    fit[min_idx] = opf
                yield pop, fit
        return mt

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
gaiter = ga.optret(ga.evolve)()

fig, ax = plt.subplots()
ax.set_xlim(-0.2, 5.2)
ax.set_ylim(-10, 7.5)
x = np.linspace(*ga.x_bound, 200)
ax.plot(x, ga.f(x))
sca1 = ax.scatter([], [], s=200, c='#CF6FC1', alpha=0.5)
sca2 = ax.scatter([], [], s=300, c='#ED8826', alpha=0.5)


def update(*args):
    pop, _ = next(gaiter)
    fx = ga.decode(pop)
    fv = ga.f(fx)
    i = np.argmax(fv)
    sca1.set_offsets(np.column_stack((fx, fv)))
    sca2.set_offsets(np.column_stack(([fx[i]], fv[i])))
    # plt.savefig(f'/tmp/img/{args[0]+1:0>2}.png')


ani = matplotlib.animation.FuncAnimation(fig, update, interval=200, repeat=False)
plt.show()
```

![img](/img/daze/ga/sga_optret/opt.gif)
