# 遗传算法/愚弄神经网络

本文灵感来自于上一篇[生物进化模拟](evolve.md). 神经网络当前已经能识别各种图像, 网络会给出一个范围为 0 至 1 的置信度(confidence) 表明它有多少把握认为这张图片属于某一分类. 通过将神经网络的置信度作为遗传算法的适应度, 可以很容易生成人眼无法辨认, 而神经网络却有 99.99% 的把握认为是某一分类的图像(例如, 将一张充满无意义噪点的图像以 99.99% 的置信度分类为狮子).

在 2014 年已经有研究者研究该方面的知识, 论文地址是: [Deep Neural Networks are Easily Fooled:High Confidence Predictions for Unrecognizable Images](https://arxiv.org/pdf/1412.1897.pdf). 除了使用随机噪点愚弄神经网络之外, 文章中还研究了如何通过微调像素点, 得到一张标签为图书馆的狮子. 其实类似的研究还有很多, 比如 [All it takes to steal your face is a special pair of glasses](https://qz.com/1191083/hugh-masekelas-extraordinary-life-and-music/) 就实现了通过佩戴一副特殊眼镜, 让人脸识别系统将你误认为是他人.

本文目的是愚弄一个手写数字识别网络.

## 训练神经网络

这里使用 keras 来训练我们的手写数字识别模型. 直接用官方 examples 里的训练代码: [https://github.com/keras-team/keras/blob/master/examples/mnist_mlp.py](https://github.com/keras-team/keras/blob/master/examples/mnist_mlp.py), 记得在原始代码最后加上 `model.save_weights('mnist_mlp.h5')` 来保存模型到本地. keras 在该模型上给出的测试精度是 **98.40%**.

在完成训练后, 随机生成一个 28 * 28 的图片测试一下该模型:

```py
import keras.losses
import keras.models
import keras.optimizers
import numpy as np

model = keras.models.Sequential()
model.add(keras.layers.core.Dense(512, activation='relu', input_shape=(784, )))
model.add(keras.layers.core.Dropout(0.2))
model.add(keras.layers.core.Dense(512, activation='relu'))
model.add(keras.layers.core.Dropout(0.2))
model.add(keras.layers.core.Dense(10, activation='softmax'))
model.compile(
    loss=keras.losses.categorical_crossentropy,
    optimizer=keras.optimizers.RMSprop(),
    metrics=['accuracy']
)
model.load_weights('mnist_mlp.h5')


def predict(x):
    assert x.shape == (784, )
    y = model.predict(np.array([x]), verbose=0)
    return y[0]


x = np.random.randint(0, 2, size=784, dtype=np.bool)
r = predict(x)
print(r)
```

输出如下:

```
[  7.09424297e-09   0.00000000e+00   7.83010735e-04   0.00000000e+00
   0.00000000e+00   3.43550600e-14   9.99216914e-01   2.81605187e-19
   2.40218861e-36   2.99693766e-28]
```

## 开始调戏

代码和前几章基本一样, 唯一不同是使用神经网络作为遗传算法的适应度计算函数. 下示算法会初始化 80 张 28*28 的图片, 并将数据传入神经网络计算每张图片在某个数字上的得分, 如果在某一轮, 群体中最优秀的个体得分超过 0.99, 则结束进化, 并保存该最优个体.

```py
import os
import os.path

import keras.losses
import keras.models
import keras.optimizers
import numpy as np
import skimage.draw
import skimage.io
import skimage.transform

model = keras.models.Sequential()
model.add(keras.layers.core.Dense(512, activation='relu', input_shape=(784, )))
model.add(keras.layers.core.Dropout(0.2))
model.add(keras.layers.core.Dense(512, activation='relu'))
model.add(keras.layers.core.Dropout(0.2))
model.add(keras.layers.core.Dense(10, activation='softmax'))
model.compile(
    loss=keras.losses.categorical_crossentropy,
    optimizer=keras.optimizers.RMSprop(),
    metrics=['accuracy']
)
model.load_weights('mnist_mlp.h5')


class GA:
    def __init__(self, aim):
        self.aim = aim
        self.pop_size = 80
        self.dna_size = 28 * 28
        self.max_iter = 500
        self.pc = 0.6
        self.pm = 0.008

    def perfit(self, per):
        y = model.predict(np.array([per]), verbose=0)
        return y[0][self.aim]

    def getfit(self, pop):
        fit = np.zeros(self.pop_size)
        for i, per in enumerate(pop):
            fit[i] = self.perfit(per)
        return fit

    def genpop(self):
        return np.random.choice(np.array([0, 1]), (self.pop_size, self.dna_size)).astype(np.bool)

    def select(self, pop, fit):
        fit = fit - np.min(fit)
        fit = fit + np.max(fit) / 2 + 0.01
        idx = np.random.choice(np.arange(self.pop_size), size=self.pop_size, replace=True, p=fit / fit.sum())
        return pop[idx]

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


save_dir = 'mnist_ga_fooled'

for n in range(10):
    ga = GA(n)
    for i, (pop, fit) in enumerate(ga.optret(ga.evolve)()):
        j = np.argmax(fit)
        per = pop[j]
        per_fit = fit[j]
        print(f'{n} {per_fit}')
        if per_fit > 0.99:
            skimage.io.imsave(os.path.join(save_dir, f'{n}.bmp'), per.reshape((28, 28)) * 255)
            break
```

在目录 `mnist_ga_fooled` 下保存了最终生成的数字 0-9 的图片, 每张图片在对应分类器下都有 99% 以上的概率. 观察这些图片, 会发现它们只是一些无意义的噪点.
