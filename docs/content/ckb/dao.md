# CKB/DAO

## Nervos DAO 是什么

Nervos DAO 是 CKB 经济模型的重要亮点之一, 被用于对抗二级发行造成的稀释. 如果您将 CKB 存入 Nervos DAO, 那么对您来说 CKB 将是存在硬顶, 且持续通缩的.

Nervos DAO 是一个智能合约, 就像 CKB 上其他的智能合约一样, 用户可以与之交互. Nervos DAO 的功能之一就是为 CKByte 持币者提供一种抗稀释的功能. 通过将 CKByte 存入 Nervos DAO 中, 持有者可以获得一定比例的二级发行, 在存款和取款之间的这段时间内, 他们的持有比例只会受到创世块和基础发行的影响, 就像和有硬顶的比特币一样.

持有者可以随时将他们的 CKByte 存入 Nervos DAO 中. Nervos DAO 是一种定期存款, 存在一个最短存款期限(会按照区块计算), 持有者只能在一个完整的存款期之后进行取款. 如果持有者在存款期结束时没有取款, 这些 CKByte 将自动进入新的存款周期, 这样可以尽量减少持币人的操作次数.

## Nervos DAO 的收益

你可以直接前往 Nervos 区块浏览器中的 Nervos DAO [页面](https://explorer.nervos.org/nervosdao) , 在上方的数据表格中, 查看当前 Nervos DAO 的收益率, 即其中的预计 APC.

## Nervos DAO 的存取

首先, Nervos DAO 完整的存取一共有三个步骤, 包括 1 次存入, 2 次取出.

1 次存入很好理解, 和将钱存入银行一样, 用户可以直接将 CKB 存入 Nervos DAO.

2 次取出可以这样理解, 第 1 次取出, 就好比您和银行提出了一份申请, 表明您需要将存入的金额取出来. 经过银行核对, 在您的取出条件满足规定后(在 Nervos DAO 这边就是, 从存入的区块高度开始计算, 180 个 epoch 的整数倍后您可以取出), 您就可以发起第 2 次提取, 最终将 CKB 提取到您的钱包内.

理解上, 存入 Nervos DAO 就是存了一个为期 30 天的定期, 到期之后会自动再为您存一个 30 天的定期. 您只有在定期时间到了之后, 才能真正取出存入的 CKB.

目前已经可以使用 CKB-CLI 来操作 Nervos DAO, 比起使用 Neuron 钱包要方便很多了. 下面使用 CKB-CLI 来演示这三个步骤. 我们将使用前文创建的账号 A, 也就是私钥为 0x1 的账户. 不过这次我们将在测试网运行而非本地开发网.


```sh
addr="ckt1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqt4z78ng4yutl5u6xsv27ht6q08mhujf8s2r0n40"
args="0x75178f34549c5fe9cd1a0c57aebd01e7ddf9249e"

# 存入 1000 CKB 到 Nervos DAO
# https://pudge.explorer.nervos.org/transaction/0x3f155b6ab7882a4c0963534c61385d59af15786250c70a941e55260446dadf3f
$ ckb-cli --url https://testnet.ckb.dev dao deposit --from-account ${args} --capacity 1000

# 查询持有的 Nervos DAO 存款
$ ckb-cli --url https://testnet.ckb.dev dao query-deposited-cells --address ${addr}

# 发起 Nervos DAO 提取请求, --out-point 为上一步查询得到的 cell 位置
# https://pudge.explorer.nervos.org/transaction/0x6bb2911bf7076c91cbd817089be02ad49bcbcd4dc0d58df4883f6883f4a0351b
$ ckb-cli --url https://testnet.ckb.dev dao prepare --from-account ${args}
          --out-point 0x3f155b6ab7882a4c0963534c61385d59af15786250c70a941e55260446dadf3f-0

# 查询 Nervow DAO 提取请求
$ ckb-cli --url https://testnet.ckb.dev dao query-prepared-cells --address ${addr}

# 完成 Nervos DAO 提取请求, --out-point 为上一步查询得到的 cell 位置
$ ckb-cli --url https://testnet.ckb.dev dao withdraw --from-account ${args}
          --out-point 0x6bb2911bf7076c91cbd817089be02ad49bcbcd4dc0d58df4883f6883f4a0351b-0
```
