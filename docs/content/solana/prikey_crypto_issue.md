# Solana/私钥, 公钥与地址/私钥的密码学解释(中篇)

同学们, secp256k1 与 ecdsa 签名算法现在已经被广泛用于许多系统中了。我知道椭圆曲线在密码学中有优势，因为它们可以在较小的密钥长度下提供更高的安全性。但是，这可能意味着什么呢？

从最近的新闻来看, 它似乎有了一些问题。美国国家标准与技术研究院认为 secp256k1 存在一些安全风险，已经不建议使用, 作为替代, 美国建议使用另一条名为 secp256r1 的椭圆曲线. 另一方面, 比特币自身也在改变, 比特币在 2021 年引入了一种叫做 schnorr 的签名算法来尝试替代 ecdsa.

是因为算法本身的问题还是其他因素导致 secp256k1 + ecdsa 不再受追捧? 我们来尝试探究下隐藏在其之下的深层原因.

## 随机数重用攻击

因为比特币的原因, secp256k1 椭圆曲线以及 ecdsa 签名算法变得无人不知, 无人不晓. 但其实在比特币之前, 它们也并非无人问津. 例如在 playstation 3 时代, 索尼就使用存储在公司总部的私钥将其 playstation 固件标记为有效且未经修改. Playstation 3 只需要一个公钥来验证签名是否来自索尼. 但不幸的是, 索尼因为他们糟糕的代码实现而遭到了黑客的破解, 这意味着他们今后发布的任何系统更新都可以毫不费力地解密.

在 fail0overflow 大会上, 黑客展示了索尼 ecdsa 的部分代码, 发现索尼让随机数的值始终保持 4, 这导致了 ecdsa 签名步骤中的随机私钥 k 始终会得到相同的值. Ecdsa 签名要求随机数 k 是严格随机的, 如果重复使用 k, 将直接导致私钥泄露. 这个攻击并不难, 因此小伙子们快来挑战一下吧!

```py
def get_random_number():
  # Chosen by fair dice roll. Guaranteed to be random.
  return 4
```

例: 有以下信息

- 信息 m₁, 及其签名 (r₁, s₁)
- 信息 m₂, 及其签名 (r₂, s₂)
- 信息 m₁ 和 m₂ 使用相同的随机数 k 进行签名, k 的具体数据则未知

求私钥 prikey.

答:

```txt
s₁ = (m₁ + prikey * r₁) / k
s₂ = (m₂ + prikey * r₂) / k = (m₂ + prikey * r₁) / k
s₁ / s₂ = (m₁ + prikey * r₁) / (m₂ + prikey * r₁)
prikey = (s₁ * m₂ - s₂ * m₁) / (s₂ - s₁) / r₁
```

这里有一个实际的例子可以帮助大家更直观的理解如何通过两个使用相同随机数 k 的签名来还原私钥.

```py
import pabtc

m1 = pabtc.secp256k1.Fr(0x72a963cdfb01bc37cd283106875ff1f07f02bc9ad6121b75c3d17629df128d4e)
r1 = pabtc.secp256k1.Fr(0x741a1cc1db8aa02cff2e695905ed866e4e1f1e19b10e2b448bf01d4ef3cbd8ed)
s1 = pabtc.secp256k1.Fr(0x2222017d7d4b9886a19fe8da9234032e5e8dc5b5b1f27517b03ac8e1dd573c78)

m2 = pabtc.secp256k1.Fr(0x059aa1e67abe518ea1e09587f828264119e3cdae0b8fcaedb542d8c287c3d420)
r2 = pabtc.secp256k1.Fr(0x741a1cc1db8aa02cff2e695905ed866e4e1f1e19b10e2b448bf01d4ef3cbd8ed)
s2 = pabtc.secp256k1.Fr(0x5c907cdd9ac36fdaf4af60e2ccfb1469c7281c30eb219eca3eddf1f0ad804655)

prikey = (s1 * m2 - s2 * m1) / (s2 - s1) / r1
assert prikey.x == 0x5f6717883bef25f45a129c11fcac1567d74bda5a9ad4cbffc8203c0da2a1473c
```
