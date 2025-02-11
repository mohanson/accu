# Solana/私钥, 公钥与地址/私钥的密码学解释

好吧, 这一章不是一篇易于理解的文章. 我将在这一章对 solana 的私钥做出一些密码学方面的解释, 这需要读者有一定的数学基础. 如果感觉到困难, 您完全可以跳过这一章内容, 我相信不会对后续学习产生任何阻碍. 作为我 solana 教程的一部分, 这篇文章花费了我最多的时间, 因此如果您下定决心阅读这篇文章, 相信看完之后会有一点的收获.

## 公私钥密码学: 区块链的基石

在我们深入探讨 solana 的私钥之前, 首先需要了解一种称为"公私钥密码学"的技术. 这是一种被广泛应用于现代信息安全领域的核心技术, 也是 solana 安全运行的基础. 公私钥密码学, 也被称为"非对称加密", 是一种基于数学算法的加密方法. 其核心在于使用一对密钥: 公钥(Public Key)和私钥(Private Key).

**公钥**

- 公钥是可以公开使用的密钥, 它的主要作用是加密数据或验证签名.
- 有了公钥, 其他人可以安全地加密信息或对你的数据进行认证.

**私钥**

- 私钥是只有你一个人知道的密钥, 它的主要作用是解密信息或创建签名.
- 如果别人用你的公钥加密的数据, 只有你才能用你的私钥来解开并读取内容.

公私钥密码学的数学基础可以追溯到 20 世纪 70 年代. 最早的尝试之一是 Diffie 和 Hellman 在 1976 年提出的 "Diffie-Hellman 关键交换协议", 但当时并没有广泛应用于实际系统. 随后, RSA 加密算法在 1977 年由 Ron Rivest, Adi Shamir 和 Len Adleman 提出, 成为公私钥密码学的经典方案. RSA 基于数论中的大质数分解难题, 被认为是安全的加密方法之一. 椭圆曲线密码学则是 RSA 的一种替代方案, 其优势在于使用更短的密钥长度即可达到相同的安全水平, 它的数学基础是椭圆曲线离散对数问题.

得益于比特币的发展, 比特币所采用的 secp256k1 椭圆曲线以及 ecdsa 签名算法在全球变得广为人知, 并产生了非常巨大的影响: 包括 ethereum, ckb 等众多区块链项目在内, 都采用了和比特币相同的密码学算法. 但 solana 在这方面有点不一样, 它采用的是一种新型的椭圆曲线数字签名算法, 其曲线名称 ed25519, 签名算法为 eddsa. 要理解这方面的改变, 我们需要先了解 secp256k1 椭圆曲线的劣势, 而要理解它的劣势, 我们需要首先了解它.

因此, 我们将首先跳脱到 solana 之外, 我们将首先聚焦在比特币采用的 secp256k1 + ecdsa 密码学算法上. 提示:

| 区块链 | 椭圆曲线  | 签名算法 |
| ------ | --------- | -------- |
| 比特币 | secp256k1 | ecdsa    |
| solana | ed25519   | eddsa    |

## 比特币标准曲线

Secp256k1 是比特币采用的标准椭圆曲线, 基于 koblitz 曲线(y² = x³ + ax + b). 其参数与 P-256 类似, 但在实现过程中存在一些问题.

> 您只需要知道 P-256 是另一类被广泛使用的椭圆曲线, secp256k1 与其的区别只有参数不同.

在椭圆曲线的计算中使用的数字不是我们常规认知中的数字, 而是一种在数论中称为"有限域"的数字. "有限域"的前提是"域", "域"的前身是"环", 而要了解"环", 又要求我们首先理解"群". 这些都是代数学里的基本结构，但对非数学专业的普通人来说还是挺抽象的.

**群**

数学里面的群(G, group)是由集合和二元运算(用符号 + 表示)构成的, 符合以下四个群公理的数学结构. 群公理的四个性质如下:

0. 加法封闭性: 对于群中的任意两个元素进行运算后, 结果仍然属于该群.
0. 加法结合律: 群中的运算满足结合律, 即对于群中的任意三个元素进行运算, 先计算前两个元素的运算结果, 然后再与第三个元素进行运算, 结果应该与先计算后两个元素的运算结果再与第三个元素进行运算的结果相同.
0. 加法单位元: 群中存在一个特殊的元素, 称为单位元, 对于群中的任意元素 a, 运算 a 与单位元的结果等于元素 a 本身, 即 a + e = e + a = a, 其中 e 表示单位元素.
0. 加法逆元素: 群中的每个元素都有一个逆元素, 对于群中的任意元素 a, 存在一个元素 b, 使得 a + b = b + a = e, 其中 e 表示单位元.

