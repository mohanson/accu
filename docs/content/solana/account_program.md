# Solana/账户模型/程序账户

Solana 上的程序账户就是一个部署了 solana 程序(智能合约)的账户. 程序部署完成后, 它就拥有一个"程序账户地址", 其他人可以通过这个地址来调用它. Solana 上的程序通常是用 rust 写的, 需要先编译成 bpf 字节码格式. 在之后的章节中我们将详细讨论 solana 上的智能合约, 现在先让我们专注于存储程序的容器, 也就是程序账户.

## 部署程序

作为一名老练的开发者, 我们已经在职业生涯中编写并运行过大量的 hello world 代码. 今天也不例外, 我们会尝试在 solana 网络上部署并运行一段简单的代码. 恰巧, pxsol 的资源目录中保存了一份 [hello world 代码](https://github.com/mohanson/pxsol/blob/master/res/hello_solana_program.so), 您可以通过以下命令下载它:

```sh
$ wget https://raw.githubusercontent.com/mohanson/pxsol/refs/heads/master/res/hello_solana_program.so
```

这个 `hello_solana_program.so` 文件, 这就是您的程序代码, 它将被上传到 solana 链上.

```py
import pathlib
import pxsol

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))

program_data = pathlib.Path('hello_solana_program.so').read_bytes()
program_pubkey = ada.program_deploy(bytearray(program_data))
print(program_pubkey) # 3EwjHuke6N6CfWPQdbRayrMUANyEkbondw96n5HJpYja
print(pxsol.rpc.get_account_info(program_pubkey.base58(), {}))
# {
#     "data": [
#         "AgAAAKqeeWx5rwCATKoazfymul8X00alxPltuX+elp+32dxO",
#         "base64"
#     ],
#     "executable": true,
#     "lamports": 1141440,
#     "owner": "BPFLoaderUpgradeab1e11111111111111111111111",
#     "rentEpoch": 18446744073709551615,
#     "space": 36
# }
```

我们在代码中, 简单的使用 `program_deploy()` 即可将程序部署到 solana 网络上. 在上述例子里, 程序被部署在了地址为 `3EwjHuke6N6CfWPQdbRayrMUANyEkbondw96n5HJpYja` 的程序账户里.

## 程序账户的权限和状态

部署后的程序账户由 [bpf upgradeable loader](https://docs.anza.xyz/runtime/programs#bpf-loader) 拥有, 这个 loader 控制是否可以升级程序.

账户信息里的 `executable` 被标记为 true, 表示它是一个程序账户, 可以执行代码.

Solana 包含少量原生程序, 这些程序是运行验证器节点所必需的. 与第三方程序不同, 原生程序是 solana 网络的一部分. 我们之前提到的用于 sol 转账的 solana 系统程序, 以及 bpf upgradeable loader 都是 solana 原生程序.

## 调用程序

Solana 里的程序就像是个链上工具人, 只要您发出合法的指令, 它就能帮你完成一些预设的基础活!

每次您要调用链上程序, 就要给它发送一个交易, 交易中包含一个指令, 指令的目标程序是它, 然后告诉它您想干嘛.

在我们的 `hello_solana_program.so` 程序里, 这个程序会向任何调用自己的用户发送一条"你好"的消息. 让我们试试调用它!

```py
import base64
import pxsol

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))

rq = pxsol.core.Requisition(pxsol.core.PubKey.base58_decode('3EwjHuke6N6CfWPQdbRayrMUANyEkbondw96n5HJpYja'), [], bytearray())
tx = pxsol.core.Transaction.requisition_decode(ada.pubkey, [rq])
tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
tx.sign([ada.prikey])
txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
pxsol.rpc.wait([txid])
r = pxsol.rpc.get_transaction(txid, {})
for e in r['meta']['logMessages']:
    print(e)

# Program 3EwjHuke6N6CfWPQdbRayrMUANyEkbondw96n5HJpYja invoke [1]
# Program log: Hello, Solana!
# Program log: Our program's Program ID: 3EwjHuke6N6CfWPQdbRayrMUANyEkbondw96n5HJpYja
# Program 3EwjHuke6N6CfWPQdbRayrMUANyEkbondw96n5HJpYja consumed 11759 of 200000 compute units
# Program 3EwjHuke6N6CfWPQdbRayrMUANyEkbondw96n5HJpYja success
```

在第二行输出, 我们收到了来自程序发出的 `Hello, Solana!` 消息.

Hello, Solana!
