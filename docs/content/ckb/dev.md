# CKB/开发网络

当您试图使用脚本来开发一个 CKB 应用时, 您可能想要在部署之前在本地查看它是如何工作的.

这和在本地运行一个本地网页服务器相似. 为了测试您的去中心化应用程序, 您可以使用开发网络创建一个本地的区块链. 这些 CKB 开发网络提供了能够比公共测试网更快的迭代功能(例如您不需要从测试网获取 CKB).

## 前置要求

CKB 开发网络与主网/测试网共用一个客户端. 要配置本地开发网络, 您可下载公开的 CKB 发布版:

<https://github.com/nervosnetwork/ckb/releases/tag/v0.108.1>

解压压缩包得到目录如下.

```text
.
├── CHANGELOG.md
├── ckb
├── ckb-cli
├── COPYING
├── docs
│   ├── configure.md
│   ├── hashes.toml
│   ├── integrity-check.md
│   ├── platform-support.md
│   ├── quick-start.md
│   └── rpc.md
├── init
│   ├── linux-systemd
│   │   ├── ckb-miner.service
│   │   ├── ckb.service
│   │   └── README.md
│   └── README.md
└── README.md
```

## 创建网络

在启动网络之前, 我们首先生成两个测试账号.

```sh
# 清空本地已有的账号(谨慎使用)
$ rm -f ~/.ckb-cli/keystore/*

# 账号 A
$ echo 0000000000000000000000000000000000000000000000000000000000000001 > /tmp/foo
$ ckb-cli account import --privkey-path /tmp/foo

# 账号 B
$ echo 0000000000000000000000000000000000000000000000000000000000000002 > /tmp/foo
$ ckb-cli account import --privkey-path /tmp/foo

# 查询新创建的账号信息, 此处只摘出两个账号的 lock_arg
$ ckb-cli account list
# - "#": 0
#   lock_arg: 0x75178f34549c5fe9cd1a0c57aebd01e7ddf9249e
# - "#": 1
#   lock_arg: 0xa3c778981c19e1dcc611fb2132dcdaac075a5064
```

之后就可以启动本地节点. 事先生成账号的原因是我们需要一个账号来接收挖矿奖励.

```sh
# 清理可能存在的节点数据
$ rm -rf data specs ckb-miner.toml ckb.toml default.db-options

# 初始化节点信息, 设置挖矿奖励接收方为账号 A
$ ckb init --chain dev --ba-arg 0x75178f34549c5fe9cd1a0c57aebd01e7ddf9249e --ba-message 0xabcd

# 打开上一步生成的 ckb.toml, 在 rpc.modules 一栏增加 Indexer
# 如果不执行这一步, 我们无法方便的获取一个账号的余额
modules = [..., "Indexer"]

# 启动节点
$ ckb run
# 开始挖矿
$ ckb miner
```

## 查询余额

希望一切顺利! 您会看到节点开始出块, 但此时如果您急着查询账号 A 的余额, 可能会发现其余额为 0. 这并非错误. 我们先来看主网上的两个区块, 区块高度 [#88888](https://explorer.nervos.org/block/0xa20ab19345a93d66da18b43505857b457af165832c5321ba9a096760305c21b6) 和区块高度 [#88877](https://explorer.nervos.org/block/0xd8760a6419d113f595fd6073f06340e6c6c5a4047230c63dc8825e19883258b1).

我们可以看到几个简单的内容:

- 挖出区块 #88888 的矿工是 `955`, 但是这个区块的 cellbase 是给到了尾号为 `ea0` 的地址.
- 挖出区块 #88877 的矿工是 `ea0`, 但是这个区块的 cellbase 是给到了尾号为 `dnr` 的地址.
- 一个区块的奖励有[四个部分](https://explorer.nervos.org/transaction/0x679093b7b43ff512097f864b14f80c11a1c4b1266cbe7bee0459372b14f34e9f): 基础奖励, 二级奖励, 提交奖励, 提案奖励

也就是说区块 #88877 的区块奖励是在区块 #88888 才发放的, 这是由于 Nervos CKB 采用了新型的共识机制 -- NC Max(一个基于中本聪共识的改进版本). 简单来说, 在区块奖励这边, 一个区块高度为 N 的区块的出块奖励会在区块 N+11 通过 cellbase 发放. 所以在 CKB 的网络里面挖出区块了不要着急哦, 区块奖励可能需要飞一会儿.

```sh
# 查询余额
$ ckb-cli wallet get-capacity --lock-arg 0x75178f34549c5fe9cd1a0c57aebd01e7ddf9249e
```

## 转账

现在我们将从账号 A 转账一笔钱给账号 B. 需要使用到的命令是 `wallet transfer`.

```sh
# 交易转账
$ ckb-cli wallet transfer --from-account 0x75178f34549c5fe9cd1a0c57aebd01e7ddf9249e --to-address ckt1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqdrcaufs8qeu8wvvy0myyedek4vqad9qeq3gc4cf --capacity 520
```
