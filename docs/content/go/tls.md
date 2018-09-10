# TLS

传输层安全协议(英语: Transport Layer Security, 缩写: TLS), 及其前身安全套接层(Secure Sockets Layer, 缩写: SSL)是一种安全协议, 目的是为互联网通信, 提供安全及数据完整性保障.

SSL 包含记录层(Record Layer)和传输层, 记录层协议确定传输层数据的封装格式. 传输层安全协议使用X.509认证, 之后利用非对称加密演算来对通信方做身份认证, 之后交换对称密钥作为会谈密钥(Session key). 这个会谈密钥是用来将通信两方交换的数据做加密, 保证两个应用间通信的保密性和可靠性, 使客户与服务器应用之间的通信不被攻击者窃听.

# 生成 TLS 私钥与公钥

```sh
# 生成 CA 私钥
openssl genrsa -out ca.key 2048
# 生成 CA 证书
openssl req -x509 -new -key ca.key -days 36525 -out ca.crt

# 生成服务端私钥
openssl genrsa -out server.key 2048
# 生成服务端签名请求
openssl req -new -key server.key -subj "/CN=host" -out server.csr
# 使用 CA 对服务端签名请求进行签名, 并生成服务端证书
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 36525

# 生成客户端私钥
openssl genrsa -out client.key 2048
# 生成客户端签名请求
openssl req -new -key client.key -out client.csr
# 使用 CA 对客户端签名请求进行签名, 并生成客户端证书
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 36525
```

# 服务端验证

```go
// server
package main

import (
	"bufio"
	"crypto/tls"
	"log"
	"net"
)

func serv(conn net.Conn) {
	defer conn.Close()
	r := bufio.NewReader(conn)
	for {
		line, err := r.ReadString('\n')
		if err != nil {
			log.Println(err)
			break
		}
		log.Println("Receive:", line[:len(line)-1])
	}
}

func main() {
	cert, err := tls.LoadX509KeyPair("server.crt", "server.key")
	if err != nil {
		log.Fatalln(err)
	}

	conf := &tls.Config{Certificates: []tls.Certificate{cert}}
	ln, err := tls.Listen("tcp", ":8080", conf)
	if err != nil {
		log.Fatalln(err)
	}
	defer ln.Close()
	log.Println("Listen and server on :8080")

	for {
		conn, err := ln.Accept()
		if err != nil {
			log.Println(err)
			continue
		}
		go serv(conn)
	}
}
```

```go
// client
package main

import (
	"crypto/tls"
	"fmt"
	"log"
	"time"
)

func main() {
	conf := &tls.Config{
		InsecureSkipVerify: true,
	}
	conn, err := tls.Dial("tcp", "localhost:8080", conf)
	if err != nil {
		log.Fatalln(err)
	}
	defer conn.Close()

	for _ = range time.NewTicker(time.Second).C {
		conn.Write([]byte(fmt.Sprintf("%d", time.Now().UnixNano())))
		conn.Write([]byte("\n"))
	}
}
```

注意客户端配置 `InsecureSkipVerify` 用来控制客户端是否校验证书安全性. 默认情况下, 客户端会检查服务端证书域名与真实请求域名是否一致. 设置为 true 则跳过检查. 这可能导致中间人攻击, 因此该设置仅应在测试过程中置为 true.

# 服务端验证-安全模式

不配置 `InsecureSkipVerify`, 客户端必须信任 CA 证书(或服务端证书):

```go
// client
package main

import (
	"crypto/tls"
	"crypto/x509"
	"fmt"
	"io/ioutil"
	"log"
	"time"
)

func main() {
	caCert, err := ioutil.ReadFile("ca.crt")
	if err != nil {
		log.Fatalln(err)
	}
	caCertPool := x509.NewCertPool()
	caCertPool.AppendCertsFromPEM(caCert)

	conf := &tls.Config{
		RootCAs: caCertPool,
	}
	conn, err := tls.Dial("tcp", "localhost:8080", conf)
	if err != nil {
		log.Fatalln(err)
	}
	defer conn.Close()

	for _ = range time.NewTicker(time.Second).C {
		conn.Write([]byte(fmt.Sprintf("%d", time.Now().UnixNano())))
		conn.Write([]byte("\n"))
	}
}
```


