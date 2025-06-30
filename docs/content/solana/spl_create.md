# Solana/SPL Token/创建您的代币

Pxsol 的内置钱包集成了一个简单且通用的接口, 用于创建您的 spl token (以及执行通用的 spl 操作).

## 创建代币

```py
import pxsol

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
spl = ada.spl_create(
    'PXSOL',
    'PXS',
    'https://raw.githubusercontent.com/mohanson/pxsol/refs/heads/master/res/pxs.json',
    9,
)
print(spl) # 2CMXJX8arHRsiiZadVheRLTd6uhP7DpbaJ9hRiRMSGcF
```

上述代码运行后, 在 `2CMXJX8arHRsiiZadVheRLTd6uhP7DpbaJ9hRiRMSGcF` 地址上创建了一个新的代币. 函数方法 `spl_create()` 接收四个参数, 分别是:

- `name`: 代币名称.
- `symbol`: 代币符号.
- `uri`: 代币元数据的 json 文件地址.
- `decimals`: 小数位, 例如 decimals=9 时, 1000000000 表示 1 个代币.

代币元数据的 json 文件的典型结构如下. 你需要将此 json 文件上传到公共可访问的服务器, 例如 arweave 或 ipfs, 然后在创建代币时将该文件地址作为参数传入 uri.

```json
{
    "name": "PXSOL",
    "symbol": "PXS",
    "description": "Proof of study https://github.com/mohanson/pxsol",
    "image": "https://raw.githubusercontent.com/mohanson/pxsol/refs/heads/master/res/pxs.png"
}
```

## 交易费用

创建一个新的 spl token, 大约需要 0.004 sol 的租金以及 0.00001 sol 的交易费用. 截止至 2025 年 6 月, 总价值大概 $0.6 美元, 四舍五入等于不要钱!
