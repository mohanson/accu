# Solana/SPL Token/铸造代币和查询代币余额

这节课我们来谈谈铸币. 不过在谈历史之前, 我想先来谈谈铸币权的一些有趣小历史.

在接触到比特币之后, 我对经济学产生了广泛的兴趣, 尤其是对古代中国经济学. 古代中国的货币大体上经历了从贵金属货币(如金银)到纸币, 之后纸币信用广泛崩溃, 社会重新回到贵金属货币这样一个轮回.

三国时期, 约公元 220-280, 刘备为筹措军费, 铸造"直百五铢"钱, 面值远超实际金属价值(约 30 倍), 大量掠夺民间财富, 使得蜀汉短短几十年, 从*隆中对*描述的"沃野千里, 天府之土"变为"百姓凋瘁", 此等变化甚至引得蜀中大儒谯周作*仇国论*. 三国志吴书亦有记载说"入其朝不闻正言, 经其野民皆菜色".

一千两百年后, 明太祖朱元璋为统一货币, 减少铜钱依赖, 发行纸币"大明宝钞", 同时立法禁止金银流通. 大明宝钞不由朝廷发行, 而是由内府(一个非政府机构, 其存在只为服务皇帝个人)发行. 在宝钞发行初期, 尚能勉强维持其价值, 到其儿子朱棣时期, 一千两的大明宝钞只能在黑市换得两百两银, 以至于民间社会开始拒收大明宝钞.

此等例子数不胜数. **垄断铸币权的人一定会滥发新币**.

不管怎么说, 本教程毕竟不是历史书, 因此让我们收束一下发散的思维, 想一想我们如何来铸造新币吧!

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

- 每个关联代币账户唯一对应于一个普通钱包账户和一个代币的铸造账户.
- 由程序自动生成, 遵循确定性地址规则, 确保同一个钱包和代币组合始终生成相同的关联代币账户地址.
- 存储用户的代币余额.

当您使用 pxsol 的 `spl_mint()` 方法增发代币时, 如果目标用户还没有关联代币账户, pxsol 则会自动为其生成.

我们尝试使用 rpc 接口查询一个关联代币账户内存储的数据, 获得返回数据如下.

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

```txt
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

您可以参考以下两个源代码链接, 这有助于您加深对关联代币账户的理解.

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