# 客户端验证

有时候, 服务端需要验证客户端身份, 以保证不是每个拿到服务端公钥的客户端都可以连接(服务端公钥在传播过程中泄露是难免的). 此时, 服务端需要验证客户端公钥.

```go
// server
package main

import (
	"bufio"
	"crypto/tls"
	"crypto/x509"
	"io/ioutil"
	"log"
	"net"
)

func serv(conn net.Conn) {
	defer conn.Close()
	r := bufio.NewReader(conn)
	for {
		line, err := r.ReadString('\n')
		if err != nil {
			log.Println(err)
			break
		}
		log.Println("Receive:", line[:len(line)-1])
	}
}

func main() {
	cert, err := tls.LoadX509KeyPair("server.crt", "server.key")
	if err != nil {
		log.Fatalln(err)
	}
	certBytes, err := ioutil.ReadFile("ca.crt")
	if err != nil {
		log.Fatalln(err)
	}
	clientCertPool := x509.NewCertPool()
	clientCertPool.AppendCertsFromPEM(certBytes)
	conf := &tls.Config{
		Certificates: []tls.Certificate{cert},
		ClientAuth:   tls.RequireAndVerifyClientCert,
		ClientCAs:    clientCertPool,
	}
	ln, err := tls.Listen("tcp", ":8080", conf)
	if err != nil {
		log.Fatalln(err)
	}
	defer ln.Close()
	log.Println("Listen and server on :8080")

	for {
		conn, err := ln.Accept()
		if err != nil {
			log.Println(err)
			continue
		}
		go serv(conn)
	}
}
```

```go
// client
package main

import (
	"crypto/tls"
	"crypto/x509"
	"fmt"
	"io/ioutil"
	"log"
	"time"
)

func main() {
	cert, err := tls.LoadX509KeyPair("client.crt", "client.key")
	if err != nil {
		log.Fatalln(err)
	}
	caCert, err := ioutil.ReadFile("ca.crt")
	if err != nil {
		log.Fatalln(err)
	}
	caCertPool := x509.NewCertPool()
	caCertPool.AppendCertsFromPEM(caCert)
	conf := &tls.Config{
		Certificates: []tls.Certificate{cert},
		RootCAs:      caCertPool,
	}
	conn, err := tls.Dial("tcp", "localhost:8080", conf)
	if err != nil {
		log.Fatalln(err)
	}
	defer conn.Close()

	for _ = range time.NewTicker(time.Second).C {
		conn.Write([]byte(fmt.Sprintf("%d", time.Now().UnixNano())))
		conn.Write([]byte("\n"))
	}
}
```

# 问题记录

## 如何签名 IP 地址?

在生成服务端公钥过程中, 将 IP 地址填入 `Common Name` 是无效的(此字段必须域名), 正确做法是:

```sh
# 复制 openssl.conf
cp /etc/pki/tls/openssl.cnf .

# 修改以下配置
[ v3_ca ]
subjectAltName=@alternate_names

# 并增加以下新区块
[ alternate_names ]
DNS.1      = localhost
DNS.2      = ...
IP.1       = 127.0.0.1
IP.2       = ...
```

```sh
# 生成 CA 私钥
openssl genrsa -out ca.key 2048
# 生成 CA 证书
openssl req -x509 -new -key ca.key -days 36525 -out ca.crt -config openssl.cnf

# 生成服务端私钥
openssl genrsa -out server.key 2048
# 生成服务端签名请求
openssl req -new -key server.key -out server.csr -config openssl.cnf
# 使用 CA 对服务端签名请求进行签名, 并生成服务端证书
openssl x509 -req -in server.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out server.crt -days 36525 -extfile openssl.cnf -extensions v3_ca

# 生成客户端私钥
openssl genrsa -out client.key 2048
# 生成客户端签名请求
openssl req -new -key client.key -out client.csr
# 使用 CA 对客户端签名请求进行签名, 并生成客户端证书
openssl x509 -req -in client.csr -CA ca.crt -CAkey ca.key -CAcreateserial -out client.crt -days 36525
```
