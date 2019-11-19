# 以太坊: 交易

交易(Transaction)是由外部调用者签名的一段数据. 它表示一个消息(Message)或一个合约(Contract). 交易记录在区块链的每个区块中.

消息(Message)是两个账户之间传递的数据(字节数组)和值(以太). 它类似两个银行账户间的转账操作: 值相当于转账数量, 字节数组相当于留言.

合约(Contract)是存储在区块中的一段代码. 这段代码作为字节码存储在区块链中, 一旦创建就不可变. 合约的地址类似于普通的基于私钥的帐户地址, 区别在于合约地址没有关联的私钥. 在其他所有方面, 合约地址都被视为与私钥支持的地址相同. 当消息发送到合约地址时, 会触发合约字节码的执行. 合约代码可以做任何正常地址可以做的事情, 包括向其他地址发送资金和在其他合约上调用代码. 合约无法做到的正常地址唯一的事情就是启动交易. 以太坊交易必须始终由基于私钥的地址启动.

现在先暂时忽略合约, 体验一下如何在以太坊上进行以太的转账.

# 乞讨以太

现在您有上一章节中所创建的私钥与地址了, 接下来您需要拥有一点以太在这个地址上. 一些慷慨的人免费提供了 ropsten 测试链上的以太: [http://faucet.ropsten.be:3001/](http://faucet.ropsten.be:3001/). 只需要填上您的以太地址就能获得 1 ETH. 注意, 过于贪婪会被它加入到黑名单.

# 交易

如下代码会构造一个交易(Transaction), 并使用私钥对该交易进行签名随后向 ropsten 测试网络发送该笔交易. 要测试如下代码, 需要填写上
`cSrcPrivKey` 与 `cSrcAddress` 两个变量, 并决定发送的 ETH 数量 `cAmount`.

```go
package main

import (
	"context"
	"encoding/hex"
	"log"
	"math/big"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/crypto"
	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/ethereum/go-ethereum/rpc"
)

var (
	cEthAddress = "https://ropsten.infura.io"
	cSrcPrivKey = "----------------------------------------------------------------"
	cSrcAddress = "0xeb1379888f6117386043b1e50aafa983006958d8"
	cDstAddress = "0x64ff867048064db76f2987445cc8909267855ec8"
	cAmount     = big.NewInt(5 * 1e14)
)

func sendETH(client *ethclient.Client, srcPriKeyHex, srcAddressHex, dstAddressHex string, amount *big.Int) error {
	srcAddress := common.HexToAddress(srcAddressHex)
	dstAddress := common.HexToAddress(dstAddressHex)
	srcPrivKeyBuf, err := hex.DecodeString(srcPriKeyHex)
	if err != nil {
		return err
	}
	srcPrivKey, err := crypto.ToECDSA(srcPrivKeyBuf)
	if err != nil {
		return err
	}
	nonce, err := client.NonceAt(context.Background(), srcAddress, nil)
	if err != nil {
		return err
	}
	gasPrice, err := client.SuggestGasPrice(context.Background())
	if err != nil {
		return err
	}
	tx := types.NewTransaction(nonce, dstAddress, amount, uint64(21000), gasPrice, []byte{})
	signer := types.HomesteadSigner{}
	sig, err := crypto.Sign(signer.Hash(tx).Bytes(), srcPrivKey)
	if err != nil {
		return err
	}
	signedTx, err := tx.WithSignature(signer, sig)
	if err != nil {
		return err
	}
	log.Println(signedTx.Hash().String())
	return client.SendTransaction(context.Background(), signedTx)
}

func main() {
	rpccli, err := rpc.Dial(cEthAddress)
	if err != nil {
		log.Fatalln(err)
	}
	client := ethclient.NewClient(rpccli)
	if err := sendETH(client, cSrcPrivKey, cSrcAddress, cDstAddress, cAmount); err != nil {
		log.Fatalln(err)
	}
}
```

为了读懂上述代码, 需要了解以下几个名词:

- Nonce: 每个账号的交易计数, 每进行一次成功交易则加一. nonce 存在的目的是为了保证交易顺序. nonce 的使用有如下几条规则:
	- 当 nonce 太小(小于之前已经有交易使用的 nonce 值), 交易会被直接拒绝.
	- 当 nonce 太大, 交易会暂时处于队列之中, 直到补齐开始 nonce 到目标 nonce 之间的所有交易.
	- 当复数个交易拥有相同 nonce 并均处于 pending 状态时, 只能成功执行一个交易.
- GasLimit: 你愿意花费多少单位 Gas 完成此交易. 一个普通交易的 GasLimit 是 21000. 如果交易中包含消息或交易本身是合约请求, 则 GasLimit 在 21000 的基础上动态增加. 如果交易不需要那么多 Gas, Ethereum 会將余下的 Gas 退回; 相反, 如果你给了 Gas 却不足够完成这个交易, 那么整个 Gas 会被消费掉并且拒绝该交易.
- GasPrice: 每单位 Gas 价值多少 Wei(1 ETH = 10^18 Wei). 矿工会优先打包 GasPrice 高的交易. 可以前往 [https://ethgasstation.info/](https://ethgasstation.info/) 查询当前合适的 GasPrice 价格.
