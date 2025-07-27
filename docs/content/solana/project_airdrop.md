# Solana/在主网发行您的代币/获取空投

Pxs 空投合约的设计允许任意调用该合约的用户获取 5 pxs 的空投, 因此我们编写脚本如下. 该脚本的功能只是简单的调用一次空投合约.

```py
import argparse
import base64
import pxsol

# Apply for PXS airdrop on the mainnet.

pxsol.config.current = pxsol.config.mainnet
pxsol.config.current.log = 1

parser = argparse.ArgumentParser()
parser.add_argument('--prikey', type=str, help='private key')
args = parser.parse_args()

user = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(int(args.prikey, 0)))
pubkey_mint = pxsol.core.PubKey.base58_decode('6B1ztFd9wSm3J5zD5vmMNEKg2r85M41wZMUW7wXwvEPH')
pubkey_mana = pxsol.core.PubKey.base58_decode('HgatfFyGw2bLJeTy9HkVd4ESD6FkKu4TqMYgALsWZnE6')
pubkey_mana_seed = bytearray([])
pubkey_mana_auth = pubkey_mana.derive_pda(pubkey_mana_seed)
pubkey_mana_spla = pxsol.wallet.Wallet.view_only(pubkey_mana_auth).spl_account(pubkey_mint)
rq = pxsol.core.Requisition(pubkey_mana, [], bytearray())
rq.account.append(pxsol.core.AccountMeta(user.pubkey, 3))
rq.account.append(pxsol.core.AccountMeta(user.spl_account(pubkey_mint), 1))
rq.account.append(pxsol.core.AccountMeta(pubkey_mana, 0))
rq.account.append(pxsol.core.AccountMeta(pubkey_mana_auth, 0))
rq.account.append(pxsol.core.AccountMeta(pubkey_mana_spla, 1))
rq.account.append(pxsol.core.AccountMeta(pubkey_mint, 0))
rq.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
rq.account.append(pxsol.core.AccountMeta(pxsol.program.Token.pubkey, 0))
rq.account.append(pxsol.core.AccountMeta(pxsol.program.AssociatedTokenAccount.pubkey, 0))
rq.data = bytearray()
tx = pxsol.core.Transaction.requisition_decode(user.pubkey, [rq])
tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
tx.sign([user.prikey])
pxsol.log.debugln(f'main: request pxs airdrop')
txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
pxsol.rpc.wait([txid])
tlog = pxsol.rpc.get_transaction(txid, {})
for e in tlog['meta']['logMessages']:
    pxsol.log.debugln(e)
pxsol.log.debugln(f'main: request pxs airdrop done')
```

您可以在 pxsol 项目的源码中找到这份[脚本](https://github.com/mohanson/pxsol/blob/master/example/pxs_airdrop.py). 脚本已经默认配置到主网, 运行脚本后, 我们的空投合约就将发送 5 pxs 至您的账户!

```sh
$ git clone https://github.com/mohanson/pxsol
$ cd pxsol
$ python example/pxs_airdrop.py --prikey 0xYOUR_MAINNET_PRIVATE_KEY
```
