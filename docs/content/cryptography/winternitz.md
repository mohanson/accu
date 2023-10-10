# Cryptography/抗量子 W-OTS 签名

## W-OTS 签名介绍

Winternitz One Time Signature(W-OTS) 签名是一种 Lamport 签名算法的变种, 它有效减小了 Lamport 签名的长度. 在 Lamport 签名中, 消息的每一个比特位都对应一个签名中的哈希值, 而 Winternitz 签名的核心思想是让每 N(2, 4, 8 ...) 个比特位对应一个签名中的哈希值. 在本文中, 我们选取 N 等于 8, 那么一条长度为 256 位的信息可以被分为 32 个 chunk, 每个 chunk 可以视为 0-255 之间的一个数字.

Winternitz 需要应用到一个叫做 Hash List 的技术, 这个技术简单来说, 就是对哈希递归计算哈希. 我们规定哈希函数:

```text
Fⁿ(x) = x          (n = 0)
      = F(Fⁿ-1(x)) (n > 0)
```

易得等式:

```text
Fⁿ⁺ᵐ(x) = Fᵐ(Fⁿ(x))
```

我们为每一个 chunk 随机生成 1 个 u256 数字, 将其全体 32 个 u256 数字作为私钥. 私钥中的每个数字递归计算哈希 256 次作为公钥. 对于每个 chunk 所表示的整数 n, 我们对相应位置的私钥递归计算哈希 n 次作为签名, 验证签名则是将签名递归计算哈希 256 - n 次并判断是否和公钥相等.

## 代码实现

```py
# On the Security of the Winternitz One-Time Signature Scheme
# https://eprint.iacr.org/2011/191.pdf

import hashlib
import secrets


def iterhash(data, n):
    for _ in range(n):
        data = hashlib.sha256(data).digest()
    return data


sk = [None for _ in range(32)]
pk = [None for _ in range(32)]
for i in range(32):
    sk[i] = secrets.token_bytes(32)
    pk[i] = iterhash(sk[i], 256)

raw = b'The quick brown fox jumps over the lazy dog'
msg = hashlib.sha256(raw).digest()
sig = [None for _ in range(32)]
for i in range(32):
    n = msg[i]
    sig[i] = iterhash(sk[i], n)

for i in range(32):
    n = msg[i]
    assert iterhash(sig[i], 256 - n) == pk[i]
```

## 资源消耗分析

- 私钥大小: 1024 字节
- 公钥大小: 1024 字节
- 签名大小: 1024 字节
- 验签哈希次数: 256 到 8192 次

## 算法缺陷及其改进

伪造者虽然很难将一个 chunk 所代表的整数 n 修改为 n - 1, 但却很容易将 n 修改为 n + 1, 该 chunk 对应的签名只需要在原签名的基础上多哈希一次即可. 解决这个问题的方法是对每个 chunk 计算 256 - n, 并将这些值相加作为校验码添加在消息的末尾, 并用同样的方式签名. 此时伪造者如果要将一个 chunk 所代表的整数 n 修改为 n + 1, 那么其势必要将校验码减少 1, 而这是无法做到的.

## 参考

- [1] [Johannes Buchmann, Erik Dahmen, Sarah Ereth, Andreas Hulsing, and Markus Ruckert. On the Security of the Winternitz One-Time Signature Scheme](https://eprint.iacr.org/2011/191.pdf).
