# Cryptography/Schnorr 签名: 安全高效的数字签名方案

在加密货币和密码学领域, 数字签名是一项至关重要的技术, 用于验证信息的完整性, 身份认证和防止伪造. Schnorr 签名作为一种安全性强, 效率高的数字签名方案, 正逐渐受到广泛关注和采用. 本文将深入介绍 Schnorr 签名的原理, 优势以及在加密货币中的应用.

> 数字签名是一种密码学技术, 用于验证消息的真实性和完整性. 它通过将私钥与消息进行组合生成一个唯一的签名, 并使用对应的公钥进行验证. 在过去的几十年里, 许多数字签名方案被提出和使用, 其中 Schnorr 签名是一种备受瞩目的方案.

## Schnorr 签名原理

Schnorr 签名方案由克劳斯·施诺尔(Claus Schnorr)在 1989 年提出. 它基于椭圆曲线密码学, 使用一个随机数生成器和哈希函数来生成签名. Schnorr 签名的主要思想是将随机数与私钥进行组合, 并利用椭圆曲线上的点运算来生成签名. 在验证时, 通过公钥和签名对进行点运算和哈希处理来验证签名的有效性.

Schnorr 签名的一般步骤如下:

0. 生成随机私钥 `k` 以及其公钥 `R`
0. 计算 `e = hash(R || m)`, 其中 `m` 为消息的哈希值
0. 计算 `s = k + e ∗ prikey`
0. 生成签名 `(R, s)`

Schnorr 验签的一般步骤如下:

0. 计算 `e = hash(R || m)`, 其中 `m` 为消息的哈希值
0. 验证 `s ∗ G == R + e ∗ pubkey`

## Schnorr 签名代码实现

```py
import hashlib
import random
import secp256k1

# https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki
#
# Schnorr signature variant Elliptic Curve Schnorr signatures for message m and public key P generally involve a point
# R, integers e and s picked by the signer, and the base point G which satisfy e = hash(R || m) and s⋅G = R + e⋅P. Two
# formulations exist, depending on whether the signer reveals e or R:
#   1. ....
#   2. Signatures are pairs (R, s) that satisfy s⋅G = R + hash(R || m)⋅P. This supports batch verification, as there
#      are no elliptic curve operations inside the hashes. Batch verification enables significant speedups.

prikey = secp256k1.Fr(0x5f6717883bef25f45a129c11fcac1567d74bda5a9ad4cbffc8203c0da2a1473c)
pubkey = secp256k1.G * prikey

# Hash of messages.
with open('./secp256k1.py', 'rb') as f:
    m = int.from_bytes(hashlib.sha256(f.read()).digest(), 'little')
    m = secp256k1.Fr(m)
print(f'hash={m}')

# R = k ∗ G
# e = hash(R || m)
# s = k + e ∗ prikey
k = secp256k1.Fr(random.randint(0, secp256k1.N))
R = secp256k1.G * k
hasher = hashlib.sha256()
hasher.update(R.x.x.to_bytes(32, 'little'))
hasher.update(R.y.x.to_bytes(32, 'little'))
hasher.update(m.x.to_bytes(32, 'little'))
e = secp256k1.Fr(int.from_bytes(hasher.digest(), 'little'))
s = k + e * prikey
print(f'sign=(R={R}, s={s})')

# s ∗ G =? R + hash(R || m) ∗ P
verify = secp256k1.G * s == R + pubkey * e
print(f'verify={verify}')
```

您可在此获取[完整代码](https://github.com/mohanson/cryptography-python/blob/master/secp256k1_schnorr.py).

## Schnorr 签名优势

Schnorr 签名相比其他数字签名方案具有多个优势. 首先, 它具有较短的签名长度, 可以减少存储空间和传输带宽要求. 其次, Schnorr 签名是线性可叠加的, 这意味着可以将多个签名组合成单个签名, 减少交易的大小. 此外, Schnorr 签名也提供了更好的隐私保护, 抵抗多种攻击, 如选择性抵赖攻击和碰撞攻击. Schnorr 签名算法几乎在各个层面均优于比特币现有的签名算法 ECDSA, 但由于 Schnorr 签名在 1990 年申请了专利, 并且直到 2008 年才失效, 因此比特币最初设计阶段未采用 Schnorr 签名. 正如 [BIP-0340](https://github.com/bitcoin/bips/blob/master/bip-0340.mediawiki) 中所描述:

> For all these advantages, there are virtually no disadvantages, apart from not being standardized.

## 参考

- [1] Schnorr, C. P. (1989). Efficient Identification and Signatures for Smart Cards.
