# Solana/SPL Token/铸造代币和查询代币余额

## 铸造代币和查询代币余额

您可以通过简单的代码为任意用户增发指定数量的代币余额. 注意: 只有代币的创建者有权限增发代币!

使用 `spl_mint()` 方法增发的代币数量需考虑小数位, 例如, 若 decimals=9, 则 1000000000 表示 1 个代币.

类似的, 使用 `spl_balance()` 方法查询您的代币余额时, 函数将返回一个数组: 数组第 0 位表示您拥有的代币数量, 第 1 位表示该代币的小数位.

```py
import pxsol

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
spl = pxsol.core.PubKey.base58_decode('2CMXJX8arHRsiiZadVheRLTd6uhP7DpbaJ9hRiRMSGcF')

ada.spl_mint(spl, ada.pubkey, 100000000 * 10 ** 9)
print(ada.spl_balance(spl)) # [100000000000000000, 9]
```

## 关联代币账户

与我们之前写的泰铢币程序一样, 您的代币实质上存储于一个 pda 账户里. 我们习惯称呼该账户为关联代币账户(associated token account, ata), 它是用于存储和管理用户持有 spl token 的特殊账户.

- 每个 ata 唯一对应于一个普通钱包账户和一个代币的地址.
- 由程序自动生成, 遵循确定性地址规则, 确保同一个钱包和代币组合始终生成相同的 ata 地址.
- 存储用户的代币余额, 并记录与该代币相关的操作(如转账, 增发, 销毁).

当您使用 pxsol 的 `spl_mint()` 方法增发代币时, 如果目标用户还没有 ata 账户, pxsol 会自动为其生成 ata 账户. 我们可以使用 rpc 查询 ata 账户数据, 获得返回数据如下.

```py
import base64
import pxsol

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
spl = pxsol.core.PubKey.base58_decode('2CMXJX8arHRsiiZadVheRLTd6uhP7DpbaJ9hRiRMSGcF')
ata = ada.spl_account(spl)

info = pxsol.rpc.get_account_info(ata.base58(), {})
data = base64.b64decode(info['data'][0])
print(data.hex())
```

返回数据总共长 170 个字节, 我们对其进行详细分析.

```
11c447d79a76ef38a896d72fe54b373bab14dcba868425645a1670180e656780 代币的地址
4cb5abf6ad79fbf5abbccafcc269d85cd2651ed4b885b5869f241aedf0a5ba29 用户的普通钱包地址
00008a5d78456301                                                 余额, 小端序表示, 为 100000000 * 10 ** 9
00000000                                                         是否设置代理地址 (delegate), 0=未设置
0000000000000000000000000000000000000000000000000000000000000000 代理地址
01                                                               账户状态(0=未初始化, 1=已初始化, 2=冻结)
00000000                                                         是否为原生代币, 0=非原生代币, 符合预期
0000000000000000                                                 若为原生代币时, 记录其租赁豁免阈值
0000000000000000                                                 委托金额
00000000                                                         是否允许关闭帐户
0000000000000000000000000000000000000000000000000000000000000000 关闭帐户的权限拥有者地址
02                                                               账户类型(0=未初始化, 1=铸造账户, 2=持仓账户)
0700                                                             代币扩展(7=不可改变账户所有权)
0000                                                             代币扩展(填充, 无实际意义)
```

您可以参考以下两个源代码链接, 这有助于您加深对 ata 账户的理解.

- [基础账户类型](https://github.com/solana-program/token-2022/blob/a2ddae7f39d6bb182b0595fa3f48e38e94e7c684/program/src/pod.rs#L64-L85)
- [账户类型以及扩展字段](https://github.com/solana-program/token-2022/blob/a2ddae7f39d6bb182b0595fa3f48e38e94e7c684/program/src/extension/mod.rs#L1036-L1137)

在多数情况下, 我们只会关注前三个字段, 也就是代币的地址, 用户的普通钱包地址以及余额.

## 习题

例: Bob 是否被允许铸造新代币? 请编写代码尝试.

答:

```py
import pxsol

bob = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(2))
spl = pxsol.core.PubKey.base58_decode('2CMXJX8arHRsiiZadVheRLTd6uhP7DpbaJ9hRiRMSGcF')

bob.spl_mint(spl, bob.pubkey, 100000000 * 10 ** 9)
# Exception: {
#     'code': -32002,
#     'message': 'Transaction simulation failed: Attempt to debit an account but found no record of a prior credit.',
#     'data': {
#         'accounts': None,
#         'err': 'AccountNotFound',
#         'innerInstructions': None,
#         'logs': [],
#         'replacementBlockhash': None,
#         'returnData': None,
#         'unitsConsumed': 0
#     }
# }
```