如果我们添加第五条要求:

0. 加法交换律: a + b = b + a.

那么这个群就是**阿贝尔群**或**交换群**.

例: 整数集 Z 是一个阿贝尔群. 自然数集 N 不是一个群, 因为它不满足第四条群公理.

一个有限群 G 的元素个数称为群的阶(order). 一个群元素 P 的阶为最小的整数 k 使得 kP = O(k 个 P 进行群运算, O 为单位元)称为 P 的阶. P 的阶一定整除群的阶. 如果一个元素 P 的阶等于群的阶, 则 P 是 G 的一个生成元, 且 G = {P, 2P, ...} 是一个循环群(cyclic group).

**环**

环(Z, ring)在群的基础上多定义了一个群运算 ×(乘法).

0. 乘法封闭性: 对于环中的任意两个元素进行乘法运算后, 结果仍然属于该环.
0. 乘法结合律: 环中的乘法运算满足结合律, 即对于环中的任意三个元素进行乘法运算, 先计算前两个元素的乘法结果, 然后再与第三个元素进行乘法运算, 结果应该与先计算后两个元素的乘法结果再与第三个元素进行乘法运算的结果相同.
0. 乘法分配律: 环中的乘法运算对于加法运算满足左分配律和右分配律, 即对于环中的任意三个元素 a, b, c, 有 a * (b + c) = a * b + a * c 和 (b + c) * a = b * a + c * a.

**域**

域(F, Field)是一种代数结构, 由一个集合和两个二元运算(加法和乘法)组成. 域满足环的所有条件, 并且具有以下额外性质:

0. 乘法单位元: 域中存在一个特殊的元素, 称为乘法单位元素, 对于域中的任意元素 a, 乘法 a 与乘法单位元素的结果等于元素 a 本身, 即 a * 1 = 1 * a = a, 其中 1 表示乘法单位元素.
0. 乘法逆元素: 域中的每个非零元素都有一个乘法逆元素, 对于域中的任意非零元素 a, 存在一个元素 b, 使得 a * b = b * a = 1, 其中 1 表示乘法单位元素.

例: 整数集 Z 构成一个环但不构成域. 有理数集, 实数集和复数集均构成域.

**有限域**

有限域(finite field)或伽罗瓦域是包含有限个元素的域. 与其他域一样, 有限域是进行加减乘除运算都有定义并且满足特定规则的集合. 有限域最常见的例子是当 p 为素数时, 整数对 p 取模.

下面我们使用 python 代码实现一个素数有限域. 客观来讲, 它十分类似我们日常生活中使用的整数, 但区别在于我们需要对所有计算结果进行取模.

```py
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

    def __repr__(self) -> str:
        return f'Fp(0x{self.x:064x})'

    def __eq__(self, data: typing.Self) -> bool:
        assert self.p == data.p
        return self.x == data.x

    def __add__(self, data: typing.Self) -> typing.Self:
        assert self.p == data.p
        return self.__class__(self.x + data.x)

    def __sub__(self, data: typing.Self) -> typing.Self:
        assert self.p == data.p
        return self.__class__(self.x - data.x)

    def __mul__(self, data: typing.Self) -> typing.Self:
        assert self.p == data.p
        return self.__class__(self.x * data.x)

    def __truediv__(self, data: typing.Self) -> typing.Self:
        return self * data ** -1

    def __pow__(self, data: int) -> typing.Self:
        return self.__class__(pow(self.x, data, self.p))

    def __pos__(self) -> typing.Self:
        return self.__class__(self.x)

    def __neg__(self) -> typing.Self:
        return self.__class__(self.p - self.x)

    @classmethod
    def nil(cls) -> typing.Self:
        return cls(0)

    @classmethod
    def one(cls) -> typing.Self:
        return cls(1)
```

例: 当素数 p 为 23 时, 求以下算式的值.

- 12 + 20
- 8 * 9
- 1 / 8

答:

- 12 + 20 = 32 % 23 = 9
- 8 * 9 = 72 % 23 = 3
- 由于 3 * 8 = 24 % 23 = 1, 因此 1 / 8 = 3

```py
Fp.p = 23
assert Fp(12) + Fp(20) == Fp(9)
assert Fp(8) * Fp(9) == Fp(3)
assert Fp(8) ** -1 == Fp(3)
```
