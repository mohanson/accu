# Solana/账户模型/账户数据结构

在 solana 中, 每个账户基本上是一个个"数据存储单元". 这些账户不仅用于存储 sol(solana 的原生代币), 还可以存储一些额外的数据, 比如智能合约的合约代码以及状态.

根据账户中存储的数据的不同, solana 的账户可以分为三大类:

- 普通账户: 也就是我们常用的钱包账户, 用于存储和转账 sol 余额.
- 程序账户: 用于存储智能合约的逻辑代码.
- 数据账户: 用于存储智能合约的状态数据.

值得注意的是, solana 的原生代币 sol 由一个特殊的程序账户, 即系统程序管理, 因此我们也可以说, 普通账户是一种特殊的数据账户.

Solana 账户的数据结构比较简单, 我们可以通过 rpc 来查询一个账户的详细信息. 我们只需要知道钱包地址, 就能通过 rpc 请求获取该账户的详细数据.

首先, 假设我们要查询的钱包地址是 `6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt`. 我们可以使用 solana 的 [get_account_info](https://solana.com/zh/docs/rpc/http/getaccountinfo) rpc 方法来查询该钱包地址的账户信息. 方法如下:

```py
import json
import pxsol

prikey = pxsol.core.PriKey.int_decode(1)
pubkey = prikey.pubkey()  # 6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt
result = pxsol.rpc.get_account_info(pubkey.base58(), {})
print(json.dumps(result, indent=4))
```

当然我们也可以不借助 pxsol 而直接使用 curl 来构造请求, 其最终结果是一致的.

```sh
curl -X POST http://127.0.0.1:8899 \
    -H "Content-Type: application/json" \
    -d '{
        "jsonrpc": "2.0",
        "id": 1,
        "method": "getAccountInfo",
        "params": ["6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt"]
    }'
```

两种方式都能得到返回数据如下:

```json
{
    "data": [
        "",
        "base64"
    ],
    "executable": false,
    "lamports": 500000000000000000,
    "owner": "11111111111111111111111111111111",
    "rentEpoch": 0,
    "space": 0
}
```

这些返回的数据字段的含义是什么呢? 让我们一一解释.

- `data`: 该字段包含了账户存储的实际数据. 数据是以 base64 编码的形式返回的, 因此你需要解码它才能看到实际内容.
    - 对于普通钱包账户, 通常这个字段是空的, 或者它包含一些额外的信息, 比如账户的状态.
    - 对于程序账户, 该字段存储了智能合约的代码.
    - 对于数据账户, 该字段包含了智能合约的状态信息.
- `executable`: 该字段是一个布尔值, 表示该账户是否是智能合约账户. 如果是智能合约账户, 这个字段会为 true, 意味着账户可以执行一些操作. 对于普通账户和数据账户, 这个字段通常是 false, 因为它只是存储数据并不执行代码.
- `lamports`: 该字段表示账户的余额. Solana 的最小货币单位是 lamport, 1 sol 等于 10⁹ lamport. 在这个例子中, 500000000000000000 lamport 等于 500000000 sol. 所以你可以通过这个字段看到账户当前的 sol 余额.
- `owner`: 该字段表示这个账户是由哪个程序控制的. 对于普通钱包账户, 这个字段通常是 `11111111111111111111111111111111`, 它表示 solana 系统程序管理着该账户. 对于数据账户而言, 该字段就会是它所关联着的程序账户.
- `rentEpoch`: 一个遗留字段, 源自 solana 曾经有一个机制定期从账户中扣除 lamport. 虽然此字段仍然存在于账户类型中, 但自从 solana v1.14 版本周期性租金收取功能被彻底弃用后, 它已不再使用.
- `space`: 简单表示 `data` 字段的长度. 一个账户最多可以存储 10 兆的数据.

您可以看到, 不同类型的账户, 其底层其实共享着完全相同的数据结构, 我们更多是从功能上对账户类型进行区分. 与其他区块链相比, solana 的账户模型简化了许多复杂的管理机制(当然, 老实说, 也带来了一些新的问题, 要解释清楚这件事情相当复杂...).
