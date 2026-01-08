# Solana/交易/序列化与反序列化

## 示例交易

> 为了避免读者不停切换页面, 我将待分析的交易复制在了每一小节的开头.

```json
{
    "signatures": [
        "3NPdLTf2Xp1XUu82VVVKgQoHfiUau3wGPTKAhbNzm8Rx5ebNQfHBzCGVsagXyQxRCeEiGr1jgr4Vn32UEAx1Aov3"
    ],
    "message": {
        "header": [
            1,
            0,
            1
        ],
        "account_keys": [
            "6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt",
            "8pM1DN3RiT8vbom5u1sNryaNT1nyL8CTTW3b5PwWXRBH",
            "11111111111111111111111111111111"
        ],
        "recent_blockhash": "6vAwzjtGMrN3mJ8o7iGVDjMM46e2AnctqmjvLbqtESrx",
        "instructions": [
            {
                "program": 2,
                "account": [
                    0,
                    1
                ],
                "data": "3Bxs3zzLZLuLQEYX"
            }
        ]
    }
}
```

## 序列化与反序列化

Solana 的交易在签名, 传播和存储时, 它们是序列化的. 序列化是指将数据结构转换为字节流的过程, 以便在网络中传输或存储. 反序列化则是相反的过程, 将字节流重新解析为原始的数据结构. Solana 使用一种高效的二进制格式来实现序列化和反序列化, 这种格式在性能和数据紧凑性之间取得了平衡.

Solana 的序列化过程基于一种自定义的二进制编码格式, 设计目标是高效且无歧义. 该序列化方式没有名字, 但特点明显且十分简单. 大体上来说, 它基于以下两个基本规则:

- 紧凑编码: solana 使用变长整数(compact-u16)来表示长度字段. 例如, 账户数量或签名数量会根据实际值的大小动态编码, 而不是固定占用 2 个字节. 这种方式下减少了不必要的空间浪费.
- 顺序存储: 交易的各个部分按固定顺序排列, 例如先存储签名数量, 再存储签名数据, 然后是消息内容. 这种顺序性简化了反序列化的逻辑.

例如, 一个简单的转账交易在序列化后可能是这样的字节流:

1. 签名数量(1 字节或更多, 变长编码).
2. 签名数据(每个 64 字节, 按顺序排列).
3. 消息头部(3 字节).
4. 账户数量(1 字节或更多, 变长编码).
5. 账户地址(每个 32 字节, 按顺序排列).
6. 最近区块哈希(32 字节).
7. 指令数量(1 字节或更多, 变长编码).
8. 指令内容
    1. 程序索引(1 字节).
    2. 账户数量(1 字节或更多, 变长编码).
    3. 账户索引(每个 1 字节, 按顺序排列).
    4. 参数长度(1 字节或更多, 变长编码).
    5. 参数数据.

## 使用变长编码表示长度

Solana 序列化算法中采用的变长整数编码称作 compact-u16. 该算法的核心思想是将 16 位整数(最大值 65535)用 1 到 3 个字节表示, 具体字节数取决于数值的大小. 它的编码规则类似于传统 vlq 编码, 通过在每个字节中使用 7 位来存储实际数据, 并用最高位(第 8 位)作为"延续位"来指示是否需要读取后续字节.

具体编码过程如下:

- 小于 128(0x7f)的值, 只需 1 个字节. 最高位设为 0, 表示没有后续字节. 剩余 7 位存储数值.

例: 数值 5(二进制 00000101)编码是多少?

答:

```py
import pxsol

assert pxsol.compact_u16.encode(5) == bytearray([0x05])
```

- 128 到 16383(0x3fff)的值, 需要 2 个字节. 第一个字节的最高位设为 1, 表示有后续字节; 低 7 位存储数值的低 7 位. 第二个字节的最高位设为 0, 表示结束; 低 7 位存储数值的剩余部分.

例: 数值 132(二进制 10000100)编码是多少?

答: 第一个字节: 0x84(10000100, 延续位 1, 数据 0000100). 第二个字节: 0x01(00000001, 延续位 0, 数据 0000001).

```py
import pxsol

assert pxsol.compact_u16.encode(132) == bytearray([0x84, 0x01])
```

- 大于 16383 的值, 需要 3 个字节. 前两个字节的延续位都设为 1, 分别存储低 14 位. 第三个字节的延续位设为 0, 存储剩余部分.

例: 数值 65535(二进制 11111111 11111111)编码是多少?

答:

```py
import pxsol

assert pxsol.compact_u16.encode(65535) == bytearray([0xff, 0xff, 0x03])
```

在 solana 中, 交易内部的数据通常较小, 长度一般会在 128 以内. 使用 compact-u16, 这些值可以用单个字节表示, 而不是固定使用 2 个字节, 从而减少传输和存储成本.

## 习题

例: 您能从序列化的十六进制交易形式手动解码 ada 的交易吗? 交易数据如下.

```
01767ae26660c142941a5961f6dec7237cae733edfe6517c37fbb8481f46bbb53ce300e714b4784
0142c93a4e6600c50fda97560ab641db0ce19559b251d66df04010001034cb5abf6ad79fbf5abbc
cafcc269d85cd2651ed4b885b5869f241aedf0a5ba297422b9887598068e32c4448a949adb290d0
f4e35b9e01b0ee5f1a1e600fe267400000000000000000000000000000000000000000000000000
0000000000000057e9774a3cad5c33f1fb6b37a03d4f009a31098118d2ceaebf430af301ad250d0
1020200010c0200000000ca9a3b00000000
```

答:

```text
01                                                               tx.signatures.length
767ae26660c142941a5961f6dec723....7560ab641db0ce19559b251d66df04 tx.signatures[0]
01                                                               tx.message.header[0]
00                                                               tx.message.header[1]
01                                                               tx.message.header[2]
03                                                               tx.message.account_keys.length
4cb5abf6ad79fbf5abbccafcc269d85cd2651ed4b885b5869f241aedf0a5ba29 tx.message.account_keys[0]
7422b9887598068e32c4448a949adb290d0f4e35b9e01b0ee5f1a1e600fe2674 tx.message.account_keys[1]
0000000000000000000000000000000000000000000000000000000000000000 tx.message.account_keys[2]
57e9774a3cad5c33f1fb6b37a03d4f009a31098118d2ceaebf430af301ad250d tx.message.recent_blockhash
01                                                               tx.message.instructions.length
02                                                               tx.message.instructions[0].program
02                                                               tx.message.instructions[0].account.length
00                                                               tx.message.instructions[0].account[0]
01                                                               tx.message.instructions[0].account[1]
0c                                                               tx.message.instructions[0].data.length
0200000000ca9a3b00000000                                         tx.message.instructions[0].data
```

## 注意事项

- 变长编码 compact-u16 仅用于表示长度. 交易中的程序索引, 账户索引值则是直接使用 u8 来表示.
