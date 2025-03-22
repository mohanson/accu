# Solana/交易/使用内置钱包进行转账

Pxsol 的内置钱包允许读者在 python 中直接管理 solana 账户, 通过私钥派生公钥(钱包地址), 从而执行如查看余额, 交易转账等操作.

## 创建您的私钥

要使用 pxsol 的内置钱包, 首先需要一个私钥对象. 有多种途径来初始化您的私钥. 以下是几种创建私钥的方式:

**从字节数组**

```py
import pxsol

prikey = pxsol.core.PriKey(bytearray([0x00] * 31 + [0x01]))
assert prikey.pubkey().base58() == '6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt'
```

**从 base58 字符串**

```py
import pxsol

prikey = pxsol.core.PriKey.base58_decode('11111111111111111111111111111112')
assert prikey.pubkey().base58() == '6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt'
```

**从 hex 字符串**

```py
import pxsol

prikey = pxsol.core.PriKey.hex_decode('0000000000000000000000000000000000000000000000000000000000000001')
assert prikey.pubkey().base58() == '6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt'
```

**从整数**

```py
import pxsol

prikey = pxsol.core.PriKey.int_decode(0x01)
assert prikey.pubkey().base58() == '6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt'
```

**从 keypair(base58)**

```py
import pxsol

prikey = pxsol.core.PriKey.wif_decode('1111111111111111111111111111111PPm2a2NNZH2EFJ5UkEjkH9Fcxn8cvjTmZDKQQisyLDmA')
assert prikey.pubkey().base58() == '6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt'
```

以上所有方法都是严格等价的.

## 使用内置钱包进行转账

Pxsol 的子模块 `pxsol.wallet` 实现了一个简单但是功能强大的内置钱包.

Ada 正在泰国享受他的假期. 他进入了一家海鲜餐厅, 美美的吃上了一顿. 在结账的时候, 他注意到这家餐厅允许顾客使用 solana 支付账单. Ada 决定试一试, 他现在需要向店主 bob 支付 1 sol. 为了实现这个过程, ada 首先用自己的私钥初始化了自己的钱包. 要完成这笔交易, ada 还需要完成两个步骤:

- 填写 bob 的 solana 公钥(地址).
- 要发送的金额, 以 lamport 表示.

```py
import pxsol

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))
bob = pxsol.core.PubKey.base58_decode('8pM1DN3RiT8vbom5u1sNryaNT1nyL8CTTW3b5PwWXRBH')
ada.sol_transfer(bob, 1 * pxsol.denomination.sol)
```

> 绝密信息: bob 的地址所对应的私钥为 0x02.

执行代码, ada 的交易就将发送到 solana 网络, 任何错误都将不可逆转. 因此, ada 仔细检查了地址和金额, 确保万无一失. Pxsol 的钱包会构建一笔交易, 从 ada 获取 1 sol 的资金并发送到 bob 的地址, 最后使用 ada 的私钥签署交易.

在完成交易之后, ada 检查了自己钱包的余额.

```py
import pxsol

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))
print(f'ada: {ada.sol_balance() / pxsol.denomination.sol} sol')
# ada: 499999998.999995 sol
```

细心的 ada 发现, 自己的余额减少的数字略微大于 1 sol, 这其间的差值是该交易所支付的手续费.

Solana 拥有无与伦比的交易确认速度: 通常在您发出交易的瞬间, 交易就会被确认. 因此 pxsol 的内置钱包采用了同步交易确认方式: 只有当交易被网络确认, `sol_transfer()` 方法才会返回.
