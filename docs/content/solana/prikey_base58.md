# Solana/私钥, 公钥与地址/Base58

Base58 是一种将二进制数据转换为人类可读文本的编码方式, 因其字符集包含 58 个字符而得名. 它最初由比特币的创始人中本聪设计, 用于比特币地址的生成, 后来被广泛应用于区块链, 加密货币和其他技术领域.

## Base58 的起源

Base58 的起源可以追溯到 2008 年, 当时中本聪发布了比特币白皮书并开始开发比特币协议. 在设计比特币地址时, 他需要一种方法将复杂的公钥哈希转换为简洁, 用户友好的字符串. 传统的 base64 编码虽然高效, 但包含了容易混淆的字符(如 0 和 O, I 和 l)以及特殊符号(+ 和 /), 不适合手动输入或视觉识别.

为了解决这个问题, 中本聪在 2009 年提出了 base58 编码方案. 他从 base64 的 64 个字符中剔除了 0, O, I 和 l, 并去除了特殊符号, 最终定义了一个由 58 个字符组成的集合:

```text
123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz
```

此外, 中本聪还引入了一种带校验位的 base58 变体, 通过添加额外的校验位增强了错误检测能力.

## Base58 的工作原理

Base58 编码的过程类似于进制转换.

0. 将二进制数据视为一个大整数.
0. 用这个整数反复除以 58, 取余数映射到字符集中的字符.
0. 重复此过程直到商为 0, 生成最终字符串.

但有一点需要额外注意, 我们需要将十六进制值开头的每个零字节 (0x00) 转换为 base58 中的 1. 在数字开头放置零不会增加其大小(例如 0x12 与 0x0012 相同), 因此当我们转换为 base58 时, 开头的任何额外零都不会影响结果. 为了确保前导零对结果有影响, base58 编码包含一个手动步骤, 将所有前导 0x00 转换为 1.

例: 有十六进制数据 `ef5557e913d5e13e9390a2fb0eeca75d739eccd5249dc174587669db471ca1f2df10d7e17a`, 获取它的 base58 表示.

答:

```py
import pxsol

data = bytearray.fromhex('ef5557e913d5e13e9390a2fb0eeca75d739eccd5249dc174587669db471ca1f2df10d7e17a')
print(pxsol.base58.encode(data)) # 92EW9Qnnov7V3QLqToHsFNyEnQ6vvJdYiLgBTfLCv3J5XJjnh1K
```

## Base58 的代码实现

您可以在 [pxsol.base58](https://github.com/mohanson/pxsol/blob/master/pxsol/base58.py) 找到一份 base58 的简单 python 实现.

```py
# Copyright (C) 2011 Sam Rushing
# Copyright (C) 2013-2014 The python-bitcoinlib developers
#
# This file is part of python-bitcoinlib.
#
# It is subject to the license terms in the LICENSE file found in the top-level
# directory of this distribution.
#
# No part of python-bitcoinlib, including this file, may be copied, modified,
# propagated, or distributed except according to the terms contained in the
# LICENSE file.

# Base58 encoding and decoding

B58_DIGITS = '123456789ABCDEFGHJKLMNPQRSTUVWXYZabcdefghijkmnopqrstuvwxyz'


def encode(b: bytearray) -> str:
    # Encode bytes to a base58-encoded string
    assert isinstance(b, bytearray)
    # Convert big-endian bytes to integer
    n = int.from_bytes(b)
    # Divide that integer into bas58
    res = []
    while n > 0:
        n, r = divmod(n, 58)
        res.append(B58_DIGITS[r])
    res = ''.join(res[::-1])
    # Encode leading zeros as base58 zeros
    czero = 0
    pad = 0
    for c in b:
        if c == czero:
            pad += 1
        else:
            break
    return B58_DIGITS[0] * pad + res


def decode(s: str) -> bytearray:
    # Decode a base58-encoding string, returning bytes.
    if not s:
        return bytearray()
    # Convert the string to an integer
    n = 0
    for c in s:
        n *= 58
        assert c in B58_DIGITS
        digit = B58_DIGITS.index(c)
        n += digit
    # Convert the integer to bytes
    res = bytearray(n.to_bytes(max((n.bit_length() + 7) // 8, 1)))
    # Add padding back.
    pad = 0
    for c in s[:-1]:
        if c == B58_DIGITS[0]:
            pad += 1
        else:
            break
    return bytearray(pad) + res
```
