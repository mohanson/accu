# Solana/交易/构建本地开发环境

交易是 solana 系统中最为核心的部分之一. 在本章节中, 我们将深入分析 solana 的各种交易形式, 包括如何创建交易, 为交易签名, 以及将交易发送至验证者节点, 使其成为 solana 系统永久交易记录的一部分.

在区块链上执行交易需要支付手续费, 而在主网上进行测试成本较高. 因此, 搭建一个本地 solana 开发链对于开发和测试至关重要. 本文将详细介绍如何在本地搭建 solana 开发链, 并为您的账户获取 sol 空投, 以便用于测试和开发.

## 获取 solana 官方发布包

2024 年 3 月 2 日, Solana 经历了一次重大的人事变动: solana 客户端的开发工作从 solana labs 移交至 anza 团队. 该团队 fork 了 solana 的源代码, 此后所有开发工作均在新 fork 的仓库中进行.

您可以通过当时的新闻报道了解更多细节: <https://solana.com/news/solana-labs-anza-fork>.

这次变动导致原有的 solana 仓库失效, 新 fork 的仓库则命名为 agave. 因此, 现在 solana 唯一的官方仓库地址为: <https://github.com/anza-xyz/agave>.

在该仓库的发布页面找到二进制发布包, 下载并解压. 以 ubuntu 系统为例, 可使用以下命令完成操作:

```sh
$ wget https://github.com/anza-xyz/agave/releases/download/v2.0.20/solana-release-x86_64-unknown-linux-gnu.tar.bz2
$ tar -xvf solana-release-x86_64-unknown-linux-gnu.tar.bz2
$ cd solana-release
```

> 注意: 本文撰写时, agave 的最新版本为 v2.0.20. 但随着时间推移, 该版本可能已不是最新版本. 请始终选择发布页面上显示的最新版本!

安装完成后, 可通过以下命令检查 Solana 是否成功安装:

```sh
$ solana --version
# solana-cli 2.0.20 (src:20a8749f; feat:607245837, client:Agave)
```

如果显示 solana 的版本信息, 说明安装成功.

## 启动 solana 本地开发链

Solana 提供了一个名为 solana-test-validator 的工具, 可以帮助我们在本地启动一个 solana 开发链. 执行以下命令来启动本地测试链:

```sh
$ solana-test-validator
```

此命令将启动一个本地的 solana 区块链实例, 默认情况下, 它会在端口 8899 上提供 api 接口. 你可以看到类似下面的输出, 表示本地链正在运行:

```sh
# Identity: H3SmeomgugZP3AYzgeLuL9ZfHQrUWahFBkzeiwdzCmaE
# Genesis Hash: B1Kc8gnygWEW6ZXxV4STaheM9WAWNYqukTLuxoiCWjUX
# Version: 2.0.20
# Shred Version: 57683
# Gossip Address: 127.0.0.1:1024
# TPU Address: 127.0.0.1:1027
# JSON RPC URL: http://127.0.0.1:8899
# WebSocket PubSub URL: ws://127.0.0.1:8900
```

## 配置 solana 命令行工具

为了让 solana 命令行工具与本地链进行交互, 您需要设置 solana 使用本地链的配置. 运行以下命令:

```sh
$ solana config set --url http://localhost:8899
```

## 创建 solana 钱包

执行以下命令:

```sh
$ solana-keygen new
```

这将生成一个新的密钥对并保存到 ~/.config/solana/id.json 文件中. 你可以通过以下命令查看该账户的公钥:

```sh
$ solana address
# 6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt
```

例: 通过上述方式创建的钱包是随机的, 不同用户生成的私钥和地址均不同. 回顾第一章内容, 若需让 solana 命令行工具使用私钥为 0x01 的账户, 应如何操作?

答: id.json 文件存储了账号的公私钥对. 我们编辑 ~/.config/solana/id.json, 将其内容替换为以下代码生成的目标公私钥对:

```py
import pxsol

prikey = pxsol.core.PriKey.int_decode(0x01)
pubkey = prikey.pubkey()
print(list(prikey.p + pubkey.p))
```

## 获取 solana 测试硬币

在本地链上, 您可以通过请求空投 sol 来为钱包账户提供一些测试资金. 使用以下命令为你的账户获取空投 sol:

```sh
$ solana airdrop 10
```

此命令将为你当前配置的账户空投 10 个 sol. 如果你需要空投更多 sol, 可以调整数字, 例如:

```sh
$ solana airdrop 100
```

您还可以为空投至指定账户, 添加目标地址作为参数, 例如:

```sh
$ solana airdrop 10 6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt
```

你可以通过以下命令查看账户的余额, 确认空投是否成功:

```sh
$ solana balance
```

如果一切顺利, 你将看到账户中已经有了空投的 sol.

## 注意事项

0. 本地开发链会消耗一定量的内存, CPU 和磁盘空间. 连续运行 24 小时可能占用约 8g 磁盘空间, 请提前规划.
0. 本地开发链的数据可能不会保存, 重启后需要重新请求空投. 但您不需要重新创建账号.
0. 如果你想回到主网或其他网络(如 devnet), 可以用 `solana config set --url <URL>` 切换, 例如: `solana config set --url https://api.devnet.solana.com`

## 准备就绪

至此, 您已成功搭建本地 solana 开发链, 并为账户空投了 sol 测试代币.

接下来是……
