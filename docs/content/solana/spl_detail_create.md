# Solana/SPL Token/指令详解(一)

在本课中, 我们将深入解读 `pxsol.wallet.Wallet` 类中的 `spl_create()` 方法. 这是一个高级接口, 用于在 solana 区块链上创建一个带有元数据的 spl token, 并初始化相关权限与租金豁免等功能.

## 源码

> 为了避免读者不停切换页面, 我将待分析的代码复制在了这里.

```py
def spl_create(self, name: str, symbol: str, uri: str, decimals: int) -> pxsol.core.PubKey:
    # Create a new token.
    mint_prikey = pxsol.core.PriKey.random()
    mint_pubkey = mint_prikey.pubkey()
    mint_size = pxsol.program.Token.size_extensions_base + pxsol.program.Token.size_extensions_metadata_pointer
    # Helper function to tack on the size of an extension bytes if an account with extensions is exactly the size
    # of a multisig.
    assert mint_size != 355
    addi_size = pxsol.program.Token.size_extensions_metadata + len(name) + len(symbol) + len(uri)
    mint_lamports = pxsol.rpc.get_minimum_balance_for_rent_exemption(mint_size + addi_size, {})
    r0 = pxsol.core.Requisition(pxsol.program.System.pubkey, [], bytearray())
    r0.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
    r0.account.append(pxsol.core.AccountMeta(mint_pubkey, 3))
    r0.data = pxsol.program.System.create_account(mint_lamports, mint_size, pxsol.program.Token.pubkey)
    r1 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
    r1.account.append(pxsol.core.AccountMeta(mint_pubkey, 1))
    r1.data = pxsol.program.TokenExtensionMetadataPointer.initialize(self.pubkey, mint_pubkey)
    r2 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
    r2.account.append(pxsol.core.AccountMeta(mint_pubkey, 1))
    r2.account.append(pxsol.core.AccountMeta(pxsol.program.SysvarRent.pubkey, 0))
    r2.data = pxsol.program.Token.initialize_mint(decimals, self.pubkey, self.pubkey)
    r3 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
    r3.account.append(pxsol.core.AccountMeta(mint_pubkey, 1))
    r3.account.append(pxsol.core.AccountMeta(self.pubkey, 0))
    r3.account.append(pxsol.core.AccountMeta(mint_pubkey, 0))
    r3.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
    r3.data = pxsol.program.Token.metadata_initialize(name, symbol, uri)
    tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [r0, r1, r2, r3])
    tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
    tx.sign([self.prikey, mint_prikey])
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    pxsol.rpc.wait([txid])
    return mint_pubkey
```

## 实现流程拆解

调用 `spl_create()` 方法, 实质上会组装并发送一笔交易, 该交易包含四条链上指令, 分别封装在 requisition 中, 依次执行如下.

**指令 1: 创建铸造账户**

```py
r0 = pxsol.core.Requisition(pxsol.program.System.pubkey, [], bytearray())
r0.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
r0.account.append(pxsol.core.AccountMeta(mint_pubkey, 3))
r0.data = pxsol.program.System.create_account(mint_lamports, mint_size, pxsol.program.Token.pubkey)
```

上述代码为新 spl token 分配一个租金豁免的账户. 账户大小需要包括基础数据与扩展数据. 参数 `mint_lamports` 是租金豁免的最低 lamports, 通过 rpc 查询获得.

**指令 2: 初始化元数据扩展指针**

```py
r1 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
r1.account.append(pxsol.core.AccountMeta(mint_pubkey, 1))
r1.data = pxsol.program.TokenExtensionMetadataPointer.initialize(self.pubkey, mint_pubkey)
```

上述代码启用 token-2022 的扩展字段: metadata pointer. 这是 token-2022 的一个特性, 允许你在铸造账户上挂载额外的元数据结构. 在稍后的指令中, 我们将实际去挂载数据, 该指令当前仅做申明使用. 除此扩展之外, token-2022 实际上还支持另外几十个不同的扩展, 您可以在[此页面](https://spl.solana.com/token-2022/extensions)了解更多.

**指令 3: 初始化铸造账户**

```py
r2 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
r2.account.append(pxsol.core.AccountMeta(mint_pubkey, 1))
r2.account.append(pxsol.core.AccountMeta(pxsol.program.SysvarRent.pubkey, 0))
r2.data = pxsol.program.Token.initialize_mint(decimals, self.pubkey, self.pubkey)
```

上述代码在创建出来的铸造账户里设置代币的小数精度, 铸造权限和冻结权限. 多数情况下, 将这些权限设置为发布者本人就可以了. 初始化完成后, 您才能开始铸币.

**指令 4: 初始化元数据**

```py
r3 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
r3.account.append(pxsol.core.AccountMeta(mint_pubkey, 1))
r3.account.append(pxsol.core.AccountMeta(self.pubkey, 0))
r3.account.append(pxsol.core.AccountMeta(mint_pubkey, 0))
r3.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
r3.data = pxsol.program.Token.metadata_initialize(name, symbol, uri)
```

上述代码将元数据(名称, 符号, 地址)直接写入铸造账户的元数据扩展字段中.
