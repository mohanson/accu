# Solana/交易/交易详情

在上一节中, ada 向 bob 转移了 1 sol. 我们想查看这笔交易的详细内容, 为此, 我们使用 `pxsol.rpc.get_signatures_for_address` 来查询 ada 过去一段时间内的所有交易历史. 接口将返回交易的序列化格式数据, 对其进行反序列化就能得到一个 `pxsol.core.Transaction` 对象.

```py
import base64
import pxsol

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))

for e in pxsol.rpc.get_signatures_for_address(ada.pubkey.base58(), {'limit': 32}):
    tx_meta = pxsol.rpc.get_transaction(e['signature'], {'encoding': 'base64'})
    tx_byte = base64.b64decode(tx_meta['transaction'][0])
    tx = pxsol.core.Transaction.serialize_decode(tx_byte)
    print(tx)
```

> 如果存在多个交易, 交易将按照交易时间倒序排序输出.

我们检索到 ada 的原始交易, 对其进行解码, 格式化并查看它包含的内容. 结果如下所示:

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

实际的交易看起来和我们期待的不太一样. 您可能注意到, account_keys 的前两个条目中包含了 ada 和 bob 的地址, 但第三个条目一连串的 1 又表示的什么呢? Ada 所发送的 1 sol 输入又在哪里?

别担心, 接下来的时间里, 我会向您介绍交易中的每一个字段.
