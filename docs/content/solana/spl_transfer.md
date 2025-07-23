# Solana/SPL Token/转账

Solana 是区块链世界的代币流动超级引擎. 凭借其极低的交易确认时间以及几乎算是免费的交易手续费, 让代币转账变得如丝般顺滑.

## 转账

您可以使用 `spl_transfer()` 发送任意 spl token 给任意用户, 但记得考虑代币的小数位. 此函数会自动检测目标用户是否存在 ata 账户, 如果没有的会, 则会为其进行自动创建.

```py
import pxsol

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
bob = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(2))
spl = pxsol.core.PubKey.base58_decode('2CMXJX8arHRsiiZadVheRLTd6uhP7DpbaJ9hRiRMSGcF')

print(ada.spl_balance(spl)) # [100000000000000000, 9]
ada.spl_transfer(spl, bob.pubkey, 100 * 10 ** 9)
print(ada.spl_balance(spl)) # [99999900000000000, 9]
print(bob.spl_balance(spl)) # [100000000000, 9]
```

## 成为空投之王

在 solana 网络上, 您可能经常遇见有陌生人给您转账 spl token. 这种由陌生人或广泛用户分发代币的行为通常被称为"空投". 空投是项目方或个人免费向特定群体或不特定群体的钱包地址发送代币的行为, 这种行为在 solana, 以太坊等区块链生态中非常常见, 旨在推广项目或增加代币的流通性.

> 这种行为常见于 meme 币项目，一些散户会通过代币的持有者人数来判断代币的活跃性或潜力, 项目方通过空投可以短时间提升这个值.

例: 请向随机的 1000 个地址空投您的代币, 成为空投之王!

答:

```py
import pxsol
import random

pxsol.config.current.log = 1

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(1))
spl = pxsol.core.PubKey.base58_decode('2CMXJX8arHRsiiZadVheRLTd6uhP7DpbaJ9hRiRMSGcF')

for _ in range(1000):
    dst = pxsol.core.PriKey.random().pubkey()
    ada.spl_transfer(spl, dst, 100 * 10 ** 9)
```
