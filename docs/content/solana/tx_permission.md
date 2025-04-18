# Solana/交易/账户与权限

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

## 账户列表

在 solana 交易中, `tx.message.account_keys` 是所有参与账户的列表. 看看我们的示例:

```json
"account_keys": [
    "6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt",
    "8pM1DN3RiT8vbom5u1sNryaNT1nyL8CTTW3b5PwWXRBH",
    "11111111111111111111111111111111"
]
```

在示例中, 我们的交易总共涉及到三个账户, 这三个账户分别是:

0. `6ASf5Ec...`: ada, 转账的发起者, 且支付了交易费用.
0. `8pM1DN3...`: bob, 转账的接收者.
0. `1111111...`: solana 系统程序(system program). 用于处理基础操作如转账.

账户列表定义了"谁参与"了这笔交易, 您可以这么理解这笔简单的交易:

0. ada 向 bob 转移了 1 sol, 这个操作会导致二人账户的余额发生变化, 因而显然他们的账户参与了交易.
0. 转账操作需要调用 solana 系统程序中的转账函数, 这个步骤会读取系统程序的代码, 因此认为系统程序也间接参与了交易.

账户列表的顺序不是任意的, 我们继续分析.

## 权限

在 solana 的交易结构中, 账户不仅是参与者, 还承载了权限和角色的定义. 账户**是否需要签名**, **是否可以被修改**, 都直接影响交易的执行逻辑. 这些权限的设置, 与交易的 `tx.message.header` 字段密切相关.

**是否需要签名?**

签名账户是交易的"授权者", 通常负责支付费用或批准操作. 在我们的例子中, ada 需要对交易进行签名, 而 bob 和 solana 系统程序不需要.

**是否可写?**

账户是否可写决定了它在交易中是否能被修改. 只读账户只能被读取, 不能更改状态. 在我们的例子中, ada 和 bob 是可写的, 但 solana 系统程序是只读的.

我们可以使用两个比特位来表示账户的权限. 第 0 个比特位表示是否可写, 第 1 个比特位表示是否需要签名, 如此, 账户权限能被表示为 0 到 3 之间的一个数字. 账户列表必须按照权限从高到低排列:

| 账户索引 |     地址     | 需要签名 | 可写 | 权限(0-3) |     角色     |
| -------- | ------------ | -------- | ---- | --------- | ------------ |
| 0        | `6ASf5Ec...` | 是       | 是   | 3         | ada (付款方) |
| 1        | `8pM1DN3...` | 否       | 是   | 1         | bob (接收者) |
| 2        | `1111111...` | 否       | 否   | 0         | 系统程序     |

账户列表的权限以一种压缩方式被保存在 `tx.message.header` 中.

```json
"header": [1, 0, 1]
```

这些数字与 `tx.message.account_keys` 中的账户列表结合, 决定了每个账户的权限状态. 它是一个包含三个数字的数组, 分别表示:

- 需要签名账户数: 这里是 1, 表示需要 1 个签名, 与 `tx.signatures` 数组长度一致.
- 需要签名, 只读账户数: 这里是 0.
- 无需签名, 只读账户数: 这里是 1.

以程序代码来描述这里的逻辑的话, 可以表示如下:

- `tx.header[0]` 为权限 >= 2 的账户数量.
- `tx.header[1]` 为权限 == 2 的账户数量.
- `tx.header[2]` 为权限 == 0 的账户数量.

只读账户无需状态变更, 这一特性使得 solana 能够充分利用并行处理能力, 从而显著提升交易吞吐量. 并行执行交易一直是区块链行业面临的一大技术难题, 因为交易通常会涉及对账户状态的修改, 而不同的执行顺序可能会导致截然不同的结果. 为了确保一致性和正确性, 传统区块链系统通常采用单核单线程的方式, 按顺序逐一处理交易. 这种方法虽然简单可靠, 但极大地限制了性能的扩展, 尤其是在高负载场景下. Solana 通过识别只读账户并优化状态管理, 打破了这一瓶颈, 实现了更高效的交易处理机制.

许多公链也试图解决这个问题, 以获得更高的 qps, 例如 ethereum 在 [eip-2930](https://eips.ethereum.org/EIPS/eip-2930) 中就打了一个补丁, 允许用户显示指定该笔交易访问了哪些账户数据, 以便节点可以并行处理互不相关的交易. 不过从作者的视角来看, 这个补丁显然十分的不成功, 在本书编写期间, 这种方式并没有在 ethereum 生态系统里被广泛采用. 相比之下, solana 为账号引入的权限系统, 似乎是一种更为高级和优雅的设计.
