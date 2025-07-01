# Solana/SPL Token/指令详解(二)

在上一节课中, 我们学习了如何使用 `spl_create()` 创建一个带有元数据的 spl token. 在本节课, 我们将深入学习另一个至关重要的操作: `spl_mint()` 是如何将 token 铸造并分发给目标地址(或自己)的?

## 源码

> 为了避免读者不停切换页面, 我将待分析的代码复制在了这里.

```py
def spl_mint(self, mint: pxsol.core.PubKey, recv: pxsol.core.PubKey, amount: int) -> None:
    # Mint a specified number of tokens and distribute them to self. Note that amount refers to the smallest unit
    # of count, For example, when the decimals of token is 2, you should use 100 to represent 1 token. If the
    # token account does not exist, it will be created automatically.
    recv_ata_pubkey = Wallet.view_only(recv).spl_account(mint)
    r0 = pxsol.core.Requisition(pxsol.program.AssociatedTokenAccount.pubkey, [], bytearray())
    r0.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
    r0.account.append(pxsol.core.AccountMeta(recv_ata_pubkey, 1))
    r0.account.append(pxsol.core.AccountMeta(recv, 0))
    r0.account.append(pxsol.core.AccountMeta(mint, 0))
    r0.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
    r0.account.append(pxsol.core.AccountMeta(pxsol.program.Token.pubkey, 0))
    r0.data = pxsol.program.AssociatedTokenAccount.create_idempotent()
    r1 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
    r1.account.append(pxsol.core.AccountMeta(mint, 1))
    r1.account.append(pxsol.core.AccountMeta(recv_ata_pubkey, 1))
    r1.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
    r1.data = pxsol.program.Token.mint_to(amount)
    tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [r0, r1])
    tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
    tx.sign([self.prikey])
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    pxsol.rpc.wait([txid])
```

## 实现流程拆解

方法 `spl_mint()` 会组装一笔交易, 内含两条链上指令.

**指令 1: 创建关联代币账户**

```py
r0 = pxsol.core.Requisition(pxsol.program.AssociatedTokenAccount.pubkey, [], bytearray())
r0.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
r0.account.append(pxsol.core.AccountMeta(recv_account_pubkey, 1))
r0.account.append(pxsol.core.AccountMeta(recv, 0))
r0.account.append(pxsol.core.AccountMeta(mint, 0))
r0.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
r0.account.append(pxsol.core.AccountMeta(pxsol.program.Token.pubkey, 0))
r0.data = pxsol.program.AssociatedTokenAccount.create_idempotent()
```

上述代码为接收人自动创建与之相关联的关联代币账户. 使用 `create_idempotent()` 保证即使目标账户已经存在, 指令也不会报错导致交易失败, 这是 `AssociatedTokenAccount.create_idempotent()` 指令区别于 `AssociatedTokenAccount.create()` 最重要的一点. 您可以这样理解这条指令的逻辑:

- 如果目标关联代币账户已经存在, 则正常退出.
- 如果目标关联代币账户还未存在, 则创建账户, 并正常退出.

> 正如它的名字所描述的, create_idempotent() 是幂等的. 幂等性是数学和计算机学中的一个概念. 在计算机中, 幂等性是指: 用户对于同一个操作发起一次请求或者多次请求, 获得的结果都是一致的. 不会因为请求多次出现异常情况.

**指令 2: 铸造代币**

```py
r1 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
r1.account.append(pxsol.core.AccountMeta(mint, 1))
r1.account.append(pxsol.core.AccountMeta(recv_account_pubkey, 1))
r1.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
r1.data = pxsol.program.Token.mint_to(amount)
```

上述代码将一定数量的代币铸造到接收者账户. 铸造代币需要拥有铸造权限, 在 `pxsol.wallet.Wallet` 的设计里, 代币的铸造权限拥有者默认是代币发布者本人.

铸造代币将会增加代币的总供应量.
