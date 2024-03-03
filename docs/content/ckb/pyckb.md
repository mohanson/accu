# CKB/Pyckb 简介

[Pyckb](https://github.com/mohanson/pyckb) 是一个用于与 CKB 区块链交互的 Python 工具库. 这个项目的目的是为了提供访问 CKB 区块链的能力, 以进行脚本部署, 交易创建, 数据查询等操作. Pyckb 具有我个人十分明显的代码编写风格, 具体而言, 它包含以下两点:

- 不盲目使用第三方依赖库. 事实上, 它没有使用第三方库.
- 较低层次的抽象, 几乎总是可以在 2 次代码跳转之内找到你感兴趣的地方.

因此, 它除了是一个工具外, 也是一个绝佳的学习 CKB 中各种概念的教程. 最初, 这个项目只是我编写的几个用以简化工作流程的脚本, 在投入了不少的业余时间后, 才慢慢变成了一个完整的 CKB 工具库.

## 安装

```sh
# 建议通过 pip 安装
$ python -m pip install pyckb

# 或者也可以使用本地安装方式
$ git clone https://github.com/mohanson/pyckb
$ cd pyckb
$ python -m pip install . --editable
```

## 生成测试账号

默认情况下, pyckb 配置为 CKB 测试网. 后文会介绍如何切换到主网. 我们创建一个新的钱包, 该钱包使用的私钥是 `1`. **注意: 请不要在主网这么做!**

```py
import ckb

user = ckb.wallet.Wallet(1)
print(user.addr)
```

返回地址 `ckt1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqt4z78ng4yutl5u6xsv27ht6q08mhujf8s2r0n40`.

## 领取测试代币

虽然有测试网[水龙头](https://faucet.nervos.org/), 但是该水龙头有 30 日 300K CKB 的限额, 有时候会显得有点不够用. 因此 pyckb 提供了一个小脚本来帮助开发者绕过限制, 无限制领取测试代币.

```sh
$ python example/faucet.py ckt1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqt4z78ng4yutl5u6xsv27ht6q08mhujf8s2r0n40
```

等待脚本执行结束, 打开[测试网浏览器](https://pudge.explorer.nervos.org/address/ckt1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqt4z78ng4yutl5u6xsv27ht6q08mhujf8s2r0n40)查询代币是否入账:

## 转账交易

我们创建一个新的账号 jack, 并向其转账 100 CKB. Hi, jack!

```py
import ckb

user = ckb.wallet.Wallet(1)
jack = ckb.wallet.Wallet(2)

hash = user.transfer(jack.script, 100 * ckb.core.shannon)
print(hash.hex())
```

## 发布脚本

```py
import ckb

user = ckb.wallet.Wallet(1)
hash = user.script_deploy_type_id(user.script, bytearray([0, 1, 2, 3]))
print(f'{hash.hex()}')
ckb.rpc.wait(f'0x{hash.hex()}')
```

## 更新脚本

将 `29af4422896ac3e647558ecedfe35df45ff2270d3f22e8029a4e0780a776cdf2` 替换为上一步骤的交易哈希, 可更新上个步骤部署的脚本:

```py
import ckb

user = ckb.wallet.Wallet(1)
out_point = ckb.core.OutPoint(bytearray.fromhex('29af4422896ac3e647558ecedfe35df45ff2270d3f22e8029a4e0780a776cdf2'), 0)
hash = user.script_update_type_id(user.script, bytearray([0, 1, 2, 3, 4, 5]), out_point)
print(f'{hash.hex()}')
ckb.rpc.wait(f'0x{hash.hex()}')
```

## DAO 操作

```py
import ckb

user = ckb.wallet.Wallet(1)

hash = user.dao_deposit(200 * ckb.core.shannon)
print(f'{hash.hex()}')
ckb.rpc.wait(f'0x{hash.hex()}')

hash = user.dao_prepare(ckb.core.OutPoint(hash, 0))
print(f'{hash.hex()}')
ckb.rpc.wait(f'0x{hash.hex()}')
```

## 如何切换到主网

在导入 `ckb` 后添加如下语句, 即可将环境切换到主网.

```py
import ckb

ckb.config.current = ckb.config.mainnet
```
