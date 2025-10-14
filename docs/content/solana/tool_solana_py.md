# Solana/更多开发者工具/solana-py 和 solders 库的结合使用

工具 solana-py 是一个 solana 的 python 库, 用于与 solana 区块链进行交互. 它提供了与 solana 节点通信的 api, 适合开发者快速构建与 solana 网络交互的应用程序. 该库底层依赖 solders 库, solders 是一个更底层的 rust 语言编写的 solana 库, 提供了对 solana 协议和数据结构的直接访问.

您可以这么理解:

- solders: 提供了对 solana 协议和数据结构的直接访问
- solana-py: 构建在 solders 之上, 提供了更高层次的 api, 适合快速开发和与 solana 网络交互的应用

下面的示例代码展示了如何使用 solana-py 和 solders 库来获取我们的简单链上数据合约的所有交易历史记录, 并打印出该程序所拥有的所有账户的数据.

```py
"""
Fetch all transaction history for a Solana program and print stored data for each account owned by the program.

Network: mainnet-beta
Program: 9RctzLPHP58wrnoGCbb5FpFKbmQb6f53i5PsebQZSaQL

This script uses the JSON-RPC getSignaturesForAddress pagination to walk the full history of the program (within node's
retention), then fetches program-owned accounts and prints their data.
"""
import datetime
import itertools
import os
import solana.rpc.api
import solders
import solders.rpc.responses
import typing

DEFAULT_PROGRAM_ID = '9RctzLPHP58wrnoGCbb5FpFKbmQb6f53i5PsebQZSaQL'
DEFAULT_RPC = os.environ.get('SOLANA_RPC', 'https://api.mainnet-beta.solana.com')


def get_all_program_sigs(
    client: solana.rpc.api.Client,
    program: solders.pubkey.Pubkey,
) -> typing.Generator[solders.rpc.responses.RpcConfirmedTransactionStatusWithSignature, None, None]:
    cursor = None
    limits = 256
    for _ in itertools.repeat(0):
        resp = client.get_signatures_for_address(program, before=cursor, limit=limits)
        sigs = resp.value
        if not sigs:
            break
        for s in sigs:
            yield s
        cursor = sigs[-1].signature


def get_all_program_pdas(
    client: solana.rpc.api.Client,
    program: solders.pubkey.Pubkey,
) -> typing.List[solders.rpc.responses.RpcKeyedAccount]:
    resp = client.get_program_accounts(program, encoding='base64')
    pdas = resp.value
    return pdas


def main():
    program_key = solders.pubkey.Pubkey.from_string(DEFAULT_PROGRAM_ID)
    client = solana.rpc.api.Client(DEFAULT_RPC)
    print('main: get_all_program_sigs')
    for e in get_all_program_sigs(client, program_key):
        print(f'main: datetime={datetime.datetime.fromtimestamp(e.block_time)}, sig={e.signature}')
    print('main: get_all_program_pdas')
    for e in get_all_program_pdas(client, program_key):
        print('main:    owner:', e.account.owner)
        print('main:      pda:', e.pubkey)
        print('main: lamports:', e.account.lamports)
        print('main:     data:',  e.account.data.decode())
        print()


if __name__ == '__main__':
    main()
```

运行后的结果如下, 它成功获取到了作者存储在链上的数据:

```txt
main: get_all_program_sigs
main: datetime=2025-10-13 14:42:45, sig=4k2rTsRW2s1GKxsaDmDx2sM9rRVTzGS7LgVnTphAPNQ4ZDpbhLeLLSrVLeRQLxBEpfWsTGFoAn3uuJDzr6eQ7y9X
main: datetime=2025-10-13 14:40:22, sig=5WduQv7NGXpnHUYWwrjhyzWtHHP6BRj2os4iuj8JpYCHGMeiT2wRzGzgm2yF5PdKcAuux7LhXkDe1B79oFj2q8fb
main: datetime=2025-10-13 14:33:51, sig=EPJQwvr3WpVHZ6Jdr4DWrx5sKVScb7yrz2YRfGHyPqTpjNL4WnmvoquA9HATsPCQrzpSsyPx5WUUQt7Ger6JLY2
main: datetime=2025-10-13 11:31:49, sig=3wXnUFazxCz5zbvMcptVXKNyjuP45zbuc5UzmpxwKzK8VaQzTsuwoMdXhJTBaowhJ5LWuVwuFghUDvG7pu7Ty7CG
main: get_all_program_pdas
main:    owner: 9RctzLPHP58wrnoGCbb5FpFKbmQb6f53i5PsebQZSaQL
main:      pda: Ep838PrgsVLKgCwab15hNkBB1EaFFBKKx6pNiE1bGD5G
main: lamports: 1120560
main:     data: 片云天共远, 永夜月同孤.
```

这个示例的原理只是使用 `get_signatures_for_address` 和 `get_all_program_sigs` 这两个 rpc 接口, 结合 solders 库来解析数据, 以便打印出我们存储在链上的数据. 通过这种方式, 我们可以很方便地查看任何 solana 程序的交易历史和账户数据.
