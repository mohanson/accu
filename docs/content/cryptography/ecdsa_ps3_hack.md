# Cryptography/椭圆曲线签名的错误用法

索尼使用通常存储在公司总部的私钥将其 Playstation 固件标记为有效且未经修改. PS3 只需要一个公钥来验证签名是否来自索尼. 通常, 这被认为是安全的. 但索尼在实施他们的签名算法时犯了一个新手错误: 他们使用相同的随机数对所有内容进行签名.

## 测验

回想一下签名中的(公共参数) r 是如何从随机数 k 生成的, 使用公式 kG = R，r 是点 R 的 x 坐标. 给定两个使用相同 k 的签名, 证明可以提取用于签名的私钥.

有:

- 信息 m₁, 及其签名 (r₁, s₁)
- 信息 m₂, 及其签名 (r₂, s₂)
- 信息 m₁ 和 m₂ 使用相同的随机数 k 进行签名, k 的具体数据则未知

求:

- 私钥 prikey

## 数学推导

0. `s₁ = (m₁ + prikey * r₁) / k`
0. `s₂ = (m₂ + prikey * r₂) / k = (m₂ + prikey * r₁) / k`
0. `s₁ / s₂ = (m₁ + prikey * r₁) / (m₂ + prikey * r₁)`
0. `prikey = (s₁ * m₂ - s₂ * m₁) / (s₂ - s₁) / r₁`

## 代码实现

```py
import secp256k1

m1 = secp256k1.Fr(0x72a963cdfb01bc37cd283106875ff1f07f02bc9ad6121b75c3d17629df128d4e)
r1 = secp256k1.Fr(0x741a1cc1db8aa02cff2e695905ed866e4e1f1e19b10e2b448bf01d4ef3cbd8ed)
s1 = secp256k1.Fr(0x2222017d7d4b9886a19fe8da9234032e5e8dc5b5b1f27517b03ac8e1dd573c78)

m2 = secp256k1.Fr(0x059aa1e67abe518ea1e09587f828264119e3cdae0b8fcaedb542d8c287c3d420)
r2 = secp256k1.Fr(0x741a1cc1db8aa02cff2e695905ed866e4e1f1e19b10e2b448bf01d4ef3cbd8ed)
s2 = secp256k1.Fr(0x5c907cdd9ac36fdaf4af60e2ccfb1469c7281c30eb219eca3eddf1f0ad804655)

prikey = (s1 * m2 - s2 * m1) / (s2 - s1) / r1
assert prikey.x == 0x5f6717883bef25f45a129c11fcac1567d74bda5a9ad4cbffc8203c0da2a1473c
```

完整代码: <https://github.com/mohanson/cryptography-python>

## 参考

- [1] [Onyb. Quiz: The Playstation 3 Hack.](https://onyb.gitbook.io/secp256k1-python/the-playstation-3-hack)
