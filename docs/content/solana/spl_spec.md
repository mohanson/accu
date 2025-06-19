# Solana/SPL Token/历史与核心规范概览

## 为什么需要 SPL Token

基于 solana 账户模型的关系, solana 本身并不内建"一个代币账户有多少余额"这样的逻辑. 开发者必须使用 pda 数据账户手动实现代币的存储, 增发与转账. 但这显然容易出错, 也容易重复造轮子. 用户还必须面临一个最大的问题: 不同的代币, 所支持的指令可能是不同的.

为了解决这个问题, solana 团队创建了 spl token, 作为统一的代币标准. 它参考了以太坊的 erc20 规范, 为开发者提供标准接口, 来促进生态兼容性. 这样钱包, dex, defi 等应用都可以通用识别代币.

与以太坊的 erc20 标准不同, 开发者无需自己部署 spl token 的代码, 相反开发者只需要创建一个被称为 spl 铸造账户的账户, 用于存储该代币的基本信息, 就可以创建出一个自己的 spl token.

## 查询链上代币信息

我们以 solana 上使用较为广泛的 usdc 代币为例, 该代币的铸造账户地址为 `EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v`, 您可以通过[浏览器](https://explorer.solana.com/address/EPjFWdd5AufqSSqeM2qN1xzybapC8G4wEGGkZwyTDt1v/metadata)查询到该代币, 一些重要信息如下.

|    Overview    |                   |
| -------------- | ----------------- |
| Current Supply | 7761611891.221625 |
| Decimals       | 6                 |
| data.name      | USD Coin          |
| data.symbol    | USDC              |

根据[最新数据](https://learn.backpack.exchange/articles/pump-fun-token-launch-2025-pump-airdrop-rumors-1b-raise-and-solana-market-impact), 截至 2025 年 06 月, solana 网络上总共有一千三百万个 spl token, 其中 pump.fun 一家就铸出了一千一百万个 token. 历史峰值出现在 2024 年 10 月 24 日, 仅仅一天就铸造了 3.6 万个新 spl token.

在 solana 创建一个新的代币几乎不花钱, 任何有一定经验的开发者都能在 1 秒之内就能完成. 同时 pump.fun 以及 let's bonk 等网站上线的一键发币功能也吸引了大量非开发者用户, 助推了 spl token 的数量暴涨.

> 让我们铸出来再说!

## 发展历史

Solana 刚上线时, spl token 是以最小可行产品方式发布(v1). 该版本仅支持铸造, 销毁和转账基本操作. 这时的 spl token 主要目标是跑通代币系统, 尚不追求高级功能.

随着 serum, raydium 等 dex 的出现, spl token 成为了 solana 各类资产流通的基石(v2). 这一阶段的重点是规范了钱包的支持, 并引入 token metadata(该功能由 metaplex 提供, 允许为 spl token 设置名字, 符号等信息).

从 2023 至今, 最近的 spl token v3(也称 token-2022)开始引入更强大的功能, 例如允许冻结账户, 转账钩子(用于支持合约式回调). 但这也意味着 token-2022 开始与旧版 spl token 不完全兼容, 一些老旧的钱包和应用可能尚未完全支持. 虽然如此, 如果您正试图创造一种新代币, 从 token-2022 入手, 是一条最省心的路径, 本课程也将默认采用 token-2022 规范进行讲解.

## 核心规范概览

使用 token-2022 定义一个 spl token 大致需要用到 4 个不同的账户.

|      类型      |                                         说明                                          |
| -------------- | ------------------------------------------------------------------------------------- |
| 程序账户       | token 2022 原生程序, 地址 `TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb`               |
| 铸造账户       | token 2022 的主账户, 代表某种 token 的定义, 包含总量, 权限, 小数精度等信息            |
| 元数据程序账户 | 一个独立合约, 由 metaplex 团队提供, 用于给铸造账户挂上额外信息                        |
| 元数据数据账户 | 元数据程序账户派生的 pda 账户, 存储该 token 的人类可读信息, 如名字, 符号, 图标 url 等 |

程序账户有两个不同版本, 旧版地址为 `TokenkegQfeZyiNwAJbNbGKPFXCWuBvf9Ss623VQ5DA`, 但目前已经基本弃用. 如果您在浏览器上查找一些极早期发行的代币, 可能会见到它.

这些账户之间的关系图如下:

```text
┌─────────────────────────────────────┐
│        Token Program v2022          │
│       (TokenzQd...xxx)              │
└─────────────────┬───────────────────┘
                  │
                  v
┌─────────────────────────────────────┐
│            Mint Account             │
│-------------------------------------│
│      decimals:        u8            │
│      supply:          u64           │
│      mint_authority:  Pubkey        │
│      freeze_authority:Option<>      │
└─────────────────┬───────────────────┘
                  │
                  v
┌─────────────────────────────────────┐
│       Token Metadata Program        │
│      (metaqbxx...)                  │
└─────────────────┬───────────────────┘
                  │
                  v
┌─────────────────────────────────────┐
│          Metadata Account           │
│ (PDA derived from Mint + seeds)     │
│-------------------------------------│
│ name: "Thai Baht Coin"              │
│ symbol: "THB"                       │
│ uri: "https://arweave.net/..."      │
└─────────────────────────────────────┘
```

总结来说, 基于一些历史原因, spl token 被设计为如此. 铸造账户是代币的基础, 用来管理代币供应和权限. 元数据账户是基于铸造账户派生出来的一个 pda 数据账户, 用来附加包装纸, 描述代币的名字, logo 等供人类阅读的信息.

Solana 已经铺好路，只等你发车.
