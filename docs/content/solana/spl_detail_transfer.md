# Solana/SPL Token/指令详解(三)

本小节带你深入理解 spl 转账操作背后的链上逻辑, 帮助你掌握在 solana 上安全自动地转移 spl token 的正确方式. 方法  `spl_transfer()` 主要完成以下两件事:

- 确保接收者的关联代币账户存在. 如果没有，自动创建.
- 从当前钱包的关联代币账户转账指定数量的代币到接收者账户.

## 源码

> 为了避免读者不停切换页面, 我将待分析的代码复制在了这里.

```py
def spl_transfer(self, mint: pxsol.core.PubKey, recv: pxsol.core.PubKey, amount: int) -> None:
    # Transfers tokens to the target. Note that amount refers to the smallest unit of count, For example, when the
    # decimals of token is 2, you should use 100 to represent 1 token. If the token account does not exist, it will
    # be created automatically.
    self_ata_pubkey = self.spl_account(mint)
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
    r1.account.append(pxsol.core.AccountMeta(self_ata_pubkey, 1))
    r1.account.append(pxsol.core.AccountMeta(recv_ata_pubkey, 1))
    r1.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
    r1.data = pxsol.program.Token.transfer(amount)
    tx = pxsol.core.Transaction.requisition_decode(self.pubkey, [r0, r1])
    tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
    tx.sign([self.prikey])
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    pxsol.rpc.wait([txid])
```

## 实现流程拆解

方法 `spl_transfer()` 会组装并发送一笔包含两条链上指令的交易.

**指令 1：创建关联代币账户**

```py
r0 = pxsol.core.Requisition(pxsol.program.AssociatedTokenAccount.pubkey, [], bytearray())
r0.account.append(pxsol.core.AccountMeta(self.pubkey, 3))
r0.account.append(pxsol.core.AccountMeta(recv_ata_pubkey, 1))
r0.account.append(pxsol.core.AccountMeta(recv, 0))
r0.account.append(pxsol.core.AccountMeta(mint, 0))
r0.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
r0.account.append(pxsol.core.AccountMeta(pxsol.program.Token.pubkey, 0))
r0.data = pxsol.program.AssociatedTokenAccount.create_idempotent()
```

上述代码与 `spl_mint()` 的第一条指令功能以及作用相同.

**指令 2：转账**

```py
r1 = pxsol.core.Requisition(pxsol.program.Token.pubkey, [], bytearray())
r1.account.append(pxsol.core.AccountMeta(self_ata_pubkey, 1))
r1.account.append(pxsol.core.AccountMeta(recv_ata_pubkey, 1))
r1.account.append(pxsol.core.AccountMeta(self.pubkey, 2))
r1.data = pxsol.program.Token.transfer(amount)
```

上述代码将一定数量的代币从当前账户转移到接收者账户. 转账操作最终会由 token-2022 程序验证并计入双方余额变化.
