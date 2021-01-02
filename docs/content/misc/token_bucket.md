# 杂项/令牌桶算法限流

令牌桶算法最初来源于计算机网络. 在网络传输数据时, 为了防止网络拥塞, 需限制流出网络的流量, 使流量以比较均匀的速度向外发送. 令牌桶算法就实现了这个功能, 可控制发送到网络上数据的数目, 并允许突发数据的发送. 令牌桶算法是网络流量整形(Traffic Shaping)和速率限制(Rate Limiting)中最常使用的一种算法. 典型情况下, 令牌桶算法用来控制发送到网络上的数据的数目, 并允许突发数据的发送.

令牌桶以恒定的速率产生令牌. 传输数据需要消耗令牌. 依据数据量大小消耗等值数量的令牌. 控制令牌的生产速度即可进行网络速率限制.

## 代码实现

在 Go 语言中, 如果需要限制每单位时间的操作速度, 最便捷的方式是使用 time.Ticker, 但需要注意它只适用于每秒几十次操作的速率, 它和令牌桶模型几乎完全一致: 按照固定速率产生令牌. 下述代码实现了一个限制 I/O 速度的 CopyRate 函数.

```go
package copyrate

import (
	"io"
	"time"
)

func CopyRate(dst io.Writer, src io.Reader, bps int64) (written int64, err error) {
	throttle := time.NewTicker(time.Second)
	defer throttle.Stop()

	var n int64
	for {
		n, err = io.CopyN(dst, src, bps)
		if n > 0 {
			written += n
		}
		if err != nil {
			if err == io.EOF {
				err = nil
			}
			break
		}
		<-throttle.C // rate limit our flows
	}
	return written, err
}
```

测试: 复制文件且在复制过程中限制复制速度

```go
package main

import (
	"copyrate"
	"log"
	"os"
	"time"
)

func main() {
	src, err := os.Open("/tmp/foo.tar")
	if err != nil {
		log.Fatalln(err)
	}
	defer src.Close()

	dst, err := os.OpenFile("/tmp/bar.tar", os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0644)
	if err != nil {
		log.Fatalln(err)
	}
	defer dst.Close()

	tic := time.Now()
	n, err := copyrate.CopyRate(dst, src, 1024*1024*10)
	toc := time.Since(tic)
	log.Println(n, err, toc)
	// 2018/05/09 15:04:36 284989440 <nil> 27.0232635s
}
```

源文件大小是 271 MB, bps 限制为 10 M/S, 复制过程总耗时 27.02 S. 最后记得 md5sum 一下两份文件, 确认 CopyRate 函数逻辑正常:

```sh
$ md5sum foo.tar bar.tar
ff90c9f1d438f80ce6392ff5d79da463 foo.tar
ff90c9f1d438f80ce6392ff5d79da463 bar.tar
```

## 参考

- [1] Go: RateLimiting [https://github.com/golang/go/wiki/RateLimiting](https://github.com/golang/go/wiki/RateLimiting)
