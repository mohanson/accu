# ReLU

线性整流函数(Rectified Linear Unit, ReLU),又称修正线性单元, 是一种人工神经网络中常用的激活函数(activation function), 通常指代以斜坡函数及其变种为代表的非线性函数.

![img](/img/dp_week1/ramp_function.svg)

通常意义下, 线性整流函数指代数学中的斜坡函数, 即

$$
f(x) = max(0, x)
$$


而在神经网络中, 线性整流作为神经元的激活函数, 定义了该神经元在线性变换 $$w^Tx + b$$ 之后的非线性输出结果. 换言之, 对于进入神经元的来自上一层神经网络的输入向量 $$x$$, 使用线性整流激活函数的神经元会输出

$$
max(0, w^Tx + b)
$$

至下一层神经元或作为整个神经网络的输出(取决现神经元在网络结构中所处位置).

# 监督式学习

监督式学习(Supervised learning), 是一个机器学习中的方法, 可以由训练资料中学到或建立一个模式(函数 / learning model), 并依此模式推测新的实例. 训练资料是由输入物件(通常是向量)和预期输出所组成. 函数的输出可以是一个连续的值(称为回归分析), 或是预测一个分类标签(称作分类).

Input(x)          | Output(y)              | Application
----------------- | ---------------------- | -------------------
Home features     | Price                  | Real Estate
Ad, user info     | Click on ad(0/1)       | Online Advertising
Image             | Object(1,...,1000)     | Photo tagging
Audit             | Text transcript        | Speech recognition
English           | Chinese                | Machine translation
Image, Radar info | Position of other cars | Autonomous driving

# 参考

- [1] Andrew Ng: Neural Networks and Deep Learning [https://www.coursera.org/learn/neural-networks-deep-learning/home/week/1](https://www.coursera.org/learn/neural-networks-deep-learning/home/week/1)
