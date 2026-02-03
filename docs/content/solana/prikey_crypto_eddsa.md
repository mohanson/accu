# Solana/私钥, 公钥与地址/私钥的密码学解释(七)

Eddsa 是一种使用基于扭曲爱德华兹曲线的 schnorr 签名变体的数字签名方案. 它旨在在不牺牲安全性的情况下比现有的数字签名方案更快.

## Eddsa 点的编码

在 eddsa 中, 我们需要使用到一种特殊的曲线上的点的编码算法. 直观上讲, 曲线上的一个点由 x 和 y 两个值组成, 且 x 和 y 都
在 0 <= x,y < p 范围内, 因此我们需要使用 64 个字节来表示它. 但有办法将空间压缩到 32 个字节, 具体方法如下:

0. 由于 y < p, 因此 y 的最高有效位始终为 0.
0. 将 x 的最低有效位复制到 y 的最高有效位上, 并将结果以小端序编码为 32 个字节.

在这种编码方式下, 我们能得知 y 的具体数值以及 x 的奇偶性. 代码实现如下.

```py
def pt_encode(pt: pxsol.ed25519.Pt) -> bytearray:
    # A curve point (x,y), with coordinates in the range 0 <= x,y < p, is coded as follows. First, encode the
    # y-coordinate as a little-endian string of 32 octets. The most significant bit of the final octet is always zero.
    # To form the encoding of the point, copy the least significant bit of the x-coordinate to the most significant bit
    # of the final octet.
    # See https://datatracker.ietf.org/doc/html/rfc8032#section-5.1.2
    n = pt.y.n | ((pt.x.n & 1) << 255)
    return bytearray(n.to_bytes(32, 'little'))
```

## Eddsa 点的解码

Eddsa 点的解码是点的编码的逆运算. 步骤如下:

0. 首先, 将 32 字节数组解释为小端表示的整数. 此数字的第 255 位是 x 坐标的最低有效位, 表示了 x 值的奇偶性. 只需清除此位即可恢复 y 坐标. 如果 y >= p, 则解码失败.
0. 要恢复 x 坐标, 意味着曲线方程 x² = (y² - 1) / (d * y² + 1) 成立. 令 u = y² - 1, v = d * y² + 1, 计算它的候选根 x = (u / v)^((p + 3) / 8).
0. 现在有三种情况:
    1. 如果 x * x == u / v, 不做处理.
    2. 如果 x * x == u / v * -1, 则令 x = x * 2^((p - 1) / 4).
    3. 解码失败, 点不在曲线上.
0. 最后, 确定 x 的奇偶性. 如果奇偶性不一致, 则令 x = -x.

代码实现如下

```py
def pt_decode(pt: bytearray) -> pxsol.ed25519.Pt:
    # Decoding a point, given as a 32-octet string, is a little more complicated.
    # See https://datatracker.ietf.org/doc/html/rfc8032#section-5.1.3
    #
    # First, interpret the string as an integer in little-endian representation. Bit 255 of this number is the least
    # significant bit of the x-coordinate and denote this value x_0. The y-coordinate is recovered simply by clearing
    # this bit. If the resulting value is >= p, decoding fails.
    uint = int.from_bytes(pt, 'little')
    bit0 = uint >> 255
    yint = uint & ((1 << 255) - 1)
    assert yint < pxsol.ed25519.P
    # To recover the x-coordinate, the curve equation implies x^2 = (y^2 - 1) / (d y^2 + 1) (mod p). The denominator is
    # always non-zero mod p.
    y = pxsol.ed25519.Fq(yint)
    u = y * y - pxsol.ed25519.Fq(1)
    v = pxsol.ed25519.D * y * y + pxsol.ed25519.Fq(1)
    w = u / v
    # To compute the square root of (u/v), the first step is to compute the candidate root x = (u/v)^((p+3)/8).
    x = w ** ((pxsol.ed25519.P + 3) // 8)
    # Again, there are three cases:
    # 1. If v x^2 = +u (mod p), x is a square root.
    # 2. If v x^2 = -u (mod p), set x <-- x * 2^((p-1)/4), which is a square root.
    # 3. Otherwise, no square root exists for modulo p, and decoding fails.
    if x*x != w:
        x = x * pxsol.ed25519.Fq(2) ** ((pxsol.ed25519.P - 1) // 4)
        assert x*x == w
    # Finally, use the x_0 bit to select the right square root. If x = 0, and x_0 = 1, decoding fails. Otherwise, if
    # x_0 != x mod 2, set x <-- p - x.  Return the decoded point (x,y).
    assert x != pxsol.ed25519.Fq(0) or not bit0
    if x.x & 1 != bit0:
        x = -x
    return pxsol.ed25519.Pt(x, y)
```

## 私钥

如前所述, Ed25519 的私钥是一个 32 字节的随机数, 通常通过安全的随机数生成器产生. 私钥是用户身份的核心, 需严格保密. 在 Ed25519 的实现中, 私钥并非用于直接签名, 而是通过哈希函数(sha-512)扩展为 64 字节的种子, 其中一部分作为标量用于生成公钥, 另一部分作为签名时的秘密标量. 这种设计增强了私钥的安全性, 防止因直接使用原始私钥而暴露风险.

私钥生成简单, 但其安全性依赖于随机数的质量. 如果随机数可预测, 攻击者可能通过暴力破解或伪造签名来威胁系统. 因此, 使用密码学安全的随机数生成器(如 /dev/urandom 或硬件随机数生成器)是生成私钥的关键.

