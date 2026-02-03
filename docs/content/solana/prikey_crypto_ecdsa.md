# Solana/私钥, 公钥与地址/私钥的密码学解释(四)

在数字化世界中, 如何在不泄露密钥的前提下验证他人身份, 一直是加密学领域的终极难题. 传统的口令和证书系统虽然安全, 但易受破解; 而公私钥体系则凭借强大的数学基础, 为数字信任提供了新的可能. 基于椭圆曲线 secp256k1 的 ecdsa 签名算法不仅能够证明信息的完整性, 更重要的是能够确保发送该信息的是身份持有者.

我们将在这一小节里学习 ecdsa 签名算法里的三个常用功能, 分别是签名, 验签以及公钥恢复.

## Ecdsa 签名

我们经常会在日常生活中的各种文书上签下自己的名字, 这通常有两层含义: 一是告诉旁人是谁签了这份文书, 二是表示您同意和认可了文书上的文字内容. 数字签名功能类似写在纸上的普通签名, 但是使用了公私钥加密技术, 以用于鉴别数字信息的方法. 与普通签名不同, 数字签名通常可以防止信息被篡改.

基于 secp256k1, 可以实现一种叫做 ecdsa 的公私钥签名算法. 您使用私钥进行签名, 他人则使用您事先提供的公钥来验证您的签名.

> 前文回顾: secp256k1 私钥是一个任意标量 k, 公钥则是生成点 g 与 k 的乘积, 即 g * k.

签名步骤如下:

0. 使用哈希函数(例如 sha256)对信息进行哈希处理, 得到信息摘要 m.
0. 从 [1, n-1] 范围内选择一个随机整数 k. 其中 n 为椭圆曲线的阶.
0. 计算点 c = g * k 并将结果的 x 坐标记为 r. 如果 r 等于 0, 则为 k 选择不同的值并重复该过程.
0. 计算 s = k⁻¹ * (m + r * prikey) 的值, 其中 k⁻¹ 是 k 的乘法逆元. 如果 s 等于 0, 则为 k 选择不同的值并重复该过程.
0. 消息的数字签名由 (r, s) 对组成.

实现代码如下:

```py
import itertools
import secrets
import typing
import pabtc.secp256k1


def sign(prikey: pabtc.secp256k1.Fr, m: pabtc.secp256k1.Fr) -> typing.Tuple[pabtc.secp256k1.Fr, pabtc.secp256k1.Fr, int]:
    # https://www.secg.org/sec1-v2.pdf
    # 4.1.3 Signing Operation
    for _ in range(64):
        k = pabtc.secp256k1.Fr(max(1, secrets.randbelow(pabtc.secp256k1.N)))
        R = pabtc.secp256k1.G * k
        r = pabtc.secp256k1.Fr(R.x.n)
        if r.n == 0:
            continue
        s = (m + prikey * r) / k
        if s.n == 0:
            continue
        v = 0
        if R.y.n & 1 == 1:
            v |= 1
        if R.x.n >= pabtc.secp256k1.N:
            v |= 2
        return r, s, v
    raise Exception('unreachable')
```

您可能发现在代码实现上, 签名函数不但返回了 (r, s), 还额外返回了一个 v 值. 这是恢复标识符, 用于从签名中确定签名者的公钥. 它使用了两个标志位, 最低标识位标志 c 的 y 轴坐标的奇偶位, 以便我们可以根据签名中的 r 来唯一还原 c 的实际值(椭圆曲线是关于 x 轴对称的曲线, 每一个 x 都对应两个可能的 y 值). 另一个比特位用于确认 r 值是否发生过溢出, 因为椭圆曲线上的点的坐标范围是 0 到 P, 但在签名运算中我们会将 c 的 x 坐标转换为一个标量, 范围将缩小到 0 到 N, 因此可能会发生溢出截断.

> 您还记得 P 与 N 的取值吗? P 指的是素数域中的素数, N 指 secp256k1 椭圆曲线的阶, N 比 P 小.

