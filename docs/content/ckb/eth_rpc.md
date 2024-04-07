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
	"github.com/godump/doa"
)

func main() {
	// Site: https://www.infura.io/zh
	// Docs: https://docs.infura.io/networks/ethereum/json-rpc-methods
	ethClient := doa.Try(ethclient.Dial("https://mainnet.infura.io/v3/5c17ecf14e0d4756aa81b6a1154dc599"))
	blockNumber := doa.Try(ethClient.BlockNumber(context.Background()))
	block := doa.Try(ethClient.BlockByNumber(context.Background(), big.NewInt(int64(blockNumber))))
	for _, tx := range block.Transactions() {
		sender := doa.Try(types.Sender(types.LatestSignerForChainID(tx.ChainId()), tx))
		amount, _ := tx.Value().Float64()
		log.Printf("%s -> %s %14.6f", sender, tx.To(), amount/1e18)
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
	"github.com/godump/doa"
)

func main() {
	ethClient := doa.Try(ethclient.Dial("https://mainnet.infura.io/v3/5c17ecf14e0d4756aa81b6a1154dc599"))
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

要调用函数, 首先要获取函数的签名. 以 `balanceOf(address)` 为例, 其函数签名为 `70a08231`, 签名计算方式为 `sha3("balanceOf(address)")` 的前 4 个 Byte. 之后构建函数调用, 其构造方式为函数签名 + 参数. 注意所有参数都需要以 uint256 表示, 因此结果为 `70a08231000000000000000000000000F977814e90dA44bFA03b6295A0616a897441aceC`.

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
	"github.com/godump/doa"
)

func main() {
	ethClient := doa.Try(ethclient.Dial("https://mainnet.infura.io/v3/5c17ecf14e0d4756aa81b6a1154dc599"))
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
	"encoding/hex"
	"log"
	"math/big"

	"github.com/ethereum/go-ethereum/crypto"
	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/godump/doa"
)

func main() {
	ethClient := doa.Try(ethclient.Dial("https://mainnet.infura.io/v3/5c17ecf14e0d4756aa81b6a1154dc599"))
	for {
		pri := doa.Try(crypto.GenerateKey())
		pub := pri.PublicKey
		adr := crypto.PubkeyToAddress(pub)
		val, err := ethClient.BalanceAt(context.Background(), adr, nil)
		if err != nil {
			log.Println(err)
			continue
		}
		log.Println("0x"+hex.EncodeToString(crypto.FromECDSA(pri)), adr, val)
		if val.Cmp(big.NewInt(0)) != 0 {
			break
		}
	}
}
```

## 签名验签

以下示例代码使用 go-ethereum 提供的 secp256k1 实现, 对任意数据的哈希进行签名和验签.

```go
package main

import (
	"crypto/rand"
	"encoding/hex"
	"log"
	"slices"

	"github.com/ethereum/go-ethereum/crypto"
	"github.com/godump/doa"
)

func main() {
	prikey := doa.Try(crypto.HexToECDSA("0000000000000000000000000000000000000000000000000000000000000001"))
	pubkey := prikey.PublicKey

	log.Println("prikey", hex.EncodeToString(crypto.FromECDSA(prikey)))
	log.Println("pubkey", hex.EncodeToString(crypto.FromECDSAPub(&pubkey)))

	msg := make([]byte, 32)
	rand.Read(msg)
	log.Println("msg", hex.EncodeToString(msg))
	sig := doa.Try(crypto.Sign(msg, prikey))
	log.Println("sig", hex.EncodeToString(sig))

	doa.Doa(crypto.VerifySignature(crypto.FromECDSAPub(&pubkey), msg, sig[:64]))
	doa.Doa(slices.Equal(doa.Try(crypto.Ecrecover(msg, sig)), crypto.FromECDSAPub(&pubkey)))
}
```

```text
2024/03/26 15:35:16 prikey 0000000000000000000000000000000000000000000000000000000000000001
2024/03/26 15:35:16 pubkey 0479be667ef9dcbbac55a06295ce870b07029bfcdb2dce28d959f2815b16f81798483ada7726a3c4655da4fbfc0e1108a8fd17b448a68554199c47d08ffb10d4b8
2024/03/26 15:35:16 msg 73d811670c997143c797190087543f8cb16494ddd662ca247b721dde6248ab0b
2024/03/26 15:35:16 sig 8a5dad0cbf16771758662cf3cd6c94f3cc10980d98367762b419ccf23e0bae736dda0fe3908e68ccf1090568e7cabe3a0bfdd054477070c040c58de4baeec82001
```

## 交易转账

进行一笔转账交易. 下面的代码会向黑洞地址转账 1 ETH.

```go
package main

import (
	"context"
	"fmt"
	"math/big"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/crypto"
	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/godump/doa"
)

func main() {
	client := doa.Try(ethclient.Dial("https://mainnet.infura.io/v3/5c17ecf14e0d4756aa81b6a1154dc599"))
	prikey := doa.Try(crypto.HexToECDSA("")) // Private key without 0x-prefix
	pubkey := prikey.PublicKey
	addr := crypto.PubkeyToAddress(pubkey)

	nonce := doa.Try(client.PendingNonceAt(context.Background(), addr))
	value := big.NewInt(1000000000000000000) // In wei (1 eth)
	gasLimit := uint64(21000)                // In units
	gasPrice := doa.Try(client.SuggestGasPrice(context.Background()))
	recv := common.HexToAddress("0x0000000000000000000000000000000000000000")
	data := []byte{}

	id := doa.Try(client.NetworkID(context.Background()))
	tx := types.NewTransaction(nonce, recv, value, gasLimit, gasPrice, data)
	txSign := doa.Try(types.SignTx(tx, types.NewEIP155Signer(id), prikey))
	doa.Nil(client.SendTransaction(context.Background(), txSign))
	fmt.Println(txSign.Hash().Hex())
}
```

略微修改上述代码, 即可向目标地址转账全部可用余额:

```go
package main

import (
	"context"
	"fmt"
	"math/big"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/crypto"
	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/godump/doa"
)

func main() {
	client := doa.Try(ethclient.Dial("https://mainnet.infura.io/v3/5c17ecf14e0d4756aa81b6a1154dc599"))
	prikey := doa.Try(crypto.HexToECDSA("")) // Private key without 0x-prefix
	pubkey := prikey.PublicKey
	addr := crypto.PubkeyToAddress(pubkey)

	nonce := doa.Try(client.PendingNonceAt(context.Background(), addr))
	gasLimit := uint64(21000) // In units
	gasPrice := doa.Try(client.SuggestGasPrice(context.Background()))
	gasValue := big.NewInt(0).Mul(big.NewInt(int64(gasLimit)), gasPrice)
	whole := doa.Try(client.BalanceAt(context.Background(), addr, nil))
	value := big.NewInt(0).Sub(whole, gasValue)
	recv := common.HexToAddress("0x0000000000000000000000000000000000000000")
	data := []byte{}

	id := doa.Try(client.NetworkID(context.Background()))
	tx := types.NewTransaction(nonce, recv, value, gasLimit, gasPrice, data)
	txSign := doa.Try(types.SignTx(tx, types.NewEIP155Signer(id), prikey))
	doa.Nil(client.SendTransaction(context.Background(), txSign))
	fmt.Println(txSign.Hash().Hex())
}
```

## 发布合约

首先将以下 Solidity 代码编译到字节码. 这一步可以使用在线编译器, 例如 Remix. 将编译结果保存到本地 `storage` 文件.

```text
pragma solidity >=0.8.2 <0.9.0;

contract Storage {
    uint256 number;
    function set(uint256 num) public { number = num; }
    function get() public view returns (uint256){ return number; }
}
```

```go
package main

import (
	"context"
	"fmt"
	"math/big"
	"os"

	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/crypto"
	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/godump/doa"
)

func main() {
	client := doa.Try(ethclient.Dial("https://mainnet.infura.io/v3/5c17ecf14e0d4756aa81b6a1154dc599"))
	prikey := doa.Try(crypto.HexToECDSA("")) // Private key without 0x-prefix
	pubkey := prikey.PublicKey
	addr := crypto.PubkeyToAddress(pubkey)

	gasLimit := uint64(3000000)
	gasPrice := doa.Try(client.SuggestGasPrice(context.Background()))
	value := big.NewInt(0)
	nonce := doa.Try(client.PendingNonceAt(context.Background(), addr))
	data := doa.Try(os.ReadFile("storage"))

	id := doa.Try(client.NetworkID(context.Background()))
	tx := types.NewContractCreation(nonce, value, gasLimit, gasPrice, data)
	txSign := doa.Try(types.SignTx(tx, types.NewEIP155Signer(id), prikey))
	doa.Nil(client.SendTransaction(context.Background(), txSign))
	fmt.Println(txSign.Hash().Hex())
	for {
		_, isp, err := client.TransactionByHash(context.Background(), txSign.Hash())
		if isp || err != nil {
			time.Sleep(time.Second)
			continue
		}
		break
	}
	cddr := doa.Try(client.TransactionReceipt(context.Background(), txSign.Hash())).ContractAddress
	fmt.Println(cddr)
}
```

## 执行合约

```go
package main

import (
	"context"
	"fmt"
	"math/big"

	"github.com/ethereum/go-ethereum"
	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/common/math"
	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/crypto"
	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/godump/doa"
	"golang.org/x/crypto/sha3"
)

func hash(data []byte) []byte {
	h := sha3.NewLegacyKeccak256()
	h.Write(data)
	return h.Sum(nil)
}

func main() {
	client := doa.Try(ethclient.Dial("https://mainnet.infura.io/v3/5c17ecf14e0d4756aa81b6a1154dc599"))
	prikey := doa.Try(crypto.HexToECDSA("")) // Private key without 0x-prefixkey without 0x-prefix
	pubkey := prikey.PublicKey
	addr := crypto.PubkeyToAddress(pubkey)
	dest := common.HexToAddress("0xa28aFDa14Be5789564aE5fA03665c4180e3c680b")

	gasLimit := uint64(3000000)
	gasPrice := doa.Try(client.SuggestGasPrice(context.Background()))
	value := big.NewInt(0)
	nonce := doa.Try(client.PendingNonceAt(context.Background(), addr))
	data := []byte{}
	data = append(data, hash([]byte("set(uint256)"))[:4]...)
	data = append(data, math.U256Bytes(big.NewInt(42))...)

	id := doa.Try(client.NetworkID(context.Background()))
	tx := types.NewTransaction(nonce, dest, value, gasLimit, gasPrice, data)
	txSign := doa.Try(types.SignTx(tx, types.NewEIP155Signer(id), prikey))
	doa.Nil(client.SendTransaction(context.Background(), txSign))
	fmt.Println(txSign.Hash().Hex())

	ret := doa.Try(client.CallContract(context.Background(), ethereum.CallMsg{
		To:   &dest,
		Data: hash([]byte("get()"))[:4],
	}, nil))
	fmt.Println(big.NewInt(0).SetBytes(ret))
}
```


## 本地开发节点搭建

```sh
$ git clone https://github.com/ethereum/go-ethereum --branch release/1.13
$ cd go-ethereum
$ make geth

$ geth --dev --http
$ geth attach /tmp/geth.ipc
> eth.sendTransaction({from: eth.accounts[0], to: '0x7e5f4552091a69125d5dfcb7b8c2659029395bdf', value: web3.toWei(10000, 'ether')})
```

```
0000000000000000000000000000000000000000000000000000000000000001 0x7e5f4552091a69125d5dfcb7b8c2659029395bdf
0000000000000000000000000000000000000000000000000000000000000002 0x2b5ad5c4795c026514f8317c7a215e218dccd6cf
```
