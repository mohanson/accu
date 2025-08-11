# Solana/经济系统/创世块(一)

Solana 区块链于 2020 年 3 月 16 日正式上线, 其创世块是区块链的第一个区块, 标志着网络的启动. 创世块本身不包含源代码, 而是一个初始状态的快照, 定义了网络的初始参数, 账户状态和代币分配等. Solana 的创世块可以通过区块链浏览器查看, 但如果想具体查看创世块的交易或账户需要通过节点或相关工具查询.

在 solana 里, 创世块与其说是一个块, 称它为一个配置文件似乎更为妥当.

您可以通过区块链浏览器"查询"创世块, 但除了最基本的数据外, 您无法从浏览器中得到更多有意义的信息: <https://explorer.solana.com/block/0>.

## 创世块代币分发

Solana 代币初始分发在网络启动时通过创世块完成. 根据 solana 白皮书, 创世块中的 sol 主要分配给了以下几类参与者:

1. 种子轮和早期投资者: 包括风险投资机构(如 a16z, multicoin capital 等)和早期支持者.
2. 团队和基金会: solana labs 团队和 solana 基金会保留了一部分代币, 用于开发和生态系统建设.
3. 社区和奖励: 部分代币分配给社区激励, 验证者奖励等.

根据**非官方来源的**的公开信息和社区讨论, solana 的初始代币分配大致如下:

1. 种子轮和私募: 约 25-30% 分配给早期投资者.
2. 团队: 约 12.5%.
3. 基金会/生态系统: 约 10-15%.
4. 社区/奖励: 剩余部分用于验证者奖励, 空投和其他社区激励.

我们谨慎的看待以上信息.

## 获取创世块数据

为了更加真实的研究 solana 的经济系统, 我决定直接分析创世块中的数据. 幸运的是, 创世块信息是**半公开**的. 您能从网络上得到创世块的数据, 但同时网络上却缺少教程来教您分析它, 也没有任何网页或图表展示它, 因此我称它为半公开. 本文将试图改变这一点.

首先我们下载创世块数据的压缩档并解压它, 获得 `genesis.bin` 文件.

```sh
$ mkdir ledger
$ cd ledger
$ wget https://api.mainnet-beta.solana.com/genesis.tar.bz2
$ tar -jxvf genesis.tar.bz2
$ ll

# drwxrwxr-x   2 ubuntu ubuntu   4096 Aug  8 18:24 ./
# drwxrwxrwt 101 ubuntu ubuntu  65536 Aug  8 18:28 ../
# rw-r--r--    1 ubuntu ubuntu 132347 Mar 16  2020 genesis.bin
```

该文件使用 bincode 编码了一个账户列表, 我们需要编译一个工具来分析 `genesis.bin` 文件. 下载 solana 源码库, 并编译其中的 `ledger-tool` 工具.

```sh
$ git clone https://github.com/anza-xyz/agave
$ cd ledger-tool
$ cargo build
```

执行编译出来的 `agave-ledger-tool` 并在参数中指定我们刚才保存 `genesis.bin` 的目录:

```sh
$ agave-ledger-tool genesis --ledger ledger --accounts --output json
```

我们得到了创世块中获得初始分配的所有账号列表. 该列表中共保存了 431 个账户, 在这里只截取头尾两个账户显示如下.

```json
{
  "accounts": [
    {
      "pubkey": "13LeFbG6m2EP1fqCj9k66fcXsoTHMMtgr7c78AivUrYD",
      "account": {
        "lamports": 153333633390909120,
        "data": [
          "AQAAAIDVIgAAAAAAEz9W2TmIqMRgQ0rrgC89RndskM9PojDPkwTMSiLZq/lkVvBa571/bSeULSeR8aaRDAXCdHyD8RGsnvQTimS4AgAAAAAAAAAAAAAAAAAAAAAFR0dn5PH8Rp6b7RVvpNOHD2ek8+95bZYJHcoJ866WowAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
          "base64"
        ],
        "owner": "Stake11111111111111111111111111111111111111",
        "executable": false,
        "rentEpoch": 0,
        "space": 200
      }
    },
    ... ...
    {
      "pubkey": "JCo7ptMT38iZdjXXdxD8Ye79dGBBkMi2nttnv965k3pE",
      "account": {
        "lamports": 104166666268940,
        "data": [
          "AQAAAIDVIgAAAAAAHo5ufv6LXJUFQplRqRqFRQY4YFx4p81H20CZkWDY9q37k5kcYLD2AC8789vlnsUxaVMBz0/FeathVFoOL2wFSwAAAAAAAAAAigoAAAAAAAAFR0dn5PH8Rp6b7RVvpNOHD2ek8+95bZYJHcoJ866WowAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAAA=",
          "base64"
        ],
        "owner": "Stake11111111111111111111111111111111111111",
        "executable": false,
        "rentEpoch": 0,
        "space": 200
      }
    },
}
```

您可以直接通过地址 <https://raw.githubusercontent.com/mohanson/pxsol/refs/heads/master/res/genesis.json> 下载我预先解析好的 json 文件.

```sh
$ wget https://raw.githubusercontent.com/mohanson/pxsol/refs/heads/master/res/genesis.json
```
