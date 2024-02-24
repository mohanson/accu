# CKB/以太坊 RPC 接口使用

本文的目的是编写相关代码, 从以太坊节点获取我们感兴趣的链上数据. 鉴于目前同步一个以太坊节点过于耗时, 因此我将使用 [Infura](https://www.infura.io/zh) 提供的公共以太坊节点来完成这一切. 那么我们开始吧!

```sh
$ go get -u -v github.com/ethereum/go-ethereum/ethclient
```

## 查询转账记录

以太坊交易数据中并不包含发送者, 要从交易中恢复发送者的地址, 可参考以下两个网页. 简单来说, 我们须首先从交易的签名中恢复发送者的公钥, 然后通过发送者公钥计算发送者地址.

- <https://github.com/ethereum/go-ethereum/issues/22918>
- <https://ethereum.stackexchange.com/questions/67449/given-a-raw-transaction-how-to-get-senders-address>

```go
package main

import (
	"context"
	"log"
	"math/big"

	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/ethereum/go-ethereum/rpc"
	"github.com/godump/doa"
)

func main() {
	// Site: https://www.infura.io/zh
	// Docs: https://docs.infura.io/networks/ethereum/json-rpc-methods
	rawClient := doa.Try(rpc.DialHTTP("https://mainnet.infura.io/v3/5c17ecf14e0d4756aa81b6a1154dc599"))
	ethClient := ethclient.NewClient(rawClient)
	blockNumber := doa.Try(ethClient.BlockNumber(context.Background()))
	block := doa.Try(ethClient.BlockByNumber(context.Background(), big.NewInt(int64(blockNumber))))
	for _, tx := range block.Transactions() {
		from := doa.Try(types.Sender(types.LatestSignerForChainID(tx.ChainId()), tx))
		value, _ := tx.Value().Float64()
		log.Printf("%s %s -> %s %10.6f eth", tx.Hash(), from, tx.To(), value/1e18)
	}
}
```

程序将获取以太坊最后一个交易区块, 并依次打印交易哈希, 交易发送者, 交易接收者和交易金额.

## 查询 USDT-ERC20 转账记录

Tether USD 在以太坊上是一个 ERC20 Token, 可以在 [Etherscan](https://etherscan.io/address/0xdac17f958d2ee523a2206206994597c13d831ec7) 查询该合约的完整信息. 我们通过解析交易的 Log 来查询 USDT 转账记录, 代码如下.

```go
package main

import (
	"context"
	"log"
	"math/big"

	"github.com/ethereum/go-ethereum"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/ethereum/go-ethereum/rpc"
	"github.com/godump/doa"
)

func main() {
	rawClient := doa.Try(rpc.DialHTTP("https://mainnet.infura.io/v3/5c17ecf14e0d4756aa81b6a1154dc599"))
	ethClient := ethclient.NewClient(rawClient)
	blockNumber := doa.Try(ethClient.BlockNumber(context.Background()))
	query := ethereum.FilterQuery{
		Addresses: []common.Address{common.HexToAddress("0xdac17f958d2ee523a2206206994597c13d831ec7")},
		Topics: [][]common.Hash{
			{common.HexToHash("0xddf252ad1be2c89b69c2b068fc378daa952ba7f163c4a11628f55a4df523b3ef")},
		},
		FromBlock: big.NewInt(int64(blockNumber)),
		ToBlock:   big.NewInt(int64(blockNumber)),
	}
	txlog := doa.Try(ethClient.FilterLogs(context.Background(), query))
	for _, e := range txlog {
		amount := new(big.Int)
		amount.SetBytes(e.Data)
		valuef, _ := amount.Float64()
		log.Printf("%s %s -> %s %14.6f USDT",
			e.TxHash,
			common.HexToAddress(e.Topics[1].Hex()),
			common.HexToAddress(e.Topics[2].Hex()),
			valuef/1e6,
		)
	}
}
```

## 查询 USDT 余额

我们还是以 USDT 合约为例, 我们的目标是查询 `F977814e90dA44bFA03b6295A0616a897441aceC` 这个地址的余额. 通过 USDT 合约代码可知, 有一个 `balanceOf(address)` 函数可以取得任意地址的余额, 因此我们只需要想办法调用这个函数即可.

要调用函数, 首先要获取函数的签名. 以 `balanceOf(address)` 为例, 其函数签名为 `70a08231`, 签名计算方式为 `sha3("balanceOf(address)")` 的前 4 个 Byte 的 Hex 值. 之后构建函数调用, 其构造方式为函数签名 + 参数. 注意所有参数都需要以 uint256 表示, 因此结果为 `70a08231000000000000000000000000F977814e90dA44bFA03b6295A0616a897441aceC`.

```go
package main

import (
	"context"
	"encoding/hex"
	"log"
	"math/big"

	"github.com/ethereum/go-ethereum"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/ethereum/go-ethereum/rpc"
	"github.com/godump/doa"
)

func main() {
	rawClient := doa.Try(rpc.DialHTTP("https://mainnet.infura.io/v3/5c17ecf14e0d4756aa81b6a1154dc599"))
	ethClient := ethclient.NewClient(rawClient)
	blockNumber := doa.Try(ethClient.BlockNumber(context.Background()))
	contract := common.HexToAddress("0xdAC17F958D2ee523a2206206994597C13D831ec7")
	ret := doa.Try(ethClient.CallContract(context.Background(), ethereum.CallMsg{
		To:   &contract,
		Data: doa.Try(hex.DecodeString("70a08231000000000000000000000000F977814e90dA44bFA03b6295A0616a897441aceC")),
	}, big.NewInt(int64(blockNumber))))
	balance := big.Int{}
	balance.SetBytes(ret)
	data, _ := balance.Float64()
	log.Println(data / 1e6)
}
```

## 查询随机地址余额

现在让我们来写一个彩票程序. 随机生成新的私钥, 并查询该私钥对应的地址的余额. 如果我们运气棒棒哒, 说不定能碰撞出一个有币的私钥捏~

```go
package main

import (
	"context"
	"log"
	"math/big"
	"net/rpc"

	"github.com/ethereum/go-ethereum/crypto"
	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/godump/doa"
)

func main() {
	rawClient := doa.Try(rpc.DialHTTP("https://mainnet.infura.io/v3/5c17ecf14e0d4756aa81b6a1154dc599"))
	ethClient := ethclient.NewClient(rawClient)
	for {
		pri := doa.Try(crypto.GenerateKey())
		pub := pri.PublicKey
		adr := crypto.PubkeyToAddress(pub)
		val := doa.Try(ethClient.BalanceAt(context.Background(), adr, nil))
		log.Println(adr, val)
		if val.Cmp(big.NewInt(0)) != 0 {
			break
		}
	}
}
```
