# Solana/私钥, 公钥与地址/私钥的密码学解释(一)

好吧, 这一章不是一篇易于理解的文章. 我将在这一章对 solana 的私钥做出一些密码学方面的解释, 这需要读者有一定的数学基础. 如果感觉到困难, 您完全可以跳过这一章内容, 我相信不会对后续学习产生任何阻碍. 作为我 solana 教程的一部分, 这篇文章花费了我最多的时间, 因此如果您下定决心阅读这篇文章, 相信看完之后会有一点的收获.

在正式进入密码学大门之前, 我们首先需要入门抽象代数. 代数主要研究的是运算规则. 一门代数, 其实都是从某种具体的运算体系中抽象出一些基本规则, 建立一个公理体系, 然后在这基础上进行研究. 一个集合再加上一套运算规则, 就构成一个代数结构.

## 群

代数里面的群(group)是由集合和二元运算(用符号 + 表示)构成的, 符合以下四个群公理的数学结构. 群公理的四个性质如下:

0. 加法封闭性: 对于群中的任意两个元素进行运算后, 结果仍然属于该群.
0. 加法结合律: 群中的运算满足结合律, 即对于群中的任意三个元素进行运算, 先计算前两个元素的运算结果, 然后再与第三个元素进行运算, 结果应该与先计算后两个元素的运算结果再与第三个元素进行运算的结果相同.
0. 加法单位元: 群中存在一个特殊的元素, 称为单位元, 对于群中的任意元素 a, 运算 a 与单位元的结果等于元素 a 本身, 即 a + e = e + a = a, 其中 e 表示单位元.
0. 加法逆元素: 群中的每个元素都有一个逆元素, 对于群中的任意元素 a, 存在一个元素 b, 使得 a + b = b + a = e, 其中 e 表示单位元.

如果我们添加第五条要求:

0. 加法交换律: a + b = b + a.

那么这个群就是**阿贝尔群**或**交换群**.

例: 整数集是否构成群? 自然数集呢?

答: 整数集是一个阿贝尔群. 自然数集不是一个群, 因为它不满足第四条群公理.

群拥有几个概念, 会在之后的文章中被提及.

0. 一个有限群的元素个数称为群的阶.
0. 一个群元素 p 的阶为最小的整数 k 使得 k * p 等于单位元.
0. 一个群元素 p 的阶如果等于群的阶, 则 p 称为该群的生成元, 且该群是一个循环群.

## 环

环在群的基础上多定义了一个群运算乘法, 用符号 x 表示.

0. 乘法封闭性: 对于环中的任意两个元素进行乘法运算后, 结果仍然属于该环.
0. 乘法结合律: 环中的乘法运算满足结合律, 即对于环中的任意三个元素进行乘法运算, 先计算前两个元素的乘法结果, 然后再与第三个元素进行乘法运算, 结果应该与先计算后两个元素的乘法结果再与第三个元素进行乘法运算的结果相同.
0. 乘法分配律: 环中的乘法运算对于加法运算满足左分配律和右分配律, 即对于环中的任意三个元素 a, b, c, 有 a * (b + c) = a * b + a * c 和 (b + c) * a = b * a + c * a.

## 域

域是一种代数结构, 由一个集合和两个二元运算(加法和乘法)组成. 域满足环的所有条件, 并且具有以下额外性质:

0. 乘法单位元: 域中存在一个特殊的元素, 称为乘法单位元, 对于域中的任意元素 a, a 与乘法单位元相乘的结果等于 a 本身, 即 a * 1 = 1 * a = a, 其中 1 表示乘法单位元.
0. 乘法逆元素: 对于域中的任意非零元素 a, 存在一个元素 b, 使得 a * b = b * a = 1, 其中 1 表示乘法单位元.

例: 整数集, 有理数集, 实数集和复数集是否构成域?

答: 整数集构成一个环但不构成域. 有理数集, 实数集和复数集均构成域.

## 素数有限域

有限域是包含有限个元素的域. 与其他域一样, 有限域是进行加减乘除运算都有定义并且满足特定规则的集合. 有限域最常见的例子是素数域, 也就是整数集对指定素数取模后构成的集合.

例: 有素数有限域为整数集对素数 23 取模, 求以下算式的值.

- 12 + 20
- 8 * 9
- 1 / 8

答:

- 12 + 20 = 32 % 23 = 9
- 8 * 9 = 72 % 23 = 3
- 由于 3 * 8 = 24 % 23 = 1, 因此 1 / 8 = 3

下面我们使用 python 代码实现一个素数有限域. 客观来讲, 它十分类似我们日常生活中使用的整数, 但区别在于我们需要对所有计算结果进行取模. 下面的代码拷贝自 [pabtc](https://github.com/mohanson/pabtc) 项目, 您可以使用 `pip install pabtc` 来获取这份代码.

```py
import json
import typing


class Fp:
    # Galois field. In mathematics, a finite field or Galois field is a field that contains a finite number of elements.
    # As with any field, a finite field is a set on which the operations of multiplication, addition, subtraction and
    # division are defined and satisfy certain basic rules.
    #
    # https://www.cs.miami.edu/home/burt/learning/Csc609.142/ecdsa-cert.pdf
    # Don Johnson, Alfred Menezes and Scott Vanstone, The Elliptic Curve Digital Signature Algorithm (ECDSA)
    # 3.1 The Finite Field Fp

    p = 0

    def __init__(self, x: int) -> None:
        self.x = x % self.p

    def __add__(self, data: typing.Self) -> typing.Self:
        assert self.p == data.p
        return self.__class__(self.x + data.x)

    def __eq__(self, data: typing.Self) -> bool:
        assert self.p == data.p
        return self.x == data.x

    def __mul__(self, data: typing.Self) -> typing.Self:
        assert self.p == data.p
        return self.__class__(self.x * data.x)

    def __neg__(self) -> typing.Self:
        return self.__class__(self.p - self.x)

    def __repr__(self) -> str:
        return json.dumps(self.json())

    def __sub__(self, data: typing.Self) -> typing.Self:
        assert self.p == data.p
        return self.__class__(self.x - data.x)

    def __truediv__(self, data: typing.Self) -> typing.Self:
        return self * data ** -1

    def __pos__(self) -> typing.Self:
        return self.__class__(self.x)

    def __pow__(self, data: int) -> typing.Self:
        return self.__class__(pow(self.x, data, self.p))

    def json(self) -> str:
        return f'{self.x:064x}'

    @classmethod
    def nil(cls) -> typing.Self:
        return cls(0)

    @classmethod
    def one(cls) -> typing.Self:
        return cls(1)
```

使用代码验证上面的例题如下.

```py
Fp.p = 23
assert Fp(12) + Fp(20) == Fp(9)
assert Fp(8) * Fp(9) == Fp(3)
assert Fp(8) ** -1 == Fp(3)
```

您可能注意到了, 有限域的除法是一个特殊情况. 当我们试图求 a / b 时, 我们实际上需要求的是 a * b⁻¹. 根据费马小定理, bᵖ⁻¹ = 1, 因此有 b * bᵖ⁻²  = 1, 因此 b⁻¹ = bᵖ⁻². 所以 a / b 等价于 a * bᵖ⁻².
