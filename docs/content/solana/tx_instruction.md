# Solana/交易/指令

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

## 交易中的指令

Solana 的交易就像是信封, 而指令就是信封里的内容, 每个指令都告诉 solana 网络如何处理这笔交易. 就像我们把信放进信封里一样, 之后我们会将信封蜡封, 然后盖上自己的腊封印章. 最后别忘记了, 您还需要付邮费!

![img](../../img/solana/tx_instruction/letter.jpg)

- 正如信封中可以添加多封信件一样, 交易中也允许添加多个指令.
- 交易的签名就像腊封印章.
- 交易手续费就像信件邮费.

Solana 交易中的每个指令都执行特定的功能. 在示例交易中, ada 发送了一笔 sol 转账, 这笔交易背后其实就包含了一个转账指令. 这个指令告诉 solana 将指定金额从一个账户转移到另一个账户.

Solana 的交易指令有很多种, 像转账指令就是其中之一. 每种指令都由一个程序(也就是智能合约)来执行. 每个指令由三部分组成:

- program: 目标程序的索引(对应 account_keys 中的位置).
- account: 涉及的账户索引数组(对应 account_keys 中的位置).
- data: 传递给程序的二进制数据.

在示例中:

- `"program": 2`: 调用 `tx.message.account_keys[2]`, 即系统程序 `1111111...`.
- `"account": [0, 1]`: 使用 `tx.message.account_keys[0]` 和 `tx.message.account_keys[1]`.
- `"data": "3Bxs3zzLZLuLQEYX"`: 表示具体操作.

我们将 data 数据进行 base58 解码, 得到其十六进制表示的数据为 `0200000000ca9a3b00000000`. 系统程序 `1111111...` 会对数据进行解析, 前 4 个字节会被解析为内部函数索引, 后 8 个字节解释为转账的金额. 在示例中, 我们的内部函数索引为 2, 表示转账, 金额则为 1000000000 lamport.

```py
import pxsol

data = pxsol.base58.decode('3Bxs3zzLZLuLQEYX')
assert data.hex() == '0200000000ca9a3b00000000'

assert int.from_bytes(data[:4], 'little') == 2
assert int.from_bytes(data[4:], 'little') == 1 * pxsol.denomination.sol
```

不同的指令对于 account 和 data 有不同的要求, 这点在您使用除转账之外的其它指令时, 需要尤其注意. 在下一节中, 我将向您简单介绍 solana 的系统程序以及它所包含的内部函数.
