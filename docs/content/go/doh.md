# Go/DNS over HTTPS

DNS over HTTPS(DoH) 与 DoT 两者都基于传输层安全性(TLS), TLS 也用于保护您与使用 HTTPS 的网站之间的通信. DoH 与 DoT 的区别在于, 其额外使用了应用层协议 HTTPS.

## 代码实现

以下代码实现了 DoH Resolver. 相比较 DoT 而言, 稍微复杂一点. 每一个 DNS 请求都包含 size(uint16) 与 DNS wire data, 我们只需要将 DNS wire data 以 POST 方法发送到远端服务器并接受服务器响应. 服务器响应同样包含一个 size(uint16) 与 DNS wire data, 其中只有 wire data 是我们需要的, 将其写入 Conn 的缓冲区即可.

DNS wire format 可参考此 RFC: <https://datatracker.ietf.org/doc/html/rfc1035>.

```go
package main

import (
	"bytes"
	"context"
	"encoding/binary"
	"io"
	"log"
	"net"
	"net/http"
	"net/url"
	"time"

	"github.com/godump/doa"
)

// Cdoh structure can be used for DoH protocol processing.
type Cdoh struct {
	Server string
	Buffer *bytes.Buffer
}

func (c Cdoh) Read(b []byte) (n int, err error)   { return c.Buffer.Read(b) }
func (c Cdoh) Close() error                       { return nil }
func (c Cdoh) LocalAddr() net.Addr                { return nil }
func (c Cdoh) RemoteAddr() net.Addr               { return nil }
func (c Cdoh) SetDeadline(t time.Time) error      { return nil }
func (c Cdoh) SetReadDeadline(t time.Time) error  { return nil }
func (c Cdoh) SetWriteDeadline(t time.Time) error { return nil }
func (c Cdoh) Write(b []byte) (n int, err error) {
	size := int(binary.BigEndian.Uint16(b[:2]))
	doa.Doa(size == len(b)-2)
	resp, err := http.Post(c.Server, "application/dns-message", bytes.NewReader(b[2:]))
	if err != nil {
		log.Println("main:", err)
		return len(b), nil
	}
	body, err := io.ReadAll(resp.Body)
	if err != nil {
		return len(b), nil
	}
	data := make([]byte, 2+len(body))
	binary.BigEndian.PutUint16(data[:2], uint16(len(body)))
	copy(data[2:], body)
	c.Buffer.Write(data)
	return len(b), nil
}

// ResolverDoh returns a DoH resolver. For further information, see https://datatracker.ietf.org/doc/html/rfc8484.
func ResolverDoh(addr string) *net.Resolver {
	urls := doa.Try(url.Parse(addr))
	urls.Host = doa.Try(net.LookupHost(urls.Hostname()))[0]
	return &net.Resolver{
		PreferGo: true,
		Dial: func(ctx context.Context, network, address string) (net.Conn, error) {
			conn := &Cdoh{
				Server: urls.String(),
				Buffer: bytes.NewBuffer([]byte{}),
			}
			return conn, nil
		},
	}
}

func main() {
	net.DefaultResolver = ResolverDoh("https://1.1.1.1/dns-query")
	log.Println(net.LookupHost("google.com"))
}
```

## 参考

- [1] [Specification for DNS over Transport Layer Security (TLS)](https://datatracker.ietf.org/doc/html/rfc8484)
