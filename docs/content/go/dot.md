# Go/DNS over TLS

DNS over TLS(DoT) 是一种用于加密域名解析流量的安全协议, 旨在提高互联网连接的隐私和安全性. 它解决了传统的 DNS(Domain Name System) 协议在传输过程中可能存在的安全问题, 例如数据泄露和劫持.

传统的 DNS 协议是明文的, 这意味着当你的设备进行域名解析时, 发送的数据包含了你要访问的网站的信息, 这可能被第三方监视和截取. DNS over TLS 通过在 DNS 查询和响应的传输中加入传输层安全性(TLS)加密来解决这个问题, 从而保护了数据的隐私和完整性.

## 代码实现

以下代码分别实现了 DNS Resolver 和 DoT Resolver.

```go
package main

import (
	"context"
	"crypto/tls"
	"log"
	"net"
	"time"
)

func ResolverDns(addr string) *net.Resolver {
	return &net.Resolver{
		PreferGo: true,
		Dial: func(ctx context.Context, network, address string) (net.Conn, error) {
			d := net.Dialer{
				Timeout: time.Second * 8,
			}
			return d.DialContext(ctx, "udp", addr)
		},
	}
}

func ResolverDot(addr string) *net.Resolver {
	host, _, _ := net.SplitHostPort(addr)
	conf := &tls.Config{
		ServerName:         host,
		ClientSessionCache: tls.NewLRUClientSessionCache(32),
	}
	return &net.Resolver{
		PreferGo: true,
		Dial: func(context context.Context, network, address string) (net.Conn, error) {
			d := net.Dialer{
				Timeout: time.Second * 8,
			}
			c, err := d.DialContext(context, "tcp", addr)
			if err != nil {
				return nil, err
			}
			_ = c.(*net.TCPConn).SetKeepAlive(true)
			_ = c.(*net.TCPConn).SetKeepAlivePeriod(10 * time.Minute)
			return tls.Client(c, conf), nil
		},
	}
}

func main() {
	dns := ResolverDns("1.1.1.1:53")
	log.Println(dns.LookupHost(context.Background(), "google.com"))
	dot := ResolverDot("1.1.1.1:853")
	log.Println(dot.LookupHost(context.Background(), "google.com"))
}
```

## 参考

- [1] [Specification for DNS over Transport Layer Security (TLS)](https://datatracker.ietf.org/doc/html/rfc7858)
- [2] [Cloudflare, 基于 HTTPS 的 DNS 和基于 TLS 的 DNS | 安全 DNS](https://www.cloudflare.com/zh-cn/learning/dns/dns-over-tls/)
- [3] [Cloudflare, DNS over TLS](https://www.cloudflare.com/zh-cn/learning/dns/dns-over-tls/)
