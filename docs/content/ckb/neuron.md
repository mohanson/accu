# CKB/Neuron 钱包

Neuron 是 CKB 的全节点钱包, 截至 2023/03/14, 该钱包至少需要 45G 硬盘空间保存链上数据. 钱包下载地址:

<https://github.com/nervosnetwork/neuron>

当第一次启动钱包时, 钱包会自动运行一个 CKB 全节点并开始同步数据. 如果你确实不希望同步一个全节点, 也可以点击帮助 -> 设置 -> 网络 -> 添加网络, 填写社区公开的 mainnet 服务地址(同步速度较慢):

<https://github.com/nervosnetwork/ckb/wiki/Public-JSON-RPC-nodes#ckb>

|  type   |             url             |
| ------- | --------------------------- |
| mainnet | https://mainnet.ckbapp.dev/ |
| mainnet | https://mainnet.ckb.dev/    |
| testnet | https://testnet.ckbapp.dev/ |
| testnet | https://testnet.ckb.dev/    |

## 创建钱包

Neuron 是一个 HD(Hierarchical Deterministic Wallets, 分层确定性)钱包, 由 [BIP-32](https://river.com/learn/terms/b/bip-32), [BIP-39](https://river.com/learn/terms/b/bip-39), BIP-43 和 [BIP-44](https://river.com/learn/terms/b/bip-44) 共同定义. 当创建钱包时, 系统会显示 12 个助记词并提示你记录下来. 保管好这 12 个助记词, 遗忘或泄露都会造成财产的损失.

## 备份钱包

有多种方式可以备份您的钱包.

**助记词**

关于助记词, 请记住一点, 助记词等于钱包. 任何人拿到助记词, 就意味着拥有了该钱包的一切权限. 如果你不幸忘记了助记词, 那么目前也无法从钱包中恢复助记词, 因为根据 BIP32 和 BIP39, 助记词记录的是钱包的种子, 该种子必须进行一次哈希才能生成钱包, 而哈希是不可逆的.

**Keystore**

Keystore 是以 JSON 格式存储的加密的私钥文件, 它通过一个额外的密码来保护私钥. 当此 Keystore 与密码一起使用时, 它类似于私钥. Keystore 比私钥或助记词更安全, 因为您需要密码才能访问它, 但请记住这并不意味着在网络上公开 Keystore 是安全的.

**Extended Public Key**

扩展公钥或 xpub 是一个公钥, 可用于推导 HD 钱包的子公钥. 扩展公钥是 BIP32 建立的比特币标准, 主要由幕后的钱包使用用以推导公钥.

<https://river.com/learn/terms/x/xpub-extended-public-key/>

任何知道您的扩展公钥的人都可以得出 HD 钱包所有的公钥, 因此可以看到过去和将来的每一次交易. 扩展公钥对于将比特币接收到冷钱包很有用, 因为用户可以将其扩展公钥保持在线以生成新地址, 同时其私钥保持离线.

无法通过扩展公钥推导出任何私钥, 因此通过扩展公钥导入的钱包仅仅是一个只读钱包, 无法发出交易. 泄露扩展公钥不会对资金安全造成损失, 但您的隐私将会受损.

## Nervos DAO

Nervos CKB 的经济模型旨在允许 CKB 持有人将其 CKB 锁定在 Nervos Dao 中, 以减轻次级发行的通货膨胀效应. 在这种情况下, 次级发行的通货膨胀效应预计将仅是名义上的.

CKB 有两个货币增发途径, 分别是基础发行和次级发行. 基础发行的规则与比特币挖矿类似, 网络向矿工支付固定数量的 CKB, 以奖励其提供的计算机资源. 基础发行大约每四年补贴金额减半, 并最终停止在 336 亿个 CKB. 次级发行则是遵循每年增发 13.44 亿个 CKB, 这些 CKB 会被分配给矿工, Nervos Dao 使用者以及 Nervos 基金会.

可以访问其[经济模型](https://docs.nervos.org/docs/basics/concepts/economics/)了解更多.

Nervos Dao 的一些信息可以在该[页面](https://explorer.nervos.org/nervosdao)查询. 截至 2023/03/27, 锁定总额 9334843250.41, 年化收益 2.47%, 地址数 23550.

## 转账限制

给任何 CKB 地址转账的时候, 最少转 61 CKB. 这是因为每个 Cell 都需要占用最少 61 CKB 的存储费用, 转账时如果余额不足 61 CKB, 则无法创建新的 Cell, 从而导致转账失败.
