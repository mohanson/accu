# Solana/交易/货币面值

Solana 网络的原生加密货币称为 sol. 它类似于其他区块链的代币, 如比特币的 btc, 以太坊的 eth 等等, 用来支付交易费用, 参与网络治理, 以及充当一种价值存储工具.

Solana 网络中最小的计量单位被称作 lamport. 类似于比特币中的"聪", solana 也需要有一种更小的单位来精确表示非常小的交易金额. 1 sol 等于 10⁹ lamport. 这使得在处理微小交易时, 不会因为单位限制而引发精度丢失问题.

例: 0.33 sol 等于多少 lamport?

答: 0.33 * 10⁹ = 330000000 lamport. 库 `pxsol.denomination` 中定义了 sol 和 lamport 的面值, 可以使用如下代码进行转换.

```py
import pxsol

print(int(0.33 * pxsol.denomination.sol))
# 330000000
```

Lamport 是 sol 的子单位, 类似于美元与美分之间的关系(1 美元 = 100 美分). 在 solana 网络中, 所有的余额和交易量都是以 lamport 来表示的, 但用户通常以 sol 为单位与网络交互, 进行交易或转账时, sol 是用户界面上显示的单位.

关于 lamport 这个名称的由来, solana 创始人 anatoly yakovenko 在设计时决定用 "lamport" 来致敬计算机科学领域的著名学者 [leslie lamport](https://en.wikipedia.org/wiki/Leslie_Lamport). Leslie lamport 是分布式系统和并发计算领域的先驱, 他的研究成果对现代区块链技术有着重要的影响. 特别是在分布式系统中的时间同步问题和共识机制方面, lamport 的贡献为 solana 的高效共识算法(历史证明)提供了理论支持.

至于为什么选择 sol 作为代币的名称, 作者没有找到确切的证据, 但能略微猜测一二:

0. 币圈项目通常使用三个字母作为代币名称, 在 solana 开发阶段, sol 恰巧是一个未被使用的名称.
0. 容易让用户联想到"太阳"(solar)的意思, 寓意一个充满活力, 不断成长并提供光明的未来.

在最后, 我会给您一些建议. 您在 solana 网络中进行一切活动时, 都应当特别注意:

0. Lamport 是 solana 网络的真实存在的最小单位, sol 则更多是一种象征符号, 并不真实存在.
0. 作为开发者, 您总是应该操作 lamport, 而仅在最后展示给用户时, 将其转换为 sol.
