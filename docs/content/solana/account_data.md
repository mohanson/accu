# Solana/账户模型/数据账户

在 solana 网络上, 程序的可执行代码与程序状态被存储在不同的账户中. 这类似于操作系统通常将程序和其数据分开存储在不同的文件中.

一个带状态的程序如果要在链上"安家落户", 它得找个地方放自己的变量, 状态或配置数据.

不过, 在 solana 上, 程序本身不能自己创建数据账户, 它只能让调用者, 也就是发交易的人, 在执行时预先签名并通过程序指令来由系统程序代创建, 并将数据账户的所有者设定为您的自定义程序, 这样您的自定义程序就能在数据账户的 data 里写入, 修改或者删除数据.

## 如何手动创建数据账户

如果您准备创建一个数据账户, 您首先需要明确以下三件事情.

- 数据账户的所有者程序是谁?
- 数据账户的空间是多少? 也就是您预期数据账户里会被写入多少数据?
- 数据账户的初始余额是多少?

创建账户需要使用 solana 系统程序的 create_account 指令. 我们举一个简单的例子, 对此进行演示.

例: 创建一个新的随机账户, 要求:

- 所有者程序指定为系统程序, 即 `11111111111111111111111111111111`.
- 数据账户的空间为 64 字节.
- 数据账户的初始余额为 1 sol.

答: 代码如下:

```py
import base64
import json
import pxsol
import random

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))
tmp = pxsol.wallet.Wallet(pxsol.core.PriKey.random())

rq = pxsol.core.Requisition(pxsol.program.System.pubkey, [], bytearray())
rq.account.append(pxsol.core.AccountMeta(ada.pubkey, 3)) # Funding account
rq.account.append(pxsol.core.AccountMeta(tmp.pubkey, 3)) # The new account
rq.data = pxsol.program.System.create_account(
    pxsol.denomination.sol, # Initial lamports
    64, # Data size for the new account
    pxsol.program.System.pubkey # Owner
)

tx = pxsol.core.Transaction.requisition_decode(ada.pubkey, [rq])
tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
tx.sign([ada.prikey, tmp.prikey])
txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
pxsol.rpc.wait([txid]) # Waiting for the transaction to be processed

r = pxsol.rpc.get_account_info(tmp.pubkey.base58(), {})
print(json.dumps(r, indent=4))
# {
#     "data": [
#         "AAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA==",
#         "base64"
#     ],
#     "executable": false,
#     "lamports": 1000000000,
#     "owner": "11111111111111111111111111111111",
#     "rentEpoch": 18446744073709551615,
#     "space": 64
# }
```

## Ada 和"泰铢币"的烦恼

Ada 的假期非常愉快, 但她也有一点小烦恼.

她虽然可以使用 sol 来支付她的餐费与娱乐费用, 但由于在现实世界中, 几乎所有商品都是以法币定价的, 因此每当她要付费时, 都需要查询 sol 当前的市价, 以决定应当转账多少 sol 给商家.

为此, 她准备在 solana 上写一个叫"泰铢币"的程序, 它不是真的代币, 但程序里能记录谁拥有多少"泰铢币".

她写好了程序, 并部署了它. 接着, 她用自己的钱包创建了一个数据账户, 专门用来存储自己的泰铢币余额. 比如她创建了一个账户地址: `ThbAdaBalance111...`, 这个账户归她的程序控制, owner 是她的程序地址, data 里记录着她的余额, 比如 1000 泰铢币.

Ada 向朋友 bob 推荐了这个程序并邀请他参与测试. 朋友 bob 也创建好了自己的数据账户, 接着, 他想给 ada 转 100 泰铢币. 他找到了 ada 的钱包地址, 开心地打开程序, 准备发钱……

但是他懵了:

"等等, ada 存储泰铢币的账户地址是啥? 不是她的钱包地址吗?"

麻烦来了, solana 的数据账户是可以随便创建的, 跟钱包地址无关! Ada 可能用任意地址当做自己泰铢币的数据账户地址, 只要她预先创建好, 让程序控制就行了.

这下 bob 可郁闷了, 每次给人转账之前还得"问一嘴你那个...那个数据账户地址是多少?"

Ada 心想: 如果可以从我的普通钱包账户确定性的派生出泰铢币的数据账户地址就好了!

## 程序派生地址

为了解决这个问题, solana 引入了一种特殊地址叫 pda(program derived address), 也就是程序派生地址. 它是从程序公钥和自定义的种子(通常是用户的普通钱包地址)推导出来的地址, 而且这个地址是唯一且可预测的.

也就是说, 在上面的例子里, 只要 bob 知道泰铢币的程序地址和 ada 的普通钱包地址, bob 就能算出 ada 的泰铢币数据账户地址, 而不需要 ada 告诉他.

所以, ada 把系统升级了一下, 以后每个用户的泰铢币余额都必须保存在 pda 上.

例: 假设 ada 的泰铢币程序地址是 `F782pXBcfvHvb8eJfrDtyD7MBtQDfsrihSRjvzwuVoJU`, 那么 ada 关于这个程序的 pda 地址是多少?

答: 在 pxsol 中, 我们可以通过 `derive_pda()` 函数来计算一个程序对于特定账户的 pda 地址.

```py
import pxsol

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))
thb = pxsol.core.PubKey.base58_decode('F782pXBcfvHvb8eJfrDtyD7MBtQDfsrihSRjvzwuVoJU')
pda = thb.derive_pda(ada.pubkey.p)[0]
print(pda) # HCPe787nPq7TfjeFivP9ZvZwejTAq1PGGzch93qUYeC3
```

## 小结

数据账户是程序用来存储自身状态数据的地方. 理论上, 任何账户都能作为数据账户. 不过, solana 上的开发者通常更习惯使用 pda 来确定性的生成数据账户.

您知道吗? 在上一小节中我们部署的 `hello_solana_program.so` 程序的 bpf 字节码, 实际上也位于一个 pda 账户内, 您可以使用下面的代码进行验证:

```py
import pxsol

program = pxsol.core.PubKey.base58_decode('3EwjHuke6N6CfWPQdbRayrMUANyEkbondw96n5HJpYja')
program_data = pxsol.core.PubKey.hex_decode('aa9e796c79af00804caa1acdfca6ba5f17d346a5c4f96db97f9e969fb7d9dc4e')
assert pxsol.program.LoaderUpgradeable.pubkey.derive_pda(program.p)[0] == program_data
```

有了 pda, 链上生活真是舒服多了!
