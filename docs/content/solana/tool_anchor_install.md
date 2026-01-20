# Solana/更多开发者工具/Anchor 环境搭建

在本书的中篇内容里, 我们将第一个想法带上 solana, 我们编写了一个可以存储任意数据的简单数据存储程序. 我们使用原生 rust 编写了这个程序, 但过程中需要我们直面账户校验, 序列化和客户端打包这些杂事, 往往会消磨兴致. Anchor 出场的意义, 正是把这些粗重活接过去, 让你把精力放在要实现什么, 而不是怎么让代码"跑"起来.

Anchor 是一种为 solana 区块链设计的开发框架, 用于快速, 安全地构建和部署链上程序. 它通过提供工具和抽象来简化开发流程, 包括自动处理账户和指令数据的序列化, 内置安全检查, 生成客户端库以及提供测试工具.

我们在这里用 Anchor 重写那个数据存储程序, 让你体会它的魔力. 我们不会在这里做说明书式的工具介绍, 如果您需要它, 请参考[官方文档](https://book.anchor-lang.com/). 我们只会准备一张干净的工作台来组装代码, 让你专注于实现核心功能. 你会看到 anchor 的核心心智模型, 完成一次从零到一的本地运行, 并学会辨认路上的几个小坑.

## 历史

Anchor 最初由 project serum(由 ftx 交易所主导) 团队开发, 旨在简化 solana 上的智能合约开发. 在 solana 生态早期, 大家通常使用 solana-program 直接编写原生 rust 程序, 但面临一些问题:

0. 大量的样板代码. 开发者需要编写大量重复的代码来处理账户验证, pda 账户管理, 租赁豁免管理等琐事.
0. 安全性挑战. 直接操作低级账户和指令数据容易引入安全漏洞, 需要开发者具备深厚的 solana 内部知识.

Anchor 通过引入高级抽象和自动化工具, 大大简化了这些任务. 它大量使用**宏**和**属性**来自动生成样板代码以防止常见漏洞, 并生成易于使用的客户端库.

不过后续随着 2022 年 11 月 ftx 交易所崩盘, project serum 团队解体, anchor 的维护也一度陷入停滞. 原 serum 团队部分成员成立了 coral-xyz, anchor 的仓库迁移到了 <https://github.com/coral-xyz/anchor>. 在 2025 年 4 月, solana 开发团队经历了一次重大人事变动, solana 协议的核心客户端 solana 改名 agave 并由 solana-labs 转移给了 anza-xyz 团队; anchor 则是由 coral-xyz 转移给了 solana-foundation 维护: <https://github.com/solana-foundation/anchor>.

> 2025 年 4 月这次人事变动看起来范围相当巨大.

## 环境搭建

如果你的机器还没有这些工具, 请先安好: rust, solana cli, node.js 与 yarn, 以及 anchor 本体. 下面的命令可以直接复用; 若你已有其一, 可跳过相应小节.

安装 anchor(使用 avm 管理版本):

```bash
$ cargo install --git https://github.com/coral-xyz/anchor avm --locked --force
$ avm install latest
$ avm use latest
$ anchor --version
```

准备 solana cli 与本地链:

```bash
$  sh -c "$(curl -sSfL https://release.solana.com/stable/install)"
$ solana --version
$ solana config set --url http://127.0.0.1:8899
$ solana-test-validator -r
```

准备 node.js 与 yarn, 因为 anchor 的测试与客户端默认使用 ts:

```bash
$ npm install -g yarn
```

本章节的配套代码在[这里](https://github.com/mohanson/pxsol-ss-anchor). 如果你正在阅读该配套仓库, `Anchor.toml` 已预设本地网络与钱包路径, `tests/` 里也放好了 ts 的测试脚本. 进入仓库根目录, 装上依赖即可:

```bash
$ yarn install
```

小提示: 第一次跑本地链时, 别忘了给默认钱包要点启动资金.

```bash
$ solana airdrop 2
```

## 创建项目

我们先使用 anchor 搭一个最小可用的程序, 看看它长什么样.

```bash
$ anchor init pxsol-ss-anchor
$ cd pxsol-ss-anchor
```

脚手架会生成一套目录:

- `programs/<name>/src/lib.rs` 是合约入口. 你会看到 `#[program]` 模块和一两个演示方法.
- `Anchor.toml` 是配置中心, 记录 program id, 要连接的集群, 测试脚本等.
- `tests/` 放着 ts 测试, 等会儿它会代表客户端来与节点进行交互和测试.

先试着构建它:

```bash
$ anchor build
```

如果你还没启动本地链, 开一个终端让验证器常驻:

```bash
$ solana-test-validator -r
```

接着跑一次测试:

```bash
$ anchor test --skip-local-validator
```

这条命令做了三件事:

0. 构建 rust 程序
0. 把它部署到本地链
0. 运行 `tests/` 下的 ts 测试用例

## 如何开始

当我们开始实现真正的业务, 可以沿着这条最小路径前进:

0. 在 `programs/<name>/src/lib.rs`:
    - 定义 pda 账户的数据结构, 使用 `#[account]` 标记它们.
    - 新增一些方法, 编写业务逻辑, 使用 `Context<>` 定义每个方法需要的账户.
    - 写出期望的 accounts 结构与约束.
0. 在 `tests/` 写一个最小的调用脚本, 跑 `anchor test` 观察失败信息.
0. 循环填写逻辑代码, 补齐账户, 空间与权限, 并时刻调整测试脚本, 直到测试通过.
0. 最后接入前端或后端服务.

当你跨过这些门槛, anchor 就会像一把顺手的扳手. 你不用每天都去记 torx 和内六角的尺寸, 只管拧紧你真正关心的那颗螺丝.
