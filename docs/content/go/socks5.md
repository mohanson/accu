根据 RFC1928 协议, 简单实现了无加密的 SOCKS Version 5 服务器.

RFC1928 中文翻译(简翻): [/content/net_rfc1928_socks5/](/content/net_rfc1928_socks5/)

```go
package main

import (
	"bufio"
	"flag"
	"io"
	"log"
	"net"
	"strconv"
)

var flBind = flag.String("b", "0.0.0.0:1080", "bind address")

func serv(conn net.Conn) {
	connl := conn
	defer connl.Close()
	connlreader := bufio.NewReader(connl)

	var b byte
	var p []byte
	var err error

	p = make([]byte, 2)
	_, err = io.ReadFull(connlreader, p)
	if err != nil || p[0] != 0x05 {
		return
	}
	_, err = connlreader.Discard(int(p[1]))
	if err != nil {
		return
	}
	_, err = connl.Write([]byte{0x05, 0x00})
	if err != nil {
		return
	}

	p = make([]byte, 4)
	_, err = io.ReadFull(connlreader, p)
	if err != nil || p[0] != 0x05 {
		return
	}

	var addr string
	switch p[3] {
	case 0x01:
		p = make([]byte, 4)
		_, err = io.ReadFull(connlreader, p)
		if err != nil {
			return
		}
		addr = net.IPv4(p[0], p[1], p[2], p[3]).String()
	case 0x03:
		b, err = connlreader.ReadByte()
		if err != nil {
			return
		}
		p = make([]byte, b)
		_, err = io.ReadFull(connlreader, p)
		if err != nil {
			return
		}
		addr = string(p)
	case 0x04:
		p = make([]byte, 16)
		_, err = io.ReadFull(connlreader, p)
		if err != nil {
			return
		}
		addr = net.IP(p).String()
	}

	p = make([]byte, 2)
	_, err = io.ReadFull(connlreader, p)
	if err != nil {
		return
	}
	addr = addr + ":" + strconv.Itoa(int(p[0])<<8|int(p[1]))
	log.Println("Accept", addr)

	connr, err := net.Dial("tcp", addr)
	if err != nil {
		return
	}
	defer connr.Close()
	connl.Write([]byte{0x05, 0x00, 0x00, 0x01, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00})

	go func() {
		io.Copy(connr, connl)
		connr.Close()
		connl.Close()
	}()
	io.Copy(connl, connr)
	connr.Close()
	connl.Close()
}

func main() {
	flag.Parse()
	log.SetFlags(log.LstdFlags | log.Lshortfile)

	ln, err := net.Listen("tcp", *flBind)
	if err != nil {
		log.Fatalln(err)
	}
	defer ln.Close()
	log.Println("Listen and server on", *flBind)

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
