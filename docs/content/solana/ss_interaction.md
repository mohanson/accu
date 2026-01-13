# Solana/程序开发入门/程序交互

现在, 我们的链上数据存储器已经被部署在 `DVapU9kvtjzFdH3sRd3VDCXjZVkwBR6Cxosx36A5sK5E` 地址上. 我们尝试写入自己的数据到程序里.

## 写入数据到账户

写数据的过程是通过一个 solana 交易来完成的. 您可以这样写入数据:

```py
import base64
import pxsol

pxsol.config.current.log = 1

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))


def save(user: pxsol.wallet.Wallet, data: bytearray) -> None:
    prog_pubkey = pxsol.core.PubKey.base58_decode('DVapU9kvtjzFdH3sRd3VDCXjZVkwBR6Cxosx36A5sK5E')
    data_pubkey = prog_pubkey.derive_pda(user.pubkey.p)[0]
    rq = pxsol.core.Requisition(prog_pubkey, [], bytearray())
    rq.account.append(pxsol.core.AccountMeta(user.pubkey, 3))
    rq.account.append(pxsol.core.AccountMeta(data_pubkey, 1))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.SysvarRent.pubkey, 0))
    rq.data = data
    tx = pxsol.core.Transaction.requisition_decode(user.pubkey, [rq])
    tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
    tx.sign([user.prikey])
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    pxsol.rpc.wait([txid])
    r = pxsol.rpc.get_transaction(txid, {})
    for e in r['meta']['logMessages']:
        print(e)

if __name__ == '__main__':
    save(ada, b'The quick brown fox jumps over the lazy dog')
```

```py
# 2025/05/27 10:17:23 pxsol: transaction send signature=oCF2esfLeM7iu8MsR5wgBPatVXGt9Dq7TSzLpwWuMjooeDBeHMtSc8ukuqmPcaMrzzHcdiLg7cPbPzsHi2vdv8j
# 2025/05/27 10:17:23 pxsol: transaction wait unconfirmed=1
# 2025/05/27 10:17:23 pxsol: transaction wait unconfirmed=0
# Program DVapU9kvtjzFdH3sRd3VDCXjZVkwBR6Cxosx36A5sK5E invoke [1]
# Program DVapU9kvtjzFdH3sRd3VDCXjZVkwBR6Cxosx36A5sK5E consumed 2903 of 200000 compute units
# Program DVapU9kvtjzFdH3sRd3VDCXjZVkwBR6Cxosx36A5sK5E success
```

## 读取链上的数据

读取数据就是查询自己的 pda 数据账户中存储数据的过程. 这个过程不需要构造交易, 只需要借助 rpc 接口查询即可.

```py
import base64
import pxsol

pxsol.config.current.log = 1

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))


def load(user: pxsol.wallet.Wallet) -> bytearray:
    prog_pubkey = pxsol.core.PubKey.base58_decode('DVapU9kvtjzFdH3sRd3VDCXjZVkwBR6Cxosx36A5sK5E')
    data_pubkey = prog_pubkey.derive_pda(user.pubkey.p)[0]
    info = pxsol.rpc.get_account_info(data_pubkey.base58(), {})
    return base64.b64decode(info['data'][0])


if __name__ == '__main__':
    print(load(ada).decode()) # The quick brown fox jumps over the lazy dog
```

## 更新链上的数据

我们只需要重新调用一次 `save()` 并写入不同的数据, 就能覆盖链上已有的数据, 程序会为我们自动实现新的租赁豁免. 完整代码如下.

```py
import base64
import pxsol

pxsol.config.current.log = 1

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))


def save(user: pxsol.wallet.Wallet, data: bytearray) -> None:
    prog_pubkey = pxsol.core.PubKey.base58_decode('DVapU9kvtjzFdH3sRd3VDCXjZVkwBR6Cxosx36A5sK5E')
    data_pubkey = prog_pubkey.derive_pda(user.pubkey.p)[0]
    rq = pxsol.core.Requisition(prog_pubkey, [], bytearray())
    rq.account.append(pxsol.core.AccountMeta(user.pubkey, 3))
    rq.account.append(pxsol.core.AccountMeta(data_pubkey, 1))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.SysvarRent.pubkey, 0))
    rq.data = data
    tx = pxsol.core.Transaction.requisition_decode(user.pubkey, [rq])
    tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
    tx.sign([user.prikey])
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    pxsol.rpc.wait([txid])
    r = pxsol.rpc.get_transaction(txid, {})
    for e in r['meta']['logMessages']:
        print(e)


def load(user: pxsol.wallet.Wallet) -> bytearray:
    prog_pubkey = pxsol.core.PubKey.base58_decode('DVapU9kvtjzFdH3sRd3VDCXjZVkwBR6Cxosx36A5sK5E')
    data_pubkey = prog_pubkey.derive_pda(user.pubkey.p)[0]
    info = pxsol.rpc.get_account_info(data_pubkey.base58(), {})
    return base64.b64decode(info['data'][0])


if __name__ == '__main__':
    save(ada, b'The quick brown fox jumps over the lazy dog')
    print(load(ada).decode()) # The quick brown fox jumps over the lazy dog
    save(ada, '片云天共远, 永夜月同孤.'.encode())
    print(load(ada).decode()) # 片云天共远, 永夜月同孤.
```
