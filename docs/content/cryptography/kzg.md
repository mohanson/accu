# Cryptography/KZG 多项式承诺

KZG 多项式承诺是 Kate, Zaverucha 和 Goldberg 等人在 2010 年发表的 Polynomial Commitments 论文提出的对多项式进行承诺的一种方案. 目前而言, 区块链上许多项目准备使用 KZG 多项式承诺解决一些特定问题, 例如 [EIP-4844](https://eips.ethereum.org/EIPS/eip-4844) 以及零知识证明相关项目.

## 承诺

承诺(commitment)是许多密码协议的基本组成部分. 一个安全的承诺⽅案允许提交者发布⼀个称为承诺的值, 该值绑定到⼀条消
息上⽽不泄露该消息. 稍后, 它可能会打开承诺并将承诺的消息透露给验证者, 验证者可以检查消息是否与承诺⼀致.

考虑一个场景: 假设 A 和 B 二人想通过抛硬币解决一些争议. 如果它们在同一时空位置, 则可能的流程是:

- A 选择正面或反面.
- B 抛硬币.
- 如果结果和 A 的选择一致, 则 A 赢, 否则 B 获胜.

但是如果 A 和 B 不在同一时空位置, 就会出现问题. 一旦 A 选择好硬币的正反面, B 就可以将结果规定为对他最适合的结果. 同样, 如果 A 不向 B 宣布她的选择, B 在抛硬币并宣布结果后, A 可以宣称这就是自己事先的选择. 这个时候, A 和 B 可以使用承诺方案解决双方互不信任的问题:

- A 选择正面或反面, 但只告诉 B 关于该选择的承诺(commitment).
- B 抛硬币并报告给 A 结果.
- A 报告她的选择并揭示(reveal)她的承诺.
- B 验证了 A 的选择与她的承诺相符.
- 如果结果和 A 的选择一致, 则 A 赢, 否则 B 获胜.

> 一些正规的赌场也会使用安全承诺方案. 赌客可能会担心赌场统计该赌局的所有赌注, 然后选择对赌场最有利的结果作为该赌局的结果--尤其是在电子化的赌博游戏中. 为了回避这种担忧, 赌场会在赌局开始前就提前设定赌局结果, 并公布该结果的承诺. 随着赌局终了, 赌客可验证赌局结果是否与提前公布的承诺相符.

多项式承诺(polynomial commitment)利用一个嵌入度为 d 的多项式隐藏所谓的秘密, 这个秘密可能是多项式的系数, 也可能就是 d + 1 个点. 在 KZG 多项式承诺方案中, 证明者计算一个多项式的承诺, 并可以在多项式的任意一点进行打开, 该承诺方案能证明多项式在特定位置的值与指定的值一致.

## 可信设置

在使用 KZG 多项式承诺之前, 需要先进行可信设置(Trust setup). 在这个步骤中, 首先生成无人知晓的 s, s ∈ Fr, 并计算 sⁱ⋅G₁ 和 sⁱ⋅G₂, i=1, ..., 随后销毁 s.

- s 为无人知晓的私钥, 在计算出 sⁱ⋅G₁ 和 sⁱ⋅G₂ 之后立即销毁
- sⁱ⋅G₁ 和 sⁱ⋅G₂ 公开, 每个人都知道

## 卡特承诺

多项式可以表达为以下结构

```text
f(x) = a₀⋅x⁰ + a₁⋅x¹ + a₂⋅x² ... + aₙ⋅xⁿ
```

我们约定该多项式的承诺为

```text
C = f(s)⋅G₁ = a₀⋅s⁰⋅G₁ + a₁⋅s¹⋅G₁ + a₂⋅s²⋅G₁ ... + aₙ⋅sⁿ⋅G₁
```

虽然 s 的值无人知晓, 但 sⁱ⋅G₁ 是公开的, 所以我们可以计算出 C. 根据公式可知 C 是椭圆曲线上的一点, 因此 C 的一个重要特征是 C 的大小是固定的, 与多项式的嵌入度无关.

## 卡特证明

卡特证明单个数据的公式推衍如下, 由于椭圆曲线群只支持加法同态, 无法支持多项式之间的乘法, 这是就需要通过配对函数解决. 其中配对函数用到的 G₂, 是另一个椭圆曲线群.

证明: (xᵢ, yᵢ) 位于多项式 f(x) 上.

```text
=> f(xᵢ) = yᵢ
=> f(x) - yᵢ = g(x) = (x - xᵢ)⋅q(x)
=> [f(s) - yᵢ]⋅G₁ = [(s - xᵢ)⋅q(s)]⋅G₁, 其中 f(s)⋅G₁ 就是卡特承诺 C
=> C - yᵢ⋅G₁ = [(s - xᵢ)⋅q(s)]⋅G₁
=> e(C - yᵢ⋅G₁, G₂) = e(q(s)⋅G₁, s⋅G₂ - xᵢ⋅G₂)
```

上式中, 只有 q(s)⋅G₁ 是未知的, 因此只需要提供 q(s)⋅G₁ 的值, 就能证明 f(xᵢ) = yᵢ. 因此 q(s)⋅G₁ 称为卡特承诺的证明, 它也是椭圆曲线上的一个点.

## 多重证明

更进一步, 我们来看看怎么使用一个群元素, 计算证明一个多项式在任意多个点的取值. 对于一个包含 k 个点的列表, 我们对其进行拉格朗日插值得到一个次数小于 k 的多项式 i(x). 现在我们假设 f(x) 经过了所有待证明的点, 那对于多项式 f(x) - i(x) 而言, 在 x₀, x₁ ... xₖ 均为零点.

```text
z(x) = (x - x₀)⋅(x - x₁)⋅ ... ⋅(x - xₖ)
q(x) = [f(x) - i(x)] / z(x)
```

注意因为 f(x) - i(x) 能被 z(x) 所有的线性因子整除, 所以它能被 z(x) 本身整除.

```text
=> [f(s) - i(s)]⋅G₁ = q(s)⋅z(s)⋅G₁
=> e(C - i(s)⋅G₁, G₂) = e(q(s)⋅G₁, z(s)⋅G₂)
```

q(s)⋅G₁ 称为卡特承诺的证明, 它也是椭圆曲线上的一个点.

## 数学工具

使用拉格朗日插值法可以将任意数据插值为一个多项式.

```py
import scipy

x = [1,  2,  3,  4]
y = [4, 15, 40, 85]
ret = scipy.interpolate.lagrange(x, y)

print(ret) # x³ + x² + x + 1
```

使用如下算法可将 `z(x) = (x - x₀)⋅(x - x₁)⋅ ... ⋅(x - xₖ)` 表达为多项式的系数形式:

```py
def vanish(c1):
    # See: https://aszepieniec.github.io/stark-anatomy/basic-tools
    x = [0, 1]
    a = [1]
    for d in c1:
        a = polynomial.mul(a, polynomial.sub(x, [d]))
    return a
```

## 代码实现

```py
import bn128
import random
import polynomial

# [1] Polynomial commits: https://cacr.uwaterloo.ca/techreports/2010/cacr2010-10.pdf
# [2] https://www.youtube.com/watch?v=n4eiiCDhTes
# [3] https://www.youtube.com/watch?v=NVvNHe_RGZ8
# [4] https://copper-witch-857.notion.site/Polynomial-KZG-or-Kate-Commitment-DappLearning-Notes-fc426c8cb9a14878840852506865f13b
# [5] https://foresightnews.pro/article/detail/17988
# [6] https://dankradfeist.de/ethereum/2021/10/13/kate-polynomial-commitments-mandarin.html


Fr = bn128.Fr
G1 = bn128.G1
I1 = bn128.I1
I2 = bn128.I2
G2 = bn128.G2
pairing = bn128.pairing

sk = Fr(random.randint(0, Fr.p - 1))
pk_g1 = [G1 * (sk**i) for i in range(10)]
pk_g2 = [G2 * (sk**i) for i in range(10)]

ax = [Fr(e) for e in [0,  1,  2,  3]]
ay = [Fr(e) for e in [4, 15, 40, 85]]
fx = polynomial.lagrange(ax, ay)
commit = sum([pk_g1[i] * fx[i] for i in range(len(fx))], start=I1)

# 单个证明
px = Fr(1)
py = Fr(15)
qx = polynomial.div(polynomial.sub(fx, [py]), [-px, Fr(1)])
proofs = sum([pk_g1[i] * qx[i] for i in range(len(qx))], start=I1)
lhs = pairing(G2, commit - G1 * py)
rhs = pairing(pk_g2[1] - G2 * px, proofs)
assert lhs == rhs

# 批量证明
px = [Fr(e) for e in [0,  1]]
py = [Fr(e) for e in [4, 15]]
ix = polynomial.lagrange(px, py)
zx = polynomial.zerofier(px)
qx = polynomial.div(polynomial.sub(fx, ix), zx)
proofs = sum([pk_g1[i] * qx[i] for i in range(len(qx))], start=I1)
ix_sg1 = sum([pk_g1[i] * ix[i] for i in range(len(ix))], start=I1)
zx_sg2 = sum([pk_g2[i] * zx[i] for i in range(len(zx))], start=I2)
lhs = pairing(G2, commit - ix_sg1)
rhs = pairing(zx_sg2, proofs)
assert lhs == rhs
```

在 Github 上阅读[完整代码](https://github.com/mohanson/cryptography-python/blob/master/kzg.py).

## 参考

- [1] [Kate, Zaverucha and Goldberg. Polynomial commits.](https://cacr.uwaterloo.ca/techreports/2010/cacr2010-10.pdf)
- [2] [Dapp Learning. Polynomial Commitment KZG with Examples(1).](https://www.youtube.com/watch?v=n4eiiCDhTes)
- [3] [Dapp Learning. Polynomial Commitment KZG with Examples(2).](https://www.youtube.com/watch?v=NVvNHe_RGZ8)
- [4] [Dapp Learning. Polynomial Commitment KZG with Examples.](https://copper-witch-857.notion.site/Polynomial-KZG-or-Kate-Commitment-DappLearning-Notes-fc426c8cb9a14878840852506865f13b)
- [5] [Xiang. 多项式承诺，正在重塑整个区块链.](https://foresightnews.pro/article/detail/17988)
- [6] [Dankrad Feist. KZG polynomial commitments.](https://dankradfeist.de/ethereum/2021/10/13/kate-polynomial-commitments-mandarin.html)
