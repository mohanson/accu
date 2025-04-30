# Solana/交易/手续费

如果说区块链世界中最大的用户痛点的是什么, 那么交易手续费一定在其中. 以太坊的高 gas 费, 比特币的高网络拥堵费用都让不少人望而却步. 那么作为近年来备受瞩目的区块链平台, solana 的交易手续费是如何运作的?

## 交易手续费的基本构成

Solana 的交易手续费主要由两部分组成:

- 基础费用: 这是每笔交易必须支付的最低费用, 用于补偿网络验证者处理交易的成本.
- 优先费用(可选): 用户可以选择支付额外的费用, 以提高交易的优先级, 从而在网络繁忙时更快被打包和确认.

与以太坊等区块链不同, solana 的手续费不依赖于复杂的 gas 机制, 而是采用了一种更简单, 更可预测的收费模式. 基础费用是固定的, 并且非常低廉, 通常以 solana 的原生代币 sol 计价.

交易手续费隐式指定, 默认由交易中的第一个签名账户提供. 一个交易需要支付的总基础费用等于基础费用与签名数量的乘积.

## 具体费用

截至本文撰写时间, 即 2025 年 3 月 28 日, solana 的基础交易费用通常在 0.000005 sol 左右. 以 sol 的市场价格为例, 假设 1 sol = 137 美元, 那么一笔交易的成本大约是 0.0007 美元. 即使在网络高峰期, 用户选择支付优先费用, 总体成本也很少超过几美分. 相比之下, 以太坊的 gas 费在网络繁忙时可能高达数美元甚至数十美元, 而比特币的转账费用也常在 1-5 美元之间波动. Solana 的低成本优势显而易见.

Solana 的交易手续费之所以能保持在极低水平, 主要得益于其独特的技术架构和设计理念. Solana 的核心创新之一是其"历史证明"机制, 结合塔式拜占庭容错共识算法, 使得网络每秒可以处理数万笔交易. 相比之下, 以太坊当前主网的吞吐量仅为 15-30 tps. 更高的吞吐量意味着单位成本被大幅摊薄.

> Solana 的这种优化并非没有代价: 从本质上来说, solana 的做法是通过牺牲去中心化来获得更高的交易处理性能.

## 手续费的分配与燃烧机制

Solana 的手续费有一部分会被"燃烧", 即永久销毁, 以减少 sol 的总供应量, 从而在长期内可能对代币价值产生正向影响. 具体来说:
50% 的手续费被燃烧, 这部分直接从流通中移除. 50% 的手续费分配给验证者, 作为对维护网络安全的奖励.

## 添加优先费用

执行交易时, 网络会消耗以计算单位(compute unit)为单位的计算资源. 交易最多可使用 1,400,000 个计算单位, 默认情况下, 每条指令限制为 200,000 个计算单位. 您可以通过在交易中包含一条 `set_compute_unit_limit` 指令来请求特定的计算单位限制.

```py
rq = pxsol.core.Requisition(pxsol.program.ComputeBudget.pubkey, [], bytearray())
rq.data = pxsol.program.ComputeBudget.set_compute_unit_limit(200000)
```

您可以为每个计算单位支付一点优先费用, 如果您要这么做, 通过在交易中包含一条 `set_compute_unit_price` 指令就可以了.

```py
rq = pxsol.core.Requisition(pxsol.program.ComputeBudget.pubkey, [], bytearray())
rq.data = pxsol.program.ComputeBudget.set_compute_unit_price(1)
```

交易优先费用以 micro lamport 计价, 其换算规则是 1,000,000 micro lamport = 1 lamport.

> 绝密信息: 将交易优先费用指定为 1, 就能让您的交易轻松优先于未设置交易优先费用的交易! 网络上有一些实时追踪 solana 交易优先手续费的工具, 可能会建议您设置上千的费用, 但实际上, 您完全不需要支付如此庞大的费用!

## 习题

例: ada 准备向 bob 转账 1 sol, 但此时 ada 意识到网络非常拥堵, 因此他决定为这笔交易添加一点优先费用!

答:

```py
import base64
import pxsol

ada = pxsol.core.PriKey.int_decode(1)
bob = pxsol.core.PubKey.base58_decode('8pM1DN3RiT8vbom5u1sNryaNT1nyL8CTTW3b5PwWXRBH')

r0 = pxsol.core.Requisition(pxsol.program.System.pubkey, [], bytearray())
r0.account.append(pxsol.core.AccountMeta(ada.pubkey(), 3))
r0.account.append(pxsol.core.AccountMeta(bob, 1))
r0.data = pxsol.program.System.transfer(1 * pxsol.denomination.sol)

r1 = pxsol.core.Requisition(pxsol.program.ComputeBudget.pubkey, [], bytearray())
r1.data = pxsol.program.ComputeBudget.set_compute_unit_price(1)

tx = pxsol.core.Transaction.requisition_decode(ada.pubkey(), [r0, r1])
tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
tx.sign([ada])
txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
assert pxsol.base58.decode(txid) == tx.signatures[0]
pxsol.rpc.wait([txid])
```