```py
import secrets

prikey = bytearray(secrets.token_bytes(32))
```

## 公钥

Ed25519 的公钥的长度同样是 32 字节. 32 字节公钥通过以下步骤生成.

0. 使用 sha-512 对 32 字节私钥进行哈希处理, 生成 64 个字节的哈希结果. 只有前 32 个字节用于生成公钥.
0. 清除第一个字节的最低三位, 清除最后一个八位字节的最高位, 并设置最后一个字节的第二高位.
0. 将上述数据解释为小端序整数, 形成秘密标量 a. 执行标量乘法 g * a, 并将结果进行点的编码.

```py
def pubkey(prikey: bytearray) -> bytearray:
    assert len(prikey) == 32
    h = hash(prikey)
    a = int.from_bytes(h[:32], 'little')
    a &= (1 << 254) - 8
    a |= (1 << 254)
    a = pxsol.ed25519.Fr(a)
    return pt_encode(pxsol.ed25519.G * a)
```

Ed25519 的公钥生成过程是单向的: 从私钥可以快速计算出公钥, 但从公钥无法反推出私钥, 这种不可逆性是椭圆曲线离散对数问题的核心保障. 公钥的作用是公开身份, 任何人都可以使用公钥来验证签名. 由于 Ed25519 的设计高效, 公钥生成和使用都非常快速, 非常适用于高性能场景.

## 签名

签名用于证明消息的真实性和完整性. 签名过程的输入是私钥(一个 32 字节的数组)和任意大小的消息 m, 签名过程如下:

0. 使用 sha-512 对私钥(32 字节)进行哈希计算. 按照前一节的描述, 从哈希的前半部分构造秘密标量 a, 以及对应的公钥 pubkey. 将哈希摘要的后半部分记为 prefix.
0. 计算 sha-512(prefix + m), 其中 m 是待签名的消息. 将得到的 64 字节哈希解释为一个小端序整数 r.
0. 计算点 g * r, 并对结果进行点的编码, 记为 digest.
0. 计算 sha-512(digest + pubkey + m),  并将得到的 64 字节摘要解释为一个小端序整数 h.
0. 计算 s = r + a * h.
0. 将 digest 和 s 的小端序编码连接起来, 形成 64 字节签名.

```py
def sign(prikey: bytearray, m: bytearray) -> bytearray:
    # The inputs to the signing procedure is the private key, a 32-octet string, and a message M of arbitrary size.
    # See https://datatracker.ietf.org/doc/html/rfc8032#section-5.1.6
    assert len(prikey) == 32
    h = hash(prikey)
    a = int.from_bytes(h[:32], 'little')
    a &= (1 << 254) - 8
    a |= (1 << 254)
    a = pxsol.ed25519.Fr(a)
    A = pxsol.ed25519.G * a
    pubkey = pt_encode(A)
    prefix = h[32:]
    r = pxsol.ed25519.Fr(int.from_bytes(hash(prefix + m), 'little'))
    R = pxsol.ed25519.G * r
    digest = pt_encode(R)
    h = pxsol.ed25519.Fr(int.from_bytes(hash(digest + pubkey + m), 'little'))
    s = r + a * h
    return digest + bytearray(s.x.to_bytes(32, 'little'))
```


## 验签

验签是验证签名的过程, 用于确认消息未被篡改且确实由持有对应私钥的人签署. Ed25519 的验签需要消息 m, 签名 v 和公钥 pubkey, 步骤如下:

0. 先将签名 v 拆分为两个 32 字节数组. 将前半部分记为 digest, 解码为点 r, 将后半部分解码为整数 s. 将公钥 pubkey 解码为点 a. 如果任何解码失败(包括 s 超出范围), 则签名无效.
0. 计算 sha-512(digest + pubkey + m), 并将 64 位字节摘要解释为小端整数 h.
0. 检查是否满足群方程 g * s == r + a * h

```py
def verify(pubkey: bytearray, m: bytearray, g: bytearray) -> bool:
    # Verify a signature on a message using public key.
    # See https://datatracker.ietf.org/doc/html/rfc8032#section-5.1.7
    assert len(pubkey) == 32
    assert len(g) == 64
    A = pt_decode(pubkey)
    digest = g[:32]
    R = pt_decode(digest)
    s = pxsol.ed25519.Fr(int.from_bytes(g[32:], 'little'))
    h = pxsol.ed25519.Fr(int.from_bytes(hash(digest + pubkey + m), 'little'))
    return pxsol.ed25519.G * s == R + A * h
```

例: 假设您有私钥 `833fe62409237b9d62ec77587520911e9a759cec1d19755b7da901b96dca3d42`, 请对消息 `sha-512('abc')` 进行签名并验证签名.

答:

```py
import pxsol
import hashlib

prikey = bytearray.fromhex('833fe62409237b9d62ec77587520911e9a759cec1d19755b7da901b96dca3d42')
pubkey = pxsol.eddsa.pubkey(prikey)
msg = hashlib.sha512(b'abc').digest()
sig = pxsol.eddsa.sign(prikey, msg)
assert sig[:32].hex() == 'dc2a4459e7369633a52b1bf277839a00201009a3efbf3ecb69bea2186c26b589'
assert sig[32:].hex() == '09351fc9ac90b3ecfdfbc7c66431e0303dca179c138ac17ad9bef1177331a704'
assert pxsol.eddsa.verify(pubkey, msg, sig)
```
