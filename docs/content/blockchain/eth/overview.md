# 以太坊: 概览

以太坊当前有多种语言实现的版本, 其中 `go-ethereum` 最为流行. 按照

[https://github.com/ethereum/go-ethereum](https://github.com/ethereum/go-ethereum)

说明进行安装.

# 节点

以太节点是一个令人头疼的问题:

- 它需要大容量 SSD 硬盘. 截至 2018-06-22 日, 以太节点大小是 108G. 这意味着, 考虑到未来的增长您至少需要 256G 的 SSD 硬盘. 另外, 请不要考虑使用机械硬盘, 现阶段一个节点平均每秒要修改 leveldb 数据库 200~300 次, 已经超出机械硬盘 IO 上限, 这意味着您永远无法完成同步.
- 它需要科学上网. 访问国际互联网, 并等待 2 天左右时间完成节点同步.

如果不具备自己搭建节点的能力, 可以暂时先**使用别人的节点**. infura 提供了安全和可靠以太坊节点访问方式.

访问 [https://infura.io/](https://infura.io/) 以了解更多.

> 以太坊当前存在一条主链(mainnet)和众多测试链(ropsten, kovan, rinkeby 等), 主链与测试链的区别在于主链上的 ETH 有价值而测试链没有. 造成这样区别的根本原因是共识算法不同: 主链采用 POW 共识, 这意味着矿工需要投入真金白银的算力和电费; 测试链采用 POA 共识, 区块打包奖励会定向分配给指定的账户而不需要这些账户投入任何资源.

# 万事俱备

是时候在以太链上游玩一番了! 下面的代码演示了如何获取一个地址的余额.

```go
package main

import (
	"context"
	"log"

	"github.com/ethereum/go-ethereum/common"
	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/ethereum/go-ethereum/rpc"
)

func main() {
	rpccli, err := rpc.Dial("https://ropsten.infura.io")
	if err != nil {
		log.Fatalln(err)
	}
	client := ethclient.NewClient(rpccli)

	r, err := client.BalanceAt(
		context.Background(),
		common.HexToAddress("0x0000000000000000000000000000000000000000"),
		nil,
	)
	if err != nil {
		log.Fatalln(err)
	}
	log.Println(r)
}
```

```
2018/06/22 17:26:14 6555308156958657908334
```

大约是 6555 个以太. 你可以前往 [etherscan](https://ropsten.etherscan.io/address/0x0000000000000000000000000000000000000000) 验证.

> ETH 地址以 0x 开头, 长度为 40 的 16 进制字符串. 0x0000000000000000000000000000000000000000 是一个比较有趣的地址, 因为它是 ETH 默认挖矿地址导致在早期部分矿工直接挖到块后奖励进了该地址; 同时该地址当前无人知道其私钥, 因此部分合约通过将 ETH 转账到该地址以模拟 "销毁" 功能.

> ETH 拥有 18 位小数, 因此 6555308156958657908334 / 10 ** 18 = 6555