```py
P = 0xfffffffffffffffffffffffffffffffffffffffffffffffffffffffefffffc2f
N = 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141
```

## Ecdsa 验签

验签是签名的反向运算, 其步骤如下:

0. 使用相同的哈希函数对收到的信息进行哈希处理, 得到信息摘要 m.
0. 检查签名值 r 和 s 是否在 [1, n-1] 范围内. 如果不在, 则签名无效.
0. 计算值 a = m * s⁻¹和 b = r * s⁻¹, 其中 s⁻¹ 是 s 的乘法逆元.
0. 计算点 c = g * a + pubkey * b. 如果 c 等于单位元, 则签名无效.
0. 如果 c 的 x 坐标等于 r, 则签名有效, 否则无效.

我们实现代码如下:

```py
import pabtc.secp256k1


def verify(pubkey: pabtc.secp256k1.Pt, m: pabtc.secp256k1.Fr, r: pabtc.secp256k1.Fr, s: pabtc.secp256k1.Fr) -> bool:
    # https://www.secg.org/sec1-v2.pdf
    # 4.1.4 Verifying Operation
    a = m / s
    b = r / s
    R = pabtc.secp256k1.G * a + pubkey * b
    assert R != pabtc.secp256k1.I
    return r == pabtc.secp256k1.Fr(R.x.n)
```

## Ecdsa 公钥恢复

给定一个 ecdsa 签名 (r, s) 以及恢复标志符 v, 可以唯一确定签名者的公钥. 步骤如下:

0. 使用相同的哈希函数对收到的信息进行哈希处理, 得到信息摘要 m.
0. 通过恢复标志符 v 唯一还原 c 值.
0. 公钥 pubkey = (c * s - g * m) / r.

我们实现代码如下:

```py
import pabtc.secp256k1


def pubkey(m: pabtc.secp256k1.Fr, r: pabtc.secp256k1.Fr, s: pabtc.secp256k1.Fr, v: int) -> pabtc.secp256k1.Pt:
    # https://www.secg.org/sec1-v2.pdf
    # 4.1.6 Public Key Recovery Operation
    assert v in [0, 1, 2, 3]
    if v & 2 == 0:
        x = pabtc.secp256k1.Fq(r.x)
    else:
        x = pabtc.secp256k1.Fq(r.x + pabtc.secp256k1.N)
    z = x * x * x + pabtc.secp256k1.A * x + pabtc.secp256k1.B
    y = z ** ((pabtc.secp256k1.P + 1) // 4)
    if v & 1 != y.x & 1:
        y = -y
    R = pabtc.secp256k1.Pt(x, y)
    return (R * s - pabtc.secp256k1.G * m) / r
```

再次提醒! 上文中所有出现的代码都公布在 github 上, 这样您可以随时查看, 参考和使用. 如果您有任何问题或需要进一步的帮助, 请随时告诉我!

- [pabtc.ecdsa](https://github.com/mohanson/pabtc/blob/master/pabtc/ecdsa.py)
- [pabtc.secp256k1](https://github.com/mohanson/pabtc/blob/master/pabtc/secp256k1.py)

## 习题

例: 有一条消息经过哈希处理, 其哈希值为 0x72a963cdfb01bc37cd283106875ff1f07f02bc9ad6121b75c3d17629df128d4e, 请使用私钥 0x01 对其进行签名, 验签以及公钥恢复.

答:

```py
import pabtc

prikey = pabtc.secp256k1.Fr(1)
pubkey = pabtc.secp256k1.G * prikey
m = pabtc.secp256k1.Fr(0x72a963cdfb01bc37cd283106875ff1f07f02bc9ad6121b75c3d17629df128d4e)

r, s, v = pabtc.ecdsa.sign(prikey, m)
assert pabtc.ecdsa.verify(pubkey, m, r, s)
assert pabtc.ecdsa.pubkey(m, r, s, v) == pubkey
```
