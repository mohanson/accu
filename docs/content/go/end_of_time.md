# 时间尽头

众所周知, 时间有多种存储方式, 其一是字符串形式, 例如在 HTTP 协议中使用的 RFC1123 格式, 时间就被保存为形如 `Thu, 01 Jan 1970 08:00:00 CST` 的字符串. 其二是使用二进制形式保存, 例如在比特币协议中就使用 4 字节(即 uint32) 保存时间. 使用二进制形式保存时间能极大降低占用空间并加快解析速度, 缺点则是对人类不友好. 但使用二进制形式保存时间有一个重要的问题: 4 字节(uint32) 或 8 字节(uint64) 能保存的时间范围是有限的.

# 开始探索

在开始探讨时间的尽头之前, 先来了解一下整数到二进制的转换. 我们以最大的 uint32 数字 4294967295 举例, 可以通过如下的简单计算过程将之转换为 4 字节 bytes([255, 255, 255, 255]), 其 go 代码如下:

```go
package main

import "fmt"

func main() {
	max := 2<<31 - 1
	buf := make([]byte, 4)
	buf[0] = byte(max >> 24 % 256)
	buf[1] = byte(max >> 16 % 256)
	buf[2] = byte(max >> 8 % 256)
	buf[3] = byte(max % 256)
	fmt.Println(buf)
	// [255 255 255 255]
}
```

可以使用 `encoding/binary` 包简化上述计算:

```go
package main

import (
	"encoding/binary"
	"fmt"
)

func main() {
	var max uint32 = 2<<31 - 1
	buf := make([]byte, 4)

	// uint32 到 4 字节
	binary.BigEndian.PutUint32(buf, max)
	fmt.Println("bin:", buf)

	// 4 字节到 uint32
	r := binary.BigEndian.Uint32([]byte{0xFF, 0xFF, 0xFF, 0xFF})
	fmt.Println("int:", r)
}
```

这里要提一下的是 `binary.BigEndian` 表示的是 `大端序`, 即高位字节在地址低位. 与之相反的还有一个 `小端序`. 目前来说大端序应用较为广泛. 可见本节参考.

# 终点

现在我们已经知道了 4 字节所能存储的最大整数是 4294967295, 同时该整数所代表的日期是:

```go
end := time.Unix(int64(2<<31-1), 0)
// 2106-02-07 14:28:15 +0800 CST
```

没错, 记得在 `2106-02-07 14:28:15 +0800 CST` 之前抛掉你手中的所有比特币(手动滑稽). 由于时间溢出引发的 BUG 最知名的应该是千年虫事件了, 虽然该事件已经过去, 但未来必定会再次发生, 有很大可能就是在 2106 年, 因为我们不知道除了比特币之外, 还有哪些软件也使用了 4 字节时间. 本次探索给我的教训是: **不要使用 uint32 保存时间**.

# 参考
- [1] 维基: 字节序 [https://zh.wikipedia.org/wiki/%E5%AD%97%E8%8A%82%E5%BA%8F](https://zh.wikipedia.org/wiki/%E5%AD%97%E8%8A%82%E5%BA%8F)
- [2] 维基: 千年虫 [https://zh.wikipedia.org/zh-hans/2000%E5%B9%B4%E9%97%AE%E9%A2%98](https://zh.wikipedia.org/zh-hans/2000%E5%B9%B4%E9%97%AE%E9%A2%98)
