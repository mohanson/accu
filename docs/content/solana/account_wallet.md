# Solana/账户模型/普通钱包账户

在 solana 网络上, 使用最广泛的账户类型就是普通钱包账户. 这些账户通常由钱包应用生成, 帮助用户存放和管理 sol. [此页面](https://solana.com/solana-wallets)列举出了常见的 solana 钱包, 您可以根据您的喜好任意选择您喜欢且信任的钱包应用.

不过我依然有一些建议, 也许可以帮助在区块链世界冲浪的您:

0. 始终在官网下载钱包应用, 并且不要相信搜索引擎. 依记得在 2022 年左右, 网络上开始出现大量钓鱼网站, 引导用户下载被黑客修改过的钱包应用. 这些钓鱼网站甚至购买了搜索引擎的排名, 使得用户搜索钱包名称时, 钓鱼网站搜索结果可以排序在官网之上.
0. 选择拥有良好声誉的开发团队的钱包应用. 开发团队不应当有黑历史, 或者来路不明.
0. 选择拥有更多用户数量的钱包应用.

## 创建普通钱包账户

创建这样一个账户其实很简单, 唯一需要做的事情就是生成一个私钥. 通过私钥派生出的公钥就是您钱包的地址, 别人可以用它给您转钱; 私钥则是您控制钱包的密码, 只有您知道它, 别人不能随便用. 通过 pxsol, 使用私钥 0x02 生成一个新的账户如下.

```py
import pxsol

bob = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x02))
ret = pxsol.rpc.get_account_info(bob.pubkey.base58(), {})
print(ret) # None
```

新创建的钱包账户此时并未被 solana 网络记录, 因此当上述代码尝试使用 [get_account_info](https://solana.com/zh/docs/rpc/http/getaccountinfo) 查询账户信息时, 返回的结果是 `None`.

向这个账户转账 sol 可以"激活"这个账户.

```py
import pxsol

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))
bob = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x02))

# Transfer 1 sol from ada to bob.
ada.sol_transfer(bob.pubkey, 1 * pxsol.denomination.sol)

ret = pxsol.rpc.get_account_info(bob.pubkey.base58(), {})
print(ret)
# {
#     "data": ["", "base64"],
#     "executable": false,
#     "lamports": 1000000000,
#     "owner": "11111111111111111111111111111111",
#     "rentEpoch": 18446744073709551615,
#     "space": 0,
# }
```

您可以看到, 此时 bob 的账户信息已经被记录到了 solana 网络上. 账户的所有者是 `1111111...`, 也就是 solana 系统程序.

## 销毁普通钱包账户

如果您不再需要某个钱包账户了, 或者想要清理账户, 您可以销毁它. 销毁钱包账户其实并不复杂. 假如我们想要销毁上面创造的 bob 账户, 只需要把账户里的 sol 全部转移到另一个账户里. 没有余额的账户将立即被销毁.

转账的命令是这样的:

```py
import pxsol

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))
bob = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x02))

# Transfer all lamports from bob to ada.
bob.sol_transfer(ada.pubkey, bob.sol_balance() - 5000)

ret = pxsol.rpc.get_account_info(bob.pubkey.base58(), {})
print(ret)
# None
```

Bob 在构造交易时, 必须预留 5000 lamport 手续费, 然后将剩余 sol 全部转账给 ada. 待转账完成后, bob 账户将被立即销毁, 您将无法在 solana 网络上查询到 bob 账户的信息.

您可以轻松地创建和销毁 solana 上的普通钱包账户. 通常来说, 创建钱包账户是很常见的操作, 而销毁账户则多发生在您不再使用某个账户时, 或者您想清理一下自己的账户列表.
