# Cryptography/抗量子 Lamport 签名

## 后量子密码学

这篇文章主要初步探索一下后量子密码学的一些基础知识. 虽然目前为止量子计算机还停留在思想实验中, 但其实早在 20 世纪 70 年代数学家就在思考对抗量子计算机的密码学了. 目前广泛使用的公钥加密算法均基于三个计算难题: 整数分解问题, 离散对数问题和椭圆曲线离散对数问题. 然而, 这些难题均可使用量子计算机并应用 [Shor's algorithm](https://en.wikipedia.org/wiki/Shor%27s_algorithm) 破解.

因此, 抗量子计算机的密码学其核心是找到一个新的计算难题, 且这个计算难题无法被量子计算机轻易破解, 并基于这个新的计算难题构建的密码学算法.

## 后量子密码学的主要研究方向

目前, 后量子公钥密码学的研究方向如下.

- 格密码学(Lattice-based cryptography)是在算法构造本身或其安全性证明中应用到格的密码学.
- 编码密码学(Code-based Cryptography)是应用了编码理论与纠错码的密码学.
- 多变量密码学(Multivariate cryptography)是应用了有限域 F 上多元多项式的密码学, 包括对称加密和非对称加密.
- 散列密码学(Hash-based Cryptography)是应用散列函数的数字签名. 散列密码学的研究历史也很长, 最早的研究工作包括莱斯利·兰波特于 1979 年提出的兰波特签名(Lamport signature), 与瑞夫·墨克提出的墨克树(Merkle tree). 后来以此为基础, 又出现了 Winternitz 签名和 GMSS 签名, 近年来的工作则包括 SPHINCS 签名与 XMSS 签名方案.
- 超奇异椭圆曲线同源密码学(Supersingular elliptic curve isogeny cryptography)是利用超奇异椭圆曲线与超奇异同源图的数学性质的密码学, 可以实现超奇异同源密钥交换(SIDH), 具有前向安全性.

## Lamport 签名步骤描述

Lamport 签名基于密码学安全的哈希函数, 由 Leslie Lamport 在 1979 年发表, 论文 [L. Lamport, Constructing digital signatures from a one-way function, Technical Report SRI-CSL-98, SRI International Computer Science Laboratory, Oct. 1979](https://www.microsoft.com/en-us/research/uploads/prod/2016/12/Constructing-Digital-Signatures-from-a-One-Way-Function.pdf), 此篇论文非常短小.

鉴于原始论文的一些语言习惯与现代有不小的区别, 我们以维基百科页面 [Lamport Signature](https://en.wikipedia.org/wiki/Lamport_signature) 的内容为准介绍 Lamport 签名的实现.

**创建私钥公钥**

Lamport 签名是一种**一次性**签名, 对每一条消息进行签名必须生成一对新的私钥和公钥. 其私钥由 256x2 个随机 u256 组成, 构成一个二维矩阵. 公钥是对私钥中每个 u256 进行哈希, 同样构成一个二维矩阵. 哈希函数可以是任意密码学安全的哈希函数, 本文以 sha256 为例.

```py
import hashlib
import secrets

sk = [[None for _ in range(256)] for _ in range(2)]
pk = [[None for _ in range(256)] for _ in range(2)]
for i in range(256):
    sk[0][i] = secrets.token_bytes(32)
    sk[1][i] = secrets.token_bytes(32)
    pk[0][i] = hashlib.sha256(sk[0][i]).digest()
    pk[1][i] = hashlib.sha256(sk[1][i]).digest()
```

**签名**

首先, 我们将消息进行哈希, 得到一个 256 位哈希值. 然后, 对于哈希中的每个位, 根据位的值, 从组成它的私钥的相应数字对中选择一个数字. 即, 如果位是 0, 选择私钥对应位置中的第一个数字, 如果位是 1, 则选择第二个. 这会产生 256 个 u256 的序列. 这些数字就是该消息的签名.

需要注意的是, 签名使用了最初创建的私钥, 因此在完成消息的签名后不应该继续使用该私钥, 否则中间人可以利用前一条消息公开的部分私钥伪造消息和签名.

```py
raw = b'The quick brown fox jumps over the lazy dog'
msg = int.from_bytes(hashlib.sha256(raw).digest(), 'little')
sig = [None for _ in range(256)]
for i in range(256):
    b = msg >> i & 1
    sig[i] = sk[b][i]
```

**验签**

验证签名的过程就是检验签名是否和事先公开的公钥一致.

```py
for i in range(256):
    b = msg >> i & 1
    assert hashlib.sha256(sig[i]).digest() == pk[b][i]
```

## 资源消耗分析

- 私钥大小: 16384 字节
- 公钥大小: 16384 字节
- 签名大小: 8192 字节
- 验签哈希次数: 256 次

可见比起椭圆曲线签名而言非常浪费空间. 原始 Lamport 签名有许多变种, 这些改进算法优化了 Lamport 签名的部分痛点, 例如允许一个公私钥对签名多条消息, 或是减小签名的大小等.

## 完整代码

```py
import hashlib
import secrets

sk = [[None for _ in range(256)] for _ in range(2)]
pk = [[None for _ in range(256)] for _ in range(2)]
for i in range(256):
    sk[0][i] = secrets.token_bytes(32)
    sk[1][i] = secrets.token_bytes(32)
    pk[0][i] = hashlib.sha256(sk[0][i]).digest()
    pk[1][i] = hashlib.sha256(sk[1][i]).digest()

raw = b'The quick brown fox jumps over the lazy dog'
msg = int.from_bytes(hashlib.sha256(raw).digest(), 'little')
sig = [None for _ in range(256)]
for i in range(256):
    b = msg >> i & 1
    sig[i] = sk[b][i]

for i in range(256):
    b = msg >> i & 1
    assert hashlib.sha256(sig[i]).digest() == pk[b][i]
```

## 参考

- [1] [Zachary Ratliff. Implementing the Lamport one-time signature scheme in Python.](https://zacharyratliff.org/Lamport-Signatures/)
