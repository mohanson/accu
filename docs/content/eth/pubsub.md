# 以太坊: 订阅通知

订阅/通知允许客户等待事件而不是轮询它们.

1. 通知是针对当前事件而不是针对过去事件发送的. 如果您的应用要求您不要错过任何通知, 那么订阅可能不是最佳选择.
2. 订阅需要全双工连接. go-ethereum 以 websockets 的形式提供这种连接(使用-ws启用)和ipc(默认启用).
3. 订阅连接到一个连接. 如果连接关闭, 则通过此连接创建的所有订阅都将被删除.
4. 通知存储在内部缓冲区中, 并从此缓冲区发送到客户端. 如果客户端无法跟上并且缓冲的通知数量达到限制(当前为10k), 则连接将关闭. 请记住, 订阅某些事件可能会导致大量通知. 例如在节点开始同步时侦听所有日志/块.

# 当前支持的订阅类型

## newHeads

每次将新的头部追加到区块链时都会触发通知, 包括区块链重组("区块链重组" 指的是节点发现一个新的难度最大的链, 该链否认了节点以前认为的难度最大的链. 这些被不信排除的块将变成叔块). 用户可以使用布隆过滤器来确定块是否包含对其感兴趣的日志.

在区块链重组的情况下, 订阅将发出新链的所有新头部. 因此, 订阅可以在同一高度上发出多个头部.

## logs

返回新导入块中包含的日志, 并匹配给定的过滤条件.

在区块链重组的情况下, 以前发送的旧链中的日志将被重新发送, 并将 `removed` 的属性设置为 true. 新链中的日志也将被发送. 因此订阅可以多次发出相同事务的日志.

## newPendingTransactions

返回所有添加到 `pending` 状态的交易.

## syncing

指示节点何时启动或停止同步.

## 示例代码

下示代码以订阅 `newHeads` 消息为例:

```go
package main

import (
	"context"
	"log"

	"github.com/ethereum/go-ethereum/core/types"
	"github.com/ethereum/go-ethereum/ethclient"
	"github.com/ethereum/go-ethereum/rpc"
)

func main() {
	rpccli, err := rpc.Dial("wss://ropsten.infura.io/ws")
	if err != nil {
		log.Fatalln(err)
	}
	client := ethclient.NewClient(rpccli)

	ch := make(chan *types.Header, 1024)
	sub, err := client.SubscribeNewHead(context.Background(), ch)
	if err != nil {
		log.Fatalln(err)
	}

	for {
		select {
		case hea := <-ch:
			log.Println(hea.Number.String(), hea.Hash().String())
		case err := <-sub.Err():
			log.Fatalln(err)
		}
	}
}
```

# 参考
- [1] ethereum: RPC PUB SUB [https://github.com/ethereum/go-ethereum/wiki/RPC-PUB-SUB](https://github.com/ethereum/go-ethereum/wiki/RPC-PUB-SUB)
