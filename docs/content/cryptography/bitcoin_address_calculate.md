# Cryptography/比特币地址生成详细步骤

比特币地址用来发送和接收比特币，就像传统的银行帐号一样. 比特币经过长年的发展, 现在拥有多种不同类型的地址格式, 这一点常常造成一些人的困扰. 许多人在钱包中导入比特币私钥后, 发现余额为零而大惊失色, 其实很多情况下是在导入私钥后不小心选择了错误的地址格式.

## P2PKH

P2PKH 地址是比特币最经典的地址类型. 生成此类型地址通常涉及以下几个步骤

1. 生成公钥和私钥对. 随机选择一个 256 位的私钥(通常是一个随机数), 使用椭圆曲线数字签名算法(ECDSA)对私钥进行椭圆曲线乘法, 以生成相应的公钥.
2. 对公钥进行 SHA-256 哈希运算, 得到哈希结果.
3. 对哈希结果进行 RIPEMD-160 哈希运算, 得到 RIPEMD-160 哈希值.
4. 在 RIPEMD-160 哈希值前面添加一个版本字节(通常是 0x00).
5. 对上一步得到的结果再进行两次 SHA-256 哈希运算, 得到两次哈希结果, 取前四个字节(32 位)作为校验和. 将校验和添加到版本字节和 RIPEMD-160 哈希值后面.
6. 对结果进行 Base58 编码, 得到最终的比特币地址.

我们使用更简洁的形式表示上述计算步骤如下:

```text
BASE58(VERSION + RIPEMD-160(SHA-256(PUBKEY)) + CHECKSUM)
```

举一个实际的例子, 假设我们选择的私钥为: `0x5f6717883bef25f45a129c11fcac1567d74bda5a9ad4cbffc8203c0da2a1473c`

步骤一: 生成公钥. 在该案例中, 选择采用[比特币公钥的非压缩表示](https://en.bitcoin.it/wiki/BIP_0137), 因此需要在公钥前增加 `0x04`:

```text
PUBKEY: 0x04fb95541bf75e809625f860758a1bc38ac3c1cf120d899096194b94a5e700e891c7b6277d32c52266ab94af215556316e31a9acde79a8b39643c6887544fdf58c
```

步骤二: 对公钥进行 SHA-256 哈希运算:

```text
SHA-256(PUBKEY): 0xc96fc67faa800de318682f8db817603b22b0f6831be40cc21784ef88cf804ffd
```

步骤三: 对哈希结果进行 RIPEMD-160 哈希运算:

```text
RIPEMD-160(SHA-256(PUBKEY)): 0x6c435f69b29dde0a1451e511e637ae4148e31f5e
```

步骤四: 在 RIPEMD-160 哈希值前面添加版本字节(0x00):

```text
VERSION + RIPEMD-160(SHA-256(PUBKEY)): 0x006c435f69b29dde0a1451e511e637ae4148e31f5e
```

步骤五: 对上一步得到的结果进行两次 SHA-256 哈希运算:

```text
SHA-256(SHA-256(VERSION + RIPEMD-160(SHA-256(PUBKEY)))): 0xf316e4544b2ef49d65b8ffa95c68fef32288a7be314e11c4aff1745bd4b059f5
```

取前四个字节(32 位)作为校验和:

```text
CHECKSUM: 0xf316e454
```

步骤六: 将校验和添加到 VERSION + RIPEMD-160 哈希值后面:

```text
VERSION + RIPEMD-160(SHA-256(PUBKEY)) + CHECKSUM: 0x006c435f69b29dde0a1451e511e637ae4148e31f5ef316e454
```

步骤七: 对结果进行 Base58 编码, 得到最终的比特币地址:

```text
ADDRESS: 1AsSgrcaWWTdmJBufJiGWB87dmwUf2PLMZ
```

代码实现

```py
import base58
import hashlib
import ripemd.ripemd160

ripemd160 = ripemd.ripemd160.ripemd160
sha256 = lambda x: hashlib.sha256(x).digest()

pubkey = bytes.fromhex(''.join([
    '04',
    'fb95541bf75e809625f860758a1bc38ac3c1cf120d899096194b94a5e700e891',
    'c7b6277d32c52266ab94af215556316e31a9acde79a8b39643c6887544fdf58c'
]))
print('pubkey', pubkey.hex())

pubkey_hash = ripemd160(sha256(pubkey))
print('pubkey_hash', pubkey_hash.hex())
version = b'\x00'
checksum = sha256(sha256(version + pubkey_hash))
print('checksum', checksum.hex())
address = base58.b58encode(version + pubkey_hash + checksum[:4])
print(address)
```

## P2PKH 压缩

P2PKH 压缩地址格式与非压缩地址格式只有第一步有不同, 即公钥的表示形式. 具体而言, 在椭圆曲线上每一个 x 点对应两个 y 点, 且 y 为一奇一偶, 因此为了节约空间不需要在公钥中记录 y 的实际值, 而仅需记录 y 的奇偶性即可. 压缩格式公钥以 0x02(偶) 或 0x03(奇) 开头, 后仅跟 x.

```text
PUBKEY: 02fb95541bf75e809625f860758a1bc38ac3c1cf120d899096194b94a5e700e891
```

代码实现

```py
import base58
import hashlib
import ripemd.ripemd160

ripemd160 = ripemd.ripemd160.ripemd160
sha256 = lambda x: hashlib.sha256(x).digest()

pubkey = bytes.fromhex(''.join([
    '02',
    'fb95541bf75e809625f860758a1bc38ac3c1cf120d899096194b94a5e700e891',
]))
print('pubkey', pubkey.hex())

pubkey_hash = ripemd160(sha256(pubkey))
print('pubkey_hash', pubkey_hash.hex())
version = b'\x00'
checksum = sha256(sha256(version + pubkey_hash))
print('checksum', checksum.hex())
address = base58.b58encode(version + pubkey_hash + checksum[:4])
print(address)
```

最终计算得到地址: `1Bfbi4fi8hfKMAsbTvbSjiqaqutfVs3PUK`
