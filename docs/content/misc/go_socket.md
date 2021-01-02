# 杂项/Go Socket 编程

Socket 是一种操作系统提供的进程间通信机制. 在操作系统中, 通常会为应用程序提供一组应用程序接口, 称为套接字接口(Socket API). 注意的是, Socket API 本身不负责通信, 它仅提供基础函数供应用层调用, 底层通信一般由 TCP, Unix 或 UDP 实现.

## TCP

以下是一个简单的 TCP 服务与其配套客户端实现.

```go
// server.go
package main

import (
	"log"
	"net"
)

func main() {
	ln, err := net.Listen("tcp", ":3000")
	if err != nil {
		log.Fatalln(err)
	}
	defer ln.Close()
	for {
		conn, err := ln.Accept()
		if err != nil {
			log.Println(err)
			continue
		}

		go func(conn net.Conn) {
			defer conn.Close()
			var (
				n   int
				b   = make([]byte, 1024)
				err error
			)
			n, err = conn.Read(b)
			if err != nil {
				log.Println(err)
				return
			}
			log.Println(string(b[:n]))
			n, err = conn.Write([]byte("pong"))
			if err != nil {
				log.Println(err)
				return
			}
		}(conn)
	}
}
```

```go
// client.go
package main

import (
	"log"
	"net"
)

func main() {
	var (
		conn net.Conn
		b    = make([]byte, 1024)
		n    int
		err  error
	)

	conn, err = net.Dial("tcp", "127.0.0.1:3000")
	if err != nil {
		log.Fatalln(err)
	}
	defer conn.Close()

	_, err = conn.Write([]byte("ping"))
	if err != nil {
		log.Fatalln(err)
	}
	n, err = conn.Read(b)
	if err != nil {
		log.Fatalln(err)
	}
	log.Println(string(b[:n]))
}
```

## UNIX

Unix Socket 是 POSIX 操作系统里的一种组件. 它通过文件系统来实现 Socket 通信. 常见的 Unix Socket 文件有 mysql.sock, supervisor.sock 等, 它们均位于 `/var/run/` 目录下.

Go 中使用 Unix Socket 与 TCP Socket 的方法完全相同, 唯一区别是在 Listen 与 Dial 时, 参数 network 为 "unix", address 为文件路径, 如 "/var/run/accu.sock"

## UDP

```go
// server
package main

import (
	"log"
	"net"
)

func main() {
	var (
		conn *net.UDPConn
		addr *net.UDPAddr
		b    = make([]byte, 1024)
		n    int
		err  error
	)

	conn, err = net.ListenUDP("udp", &net.UDPAddr{IP: net.ParseIP("0.0.0.0"), Port: 3000})
	if err != nil {
		log.Fatalln(err)
	}
	defer conn.Close()

	for {
		n, addr, err = conn.ReadFromUDP(b)
		if err != nil {
			log.Println(err)
			continue
		}
		log.Println(addr, string(b[:n]))

		_, err = conn.WriteToUDP([]byte("pong"), addr)
		if err != nil {
			log.Println(err)
			continue
		}
	}
}
```

```go
//client
package main

import (
	"log"
    "net"
)

func main() {
	var (
		conn net.Conn
		b    = make([]byte, 1024)
		n    int
		err  error
	)

	conn, err = net.Dial("udp", "127.0.0.1:3000")
	if err != nil {
		log.Fatalln(err)
	}
	defer conn.Close()

	_, err = conn.Write([]byte("ping"))
	if err != nil {
		log.Fatalln(err)
	}
	n, err = conn.Read(b)
	if err != nil {
		log.Fatalln(err)
	}
	log.Println(string(b[:n]))
}
```
