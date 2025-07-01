# Solana/SPL Token/铸造账户解析

铸造账户是用于定义和管理代币的核心账户类型. 铸造账户存储了代币的基本信息, 例如代币的供应量, 小数位数, 铸造权限以及冻结权限. 在 token-2022 升级中, 铸造账户还可以包含扩展字段, 以支持额外的功能, 例如代币元数据, 代币转账手续费等. 目前使用最广泛的是两个代币扩展: 元数据指针扩展以及元数据扩展.

我们使用下面的代码解析上一小节我们创建的代币.

```py
import base64
import pxsol

info = pxsol.rpc.get_account_info('2CMXJX8arHRsiiZadVheRLTd6uhP7DpbaJ9hRiRMSGcF', {})
data = bytearray(base64.b64decode(info['data'][0]))
mint = pxsol.core.TokenMint.serialize_decode(data)
print(mint)
# {
#     "auth_mint": "6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt",
#     "supply": 0,
#     "decimals": 9,
#     "inited": true,
#     "auth_freeze": "6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt",
#     "extensions": {
#         "metadata_pointer": {
#             "auth": "6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt",
#             "hold": "2CMXJX8arHRsiiZadVheRLTd6uhP7DpbaJ9hRiRMSGcF"
#         },
#         "metadata": [
#             {
#                 "auth_update": "6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt",
#                 "mint": "2CMXJX8arHRsiiZadVheRLTd6uhP7DpbaJ9hRiRMSGcF",
#                 "name": "PXSOL",
#                 "symbol": "PXS",
#                 "uri": "https://raw.githubusercontent.com/mohanson/pxsol/refs/heads/master/res/pxs.json",
#                 "addition": {}
#             }
#         ]
#     }
# }
```

## 基础字段解析

- `auth_mint`: 铸造权限. 表示有权铸造(发行)新代币的账户地址. 此账户可以调用链上指令来增加代币供应量. 在本例中, 铸造权限归属于地址 `6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt`.
- `supply`: 当前代币的总供应量. 当前此代币供应量为 0, 表明尚未铸造任何代币.
- `decimals`: 代币的小数位数, 决定了代币的最小单位. 例如, decimals=9 表示代币的最小单位是 1/10⁹(即 0.000000001). 这与以太坊上 erc-20 代币的 decimals 字段类似.
- `inited`: 表示铸造账户是否已初始化. 只有正确初始化的铸造账户可用于代币操作.
- `auth_freeze`: 冻结权限表示有权冻结或解冻代币账户的地址. 冻结功能可用于暂停代币的转账操作, 通常用于合规性或安全管理. 在本例中, 冻结权限与铸造权限相同, 均为 `6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt`.

## 扩展字段解析

Token-2022 程序的一大特点是支持扩展功能, 这些功能通过 `extensions` 字段实现. 在本例中, 铸造账户包含了两种扩展: `metadata_pointer` 与 `metadata`.

扩展 `metadata_pointer` 表示为元数据指针, 也就是指明当前代币的元数据信息存储在哪里. 字段 `auth` 表明谁有权限修改元数据指针, 字段 `hold` 表明元数据的存储账户地址. 我们可以将元数据存储在铸造账户中, 也可以将元数据存储在另一个独立账户里. 不过就我来看, 允许将元数据信息和铸造信息分开存储更多是为了维持与旧版本的兼容性, 现实中您不应该这么做.

扩展 `metadata` 表示为元数据. 您可以很容易通过字段名来分析出大部分字段的用处, 因此我不再做多解释. 需要额外注意的是其中的 `addition` 字段, 它是一个 key/value 结构, 用于为代币提供更多的标识信息, 可便于在钱包或去中心化应用中展示.
