# Solana/泰铢币/程序交互

## 编译并部署程序

在之前的文章中, 我们已经展示过如何编译以及部署程序, 此处不再赘述, 仅**再次**给出相关步骤和代码如下.

使用下面的命令编译程序代码.

```sh
$ cargo build-sbf -- -Znext-lockfile-bump
```

使用下面的 python 代码部署目标程序上链.

```py
import pathlib
import pxsol

# Enable log
pxsol.config.current.log = 1

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))

program_data = pathlib.Path('target/deploy/pxsol_thaibaht.so').read_bytes()
program_pubkey = ada.program_deploy(bytearray(program_data))
print(program_pubkey) # 9SP6msRytNxeHXvW38xHxjsBHspqZERDTMh5Wi8xh16Q
```

此处泰铢币部署地址为 `9SP6msRytNxeHXvW38xHxjsBHspqZERDTMh5Wi8xh16Q`.

## 铸造代币

铸造新泰铢币的过程是通过一个 solana 交易来完成的. Ada 可以这样为自己铸造新的 100 个泰铢币. 您可能需要注意下 `data` 的构造, 它的长度为 9 个字节, 第一个字节为 0, 代表铸造操作.

另外要注意, 只有 ada 有权利铸造新的代币, 此权限已经在泰铢币的链上程序中被强制硬编码.

```py
import base64
import pxsol


def mint(user: pxsol.wallet.Wallet, amount: int) -> None:
    assert user.pubkey.base58() == '6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt' # Is ada?
    prog_pubkey = pxsol.core.PubKey.base58_decode('9SP6msRytNxeHXvW38xHxjsBHspqZERDTMh5Wi8xh16Q')
    data_pubkey = prog_pubkey.derive_pda(user.pubkey.p)
    rq = pxsol.core.Requisition(prog_pubkey, [], bytearray())
    rq.account.append(pxsol.core.AccountMeta(user.pubkey, 3))
    rq.account.append(pxsol.core.AccountMeta(data_pubkey, 1))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.SysvarRent.pubkey, 0))
    rq.data = bytearray([0x00]) + bytearray(amount.to_bytes(8))
    tx = pxsol.core.Transaction.requisition_decode(user.pubkey, [rq])
    tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
    tx.sign([user.prikey])
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    pxsol.rpc.wait([txid])
    r = pxsol.rpc.get_transaction(txid, {})
    for e in r['meta']['logMessages']:
        print(e)


if __name__ == '__main__':
    ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
    mint(ada, 100)
```

## 查询余额

使用 rpc 接口查询自己的数据账户中的数据, 并将其转换为 64 位无符号整数, 该数字即表示用户的泰铢币余额.

```py
import base64
import pxsol

def balance(user: pxsol.core.PubKey) -> int:
    prog_pubkey = pxsol.core.PubKey.base58_decode('9SP6msRytNxeHXvW38xHxjsBHspqZERDTMh5Wi8xh16Q')
    data_pubkey = prog_pubkey.derive_pda(user.p)
    info = pxsol.rpc.get_account_info(data_pubkey.base58(), {})
    return int.from_bytes(base64.b64decode(info['data'][0]))

if __name__ == '__main__':
    ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
    print(balance(ada.pubkey))
```

## 转账

Ada 向 bob 转账 50 泰铢币, 转账完成后, 查询双方的余额.

```py
import base64
import pxsol


def balance(user: pxsol.core.PubKey) -> int:
    prog_pubkey = pxsol.core.PubKey.base58_decode('9SP6msRytNxeHXvW38xHxjsBHspqZERDTMh5Wi8xh16Q')
    data_pubkey = prog_pubkey.derive_pda(user.p)
    info = pxsol.rpc.get_account_info(data_pubkey.base58(), {})
    return int.from_bytes(base64.b64decode(info['data'][0]))


def transfer(user: pxsol.wallet.Wallet, into: pxsol.core.PubKey, amount: int) -> None:
    prog_pubkey = pxsol.core.PubKey.base58_decode('9SP6msRytNxeHXvW38xHxjsBHspqZERDTMh5Wi8xh16Q')
    upda_pubkey = prog_pubkey.derive_pda(user.pubkey.p)
    into_pubkey = into
    ipda_pubkey = prog_pubkey.derive_pda(into_pubkey.p)
    rq = pxsol.core.Requisition(prog_pubkey, [], bytearray())
    rq.account.append(pxsol.core.AccountMeta(user.pubkey, 3))
    rq.account.append(pxsol.core.AccountMeta(upda_pubkey, 1))
    rq.account.append(pxsol.core.AccountMeta(into_pubkey, 0))
    rq.account.append(pxsol.core.AccountMeta(ipda_pubkey, 1))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.SysvarRent.pubkey, 0))
    rq.data = bytearray([0x01]) + bytearray(amount.to_bytes(8))
    tx = pxsol.core.Transaction.requisition_decode(user.pubkey, [rq])
    tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
    tx.sign([user.prikey])
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    pxsol.rpc.wait([txid])
    r = pxsol.rpc.get_transaction(txid, {})
    for e in r['meta']['logMessages']:
        print(e)


if __name__ == '__main__':
    ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
    bob = pxsol.core.PriKey.int_decode(2).pubkey()
    transfer(ada, bob, 50)
    print(balance(ada.pubkey))
    print(balance(bob))
```
