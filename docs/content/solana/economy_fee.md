# Solana/经济系统/手续费与手续费燃烧

Solana 的手续费体系采用两层结构, 主要由基础费用和优先费用组成, 辅以存储租金机制, 以支持网络的高效运行和抗垃圾交易能力.

## 基础费用

每笔 solana 交易都需要支付基础费用, 用于补偿验证者处理交易所需的计算资源. 基础费用固定为每个签名 5000 lamports. 以 2025 年 sol 价格约为 200 美元为例, 5000 lamports 相当于约 0.001 美元, 即千分之一美元. 这种固定费率设计使得 solana 的交易成本在网络拥堵时仍保持稳定, 与以太坊等基于拍卖的费用模型形成鲜明对比.

Solana 的费用燃烧机制是其经济模型的重要组成部分, 旨在通过减少 sol 的流通供应来支持代币的长期价值. 基础费用的 50% (即2500 lamports/签名)会被燃烧, 永久移除出流通供应, 剩余 50% 分配给处理交易的验证者.

在本文写作时, 根据 [solana compass](https://solanacompass.com/statistics/fees) 上的数据, 在过去 24 小时时间里, 用户总计支付了 1675.48 sol 的基础费用, 也就是说有 837.74 sol 被同时燃烧销毁. 按此估算, 年度燃烧量约为 305775 sol. 若以 2025 年 sol 价格 200 美元计算, 年度燃烧价值约为 61155000 美元.

这种燃烧机制类似于以太坊的 [eip-1559](https://github.com/ethereum/EIPs/blob/master/EIPS/eip-1559.md), 通过减少代币供应来增强 sol 作为价值存储的潜力.

## 优先费用

优先费用是可选的附加费用, 用户可以通过支付额外的 sol 来提高交易被当前领导者(即验证者)优先处理的概率. 优先费用的计算公式为 `计算单元限制 x 计算单元价格`.

其中, 计算单元限制是交易可使用的最大计算资源, 上限为 140 万个计算单元, 默认 200000 个. 计算单元价格由用户指定. 根据 [SIMD-0096](https://github.com/solana-foundation/solana-improvement-documents/blob/main/proposals/0096-reward-collected-priority-fee-in-entirety.md), 优先费用完全由处理交易的验证者收取, 不进行燃烧.

在本文写作时, 根据 [solana compass](https://solanacompass.com/statistics/fees) 上的数据, 在过去 24 小时时间里, 用户总计支付了 3268.76 sol 的优先费用, 且 66.42% 的交易用户都支付了优先费用.

## 存储租金

在 solana上, 存储账户数据需要支付租金, 费用与账户占用空间成正比. 租金费用在账户关闭时可退还, 旨在激励用户清理不必要的链上数据. 50% 的租金费用会被燃烧, 剩余 50% 分配给验证者.

租金费用相当于将一半 sol 永久移出流动池, 并将剩下一半 sol **暂时**移出流动池, 除非用户决定删除自己的账户, 否则这部分租金将永远不会参与流通. 根据 [coinlaw 的报告](https://coinlaw.io/solana-statistics/), solana 目前每周新增约 200000 个钱包, 平均每日新增约 28571 个账户.

> More than 200,000 new wallets are created on Solana each week, indicating robust organic adoption.

假设一个账户的平均数据大小为 165 字节(spl token 账户的典型大小), 那么使用以下代码估算下每日新增租金消耗约为 83 sol.

```py
import pxsol

pxsol.config.current = pxsol.config.mainnet

lamport = pxsol.rpc.get_minimum_balance_for_rent_exemption(128 + 165, {}) * 28571
sol = lamport / pxsol.denomination.sol
print(sol) # 83.71760136
```

不过事实上, 如果一名开发者要在 solana 网络上部署程序账户, 需要支付的租金要远远大于一个普通用户账户. 因此这个 83 sol 数据是极端低估的.

## 总结

Solana 的手续费规则通过固定基础费用, 可选优先费用和存储租金的组合, 实现了低成本, 可预测和高效率的交易体验. 理论上来说, 通过手续费燃烧机制, 可以有效减少 sol 的流通供应, 增强代币的经济价值. 然而, 以实际数据来说, 被燃烧掉的 sol 只占每年通胀增发的极小部分(数据参考上一章节), 也就是说想依靠手续费燃烧扭通胀为通缩, 短期看来是不可能的.
