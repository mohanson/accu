# Solana/交易/手工构造交易

夫交易者, 数字雕琢而出, 财富流动之诗也.

匠人之手, 运字节于毫端, 化混沌为有序, 宛若琢玉成器, 精妙不可言.

本节课程中, 我们会学习如何以手工方式构造一笔 solana 转账交易. 通过这个过程, 希望您能更加深入了解 solana 的交易结构.

## 我们的目标是

假设 ada 要向 bob 支付 2 sol, 同时 bob 要向 cuc 支付 1 sol. 请在一个交易里实现 ada 和 bob 二人的要求.

## 定义交易的参与者

这笔交易总共有四个参与者, 分别如下:

- `ada`: 私钥为 `1`.
- `bob`: 私钥为 `2`.
- `cuc`: 公钥为 `HPYVwAQmskwT1qEEeRzhoomyfyupJGASQQtCXSNG8XS2`.

在 solana 中, 转账是通过系统程序完成的, 它的地址是固定的:

- `系统程序`: `11111111111111111111111111111111`.

> 绝密信息: cuc 的地址所对应的私钥为 0x03.

## 构造指令

Solana 的交易由一条或多条指令组成. 对于本交易, 我们需要构造两个转账指令.

Solana 交易中的指令仅存储程序和账户的索引, 而具体的账户信息(公钥和权限)却并不存储在指令中. 这让我们在构建交易时十分的被动. 为此, pxsol 实现了两个辅助数据结构:

- `pxsol.core.AccountMeta`. AccountMeta 包含账户公钥以及其账户权限. 在本示例中, ada 与 bob 的权限应当是需要签名且可写, cuc 的权限应当是无需签名且可写.
- `pxsol.core.Requisition`. Requisition 自身包含一条交易指令的全部数据, 并且能在稍后构建交易时, 将自身"编译"为使用索引的指令.

构造如下代码:

```py
import pxsol

ada = pxsol.core.PriKey.int_decode(1)
bob = pxsol.core.PriKey.int_decode(2)
cuc = pxsol.core.PubKey.base58_decode('HPYVwAQmskwT1qEEeRzhoomyfyupJGASQQtCXSNG8XS2')

# Transfer from ada to bob, 2 sol
r0 = pxsol.core.Requisition(pxsol.program.System.pubkey, [], bytearray())
r0.account.append(pxsol.core.AccountMeta(ada.pubkey(), 3))
r0.account.append(pxsol.core.AccountMeta(bob.pubkey(), 1))
r0.data = pxsol.program.System.transfer(2 * pxsol.denomination.sol)

# Transfer from bob to cuc, 1 sol
r1 = pxsol.core.Requisition(pxsol.program.System.pubkey, [], bytearray())
r1.account.append(pxsol.core.AccountMeta(bob.pubkey(), 3))
r1.account.append(pxsol.core.AccountMeta(cuc, 1))
r1.data = pxsol.program.System.transfer(1 * pxsol.denomination.sol)
```

## 组建交易

使用 `pxsol.core.Transaction.requisition_decode` 方法, 将上文定义的两个请求编译为指令并组装在一个交易里. 该方法的第一个参数表示应该由谁支付手续费, 第二个参数则是 Requisition 列表. 在本示例中, 我们决定由 ada 付出交易手续费.

```py
tx = pxsol.core.Transaction.requisition_decode(ada.pubkey(), [r0, r1])
```

## 获取最近区块哈希

使用 rpc 接口获取 solana 的最近区块哈希.

```py
tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
```

## 签名交易

组装好交易后, ada 和 bob 需要用他们的私钥对交易进行签名. 此步骤需注意签名顺序与账户列表顺序应当匹配. 在本示例中, ada 的签名要放置在 bob 的签名之前. 您可以根据以下两条规则简单评估签名的顺序:

0. 支付手续费的账户总是在签名列表最前.
0. 可写的账户总在只读账户之前.
0. 按照账户在交易中出现的先后顺序排列.

代码调用如下:

```py
tx.sign([ada, bob])
```

## 最终交易结构

使用 `print(tx)` 可以将交易完整打印如下.

```json
{
    "signatures": [
        "2DNYcExSuLB1BgkB7p3gSFEuWvwgnCbcBXtENBgU9tXGQdfknvST4c3U1uQ7AEAwbEc6D1qzxMQhjdiTQytE3A24",
        "42hH4QE2r9w4yRE9CQGZq7N16Pr4712sPU6myqQNAaaAxo8A8F7HB9d46By4EVXbmRJVYMNHSgdHfXmv9XY4TFud"
    ],
    "message": {
        "header": [
            2,
            0,
            1
        ],
        "account_keys": [
            "6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt",
            "8pM1DN3RiT8vbom5u1sNryaNT1nyL8CTTW3b5PwWXRBH",
            "HPYVwAQmskwT1qEEeRzhoomyfyupJGASQQtCXSNG8XS2",
            "11111111111111111111111111111111"
        ],
        "recent_blockhash": "FSLe6dD3NxjJacCSW9P3LSyzpZd6H4SHSUCcCFUaTQwj",
        "instructions": [
            {
                "program": 3,
                "account": [
                    0,
                    1
                ],
                "data": "3Bxs3zzLZLuLQEYX"
            },
            {
                "program": 3,
                "account": [
                    1,
                    2
                ],
                "data": "3Bxs3zvX19cRxrhM"
            }
        ]
    }
}
```

## 提交交易

将签名后的交易序列化为字节, 通过 solana 的 rpc 接口 `send_transaction` 提交到网络. 网络将会验证交易的签名, 检查余额并执行转账.

```py
txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
assert pxsol.base58.decode(txid) == tx.signatures[0]
pxsol.rpc.wait([txid])
```

几秒钟后, bob 和 cuc 的账户就会各自多了 1 sol!

## 完整代码

```py
import base64
import pxsol

ada = pxsol.core.PriKey.int_decode(1)
bob = pxsol.core.PriKey.int_decode(2)
cuc = pxsol.core.PubKey.base58_decode('HPYVwAQmskwT1qEEeRzhoomyfyupJGASQQtCXSNG8XS2')

r0 = pxsol.core.Requisition(pxsol.program.System.pubkey, [], bytearray())
r0.account.append(pxsol.core.AccountMeta(ada.pubkey(), 3))
r0.account.append(pxsol.core.AccountMeta(bob.pubkey(), 1))
r0.data = pxsol.program.System.transfer(2 * pxsol.denomination.sol)

r1 = pxsol.core.Requisition(pxsol.program.System.pubkey, [], bytearray())
r1.account.append(pxsol.core.AccountMeta(bob.pubkey(), 3))
r1.account.append(pxsol.core.AccountMeta(cuc, 1))
r1.data = pxsol.program.System.transfer(1 * pxsol.denomination.sol)

tx = pxsol.core.Transaction.requisition_decode(ada.pubkey(), [r0, r1])
tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
tx.sign([ada, bob])
txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
assert pxsol.base58.decode(txid) == tx.signatures[0]
pxsol.rpc.wait([txid])
```

> 使用两个辅助数据结构: pxsol.core.AccountMeta 和 pxsol.core.Requisition 让手工构造 solana 交易变得简单和有趣!
