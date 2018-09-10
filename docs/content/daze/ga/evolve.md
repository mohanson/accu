# 遗传算法: 内存中的进化

这是个真实的故事.

从前在海岸边有一群扇贝在悠哉游哉地生活繁衍着. 它们自然是衣食不愁, 连房子也有了着落. 它们担忧的只有一件事: 每隔一段时间, 总有一个人来挖走它们之中的一部分. 当然啦, 挖回去干什么这大家都知道. 但扇贝们不知道的是, 这人的家族图腾是 Firefox 的图标, 所以他总是选择那些贝壳花纹长得比较不像 Firefox 图标的扇贝.

这种状况持续了好几十万代. 大家应该也猜到扇贝们身上发生什么事情了: 它们的贝壳上都印着很像 Firefox 图标的图案.

![img](/img/daze/ga/evolve/snapshot.png)

# 解析

上述故事是一个遗传算法的一部分. 下面, 就来实现这个遗传算法. 假设每个扇贝均由 100 个半透明且颜色随机的三角形组成:

- 决策变量: 100 个半透明三角形, 每个三角形的属性包括: 三个顶点的坐标, 透明度(0 - 0.45), 颜色.
- 个体评价方法: 100 个半透明三角形组合成而成的图案与 Firefox 图标进行逐像素比对, 并用一个较大的数减去逐像素向量距离的和作为个体适应度
- 选择算子: 轮盘选择 + 最优保留策略
- 交叉算子: 单点交叉
- 变异算子: 等位变异
- 运行参数: 迭代 12000 次, 种群大小 80, 交叉概率 0.6, 变异概率 0.008

# 代码实现

下面用 Python 实现上述故事.

```py
import copy
import os
import os.path

import numpy as np
import skimage.draw
import skimage.io
import skimage.transform

control_im_path = 'firefox.jpg'
save_dir = '/tmp/img'


class Base:
    def __init__(self, r, c, color, alpha):
        self.r = r
        self.c = c
        self.color = color
        self.alpha = alpha


class Gene:
    def __init__(self):
        self.base = []

    def copy(self):
        return copy.deepcopy(self)


class GA:
    def __init__(self):
        self.pop_size = 80
        self.dna_size = 100
        self.max_iter = 12000
        self.pc = 0.6
        self.pm = 0.008

        control_im = skimage.io.imread(control_im_path)
        self.control_im = skimage.transform.resize(
            control_im, (128, 128), mode='reflect', preserve_range=True).astype(np.float64)

    def decode(self, per):
        im = np.ones(self.control_im.shape, dtype=np.uint8) * 255
        for e in per.base:
            rr, cc = skimage.draw.polygon(e.r, e.c)
            skimage.draw.set_color(im, (rr, cc), e.color, e.alpha)
        return im

    def perfit(self, per):
        im = self.decode(per)
        assert im.shape == self.control_im.shape
        # 三维矩阵的欧式距离
        d = np.linalg.norm(np.where(self.control_im > im, self.control_im - im, im - self.control_im))
        # 使用一个较大的数减去欧式距离
        # 此处该数为 (self.control_im.size * ((3 * 255 ** 2) ** 0.5) ** 2) ** 0.5
        return (self.control_im.size * 195075) ** 0.5 - d

    def getfit(self, pop):
        fit = np.zeros(self.pop_size)
        for i, per in enumerate(pop):
            fit[i] = self.perfit(per)
        return fit

    def genpop(self):
        pop = []
        for _ in range(self.pop_size):
            per = Gene()
            for _ in range(self.dna_size):
                r = np.random.randint(0, self.control_im.shape[0], 3, dtype=np.uint8)
                c = np.random.randint(0, self.control_im.shape[1], 3, dtype=np.uint8)
                color = np.random.randint(0, 256, 3)
                alpha = np.random.random() * 0.45
                per.base.append(Base(r, c, color, alpha))
            pop.append(per)
        return pop

    def select(self, pop, fit):
        fit = fit - np.min(fit)
        fit = fit + np.max(fit) / 2 + 0.01
        idx = np.random.choice(np.arange(self.pop_size), size=self.pop_size, replace=True, p=fit / fit.sum())
        son = []
        for i in idx:
            son.append(pop[i].copy())
        return son

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
                a.base[p:], b.base[p:] = b.base[p:], a.base[p:]
                pop[i] = a
                pop[i + 1] = b
        return pop

    def mutate(self, pop):
        for per in pop:
            for base in per.base:
                if np.random.random() < self.pm:
                    base.r = np.random.randint(0, self.control_im.shape[0], 3, dtype=np.uint8)
                    base.c = np.random.randint(0, self.control_im.shape[1], 3, dtype=np.uint8)
                    base.color = np.random.randint(0, 256, 3)
                    base.alpha = np.random.random() * 0.45
        return pop

    def evolve(self):
        pop = self.genpop()
        pop_fit = self.getfit(pop)
        for _ in range(self.max_iter):
            chd = self.select(pop, pop_fit)
            chd = self.crosso(chd)
            chd = self.mutate(chd)
            chd_fit = self.getfit(chd)
            yield chd, chd_fit
            pop = chd
            pop_fit = chd_fit


ga = GA()
for i, (pop, fit) in enumerate(ga.optret(ga.evolve)()):
    j = np.argmax(fit)
    per = pop[j]
    per_fit = ga.perfit(per)
    print(f'{i:0>5} {per_fit}')
    skimage.io.imsave(os.path.join(save_dir, f'{i:0>5}.jpg'), ga.decode(per))
```

执行上述代码, 记得修改 `control_im_path` 与 `save_dir` 为可用地址. 不用一会, 就能在 `save_dir` 中见到每一代最优个体了. 当然, 跑完 3000 代还是需要一点时间的(大约半天~).

# 后记

实际上, 在生活和生产中, 很多时候并不需要得到一个完美的答案; 而很多问题如果要得到完美的答案的话, 需要很大量的计算. 所以, 因为**遗传算法能在相对较短的时间内给出一个足够好能凑合的答案**, 它从问世伊始就越来越受到大家的重视, 对它的研究也是方兴未艾. 当然, 它也有缺点, 比如说早期的优势基因可能会很快通过交换基因的途径散播到整个种群中, 这样有可能导致早熟(premature), 也就是说整个种群的基因过早同一化, 得不到足够好的结果. 这个问题是难以完全避免的.

其实, 通过微调参数和繁衍、变异、淘汰、终止的代码, 我们有可能得到更有效的算法. 遗传算法只是一个框架, 里边具体内容可以根据实际问题进行调整, 这也是它能在许多问题上派上用场的一个原因. 像这样可以适应很多问题的算法还有模拟退火算法, 粒子群算法, 蚁群算法, 禁忌搜索等等, 统称为元启发式算法(Meta-heuristic algorithms).

另外, 基于自然演化过程的算法除了在这里说到的遗传算法以外, 还有更广泛的群体遗传算法和遗传编程等, 它们能解决很多棘手的问题. 这也从一个侧面说明, 我们不一定需要一个智能才能得到一个构造精巧的系统.

# 参考

- [1] 方弦: 遗传算法: 内存中的进化 [http://songshuhui.net/archives/10462](http://songshuhui.net/archives/10462)
