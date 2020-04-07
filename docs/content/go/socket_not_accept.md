# Socket: 假如服务端不调用 Accept?

我相信绝大多数人都会写 TCP 的服务端代码, 就自己而言, 已经几乎机械式地在写如下代码(就如定式一般):

```go
ln, err := net.Listen("tcp", ":3000")
for {
    conn, err := ln.Accept()
    ...
}
```

Good! `conn` 对象到手! 之后便可以安心地从 conn 对象中读取数据, 或写入数据.

但是有没有考虑过一个问题, 如果在 Listen 后不调用 Accept, 会发生什么事? 这并非是无事找事的异想天开, 在现实中, 有很多种情况会导致代码 Accept 失败, 比如 `too many open files` 发生时.

# 实验开始

这是本次实验的服务端伪代码, 可以看到, 在 Listen 端口后, 代码只使用了一个循环 Sleep 将进程永久挂起.

```go
func main() {
	listen, err := net.Listen("tcp", ":3000")
	for {
		time.Sleep(time.Second)
	}
}
```

客户端伪代码主要执行三个步骤: 连接服务器, 等待 10 秒后向服务器发送数据, 关闭连接.

```go
func main() {
	conn, err := net.Dial("tcp", "127.0.0.1:3000")
    log.Println("Dial conn", conn, err)

    time.Sleep(time.Second * 10)

	n, err := io.WriteString(conn, "ping")
	log.Println("Write", n, "bytes,", "error is", err)

    err := conn.Close()
    log.Println("Close", err)
}
```

如此这般, 执行程序!

```text
2020/03/30 17:57:45 Dial conn &{{0xc0000a2080}}
2020/03/30 17:57:45 Write 4 bytes, error is <nil>
2020/03/30 17:57:45 Close <nil>
```

客户端连接服务器成功未报错, 发送数据成功未报错, 关闭连接成功亦未报错. 重新执行客户端代码, 这次让我们在执行的时候用 netstat 工具查看连接状态. 这里分为三个步骤.

**客户端连接到服务器后**

```text
tcp        0      0 127.0.0.1:56428         127.0.0.1:8080          ESTABLISHED 18063/client
tcp        0      0 127.0.0.1:8080          127.0.0.1:56428         ESTABLISHED -
```

**客户端调用 Close 后**

```text
tcp        0      0 127.0.0.1:56428         127.0.0.1:8080          FIN_WAIT2   -
tcp        5      0 127.0.0.1:8080          127.0.0.1:56428         CLOSE_WAIT  -
```

**客户端进程退出后**

```text
tcp        5      0 127.0.0.1:8080          127.0.0.1:56428         CLOSE_WAIT  -
```

注意最后的 CLOSE_WAIT, **它将永远存在, 直到服务端进程退出**.

# 原理分析

当客户端连接服务端后, 通过 netstat 看到连接状态为 ESTABLISHED, 这说明 TCP 三次握手已经成功, 也就是说 TCP 连接已经在网络上建立了起来. 可得知 TCP 握手并不是 Accept 函数的职责.

阅读操作系统的 Accept 函数文档: [http://man7.org/linux/man-pages/man2/accept.2.html](http://man7.org/linux/man-pages/man2/accept.2.html), 在第一段落中有如下描述:

> It extracts the first connection request on the queue of pending connections for the listening socket, sockfd, creates a new connected socket, and returns a new file descriptor referring to that socket.
>
> 翻译: 它从 connections 队列中取出第一个 connection, 并返回引用该 connection 的一个新的文件描述符.

验证了我的想法, 无论是否调用 Accept, connection 都已经建立起来了, Accept 只是将该 connection 包装成一个文件描述符, 供程序 Read, Write 和 Close. 那么关于第二步为什么客户端能 Write 成功就很容易解释了, 因为 connection 早已被建立(数据应该被暂存在服务端的接受缓冲区).

接着再分析 CLOSE_WAIT. 正常情况下 CLOSE_WAIT 在 TCP 挥手过程中持续时间极短, 如果出现则表明"被动关闭 TCP 连接的一方未调用 Close 函数". 观察下图的 TCP 挥手过程, 得知"即使被动关闭一方未调用 Close, 依然会响应 FIN 包发出 ACK 包", 因此主动关闭一方处于 FIN_WAIT2 是理所当然的.

```text
                              +---------+ ---------\      active OPEN
                              |  CLOSED |            \    -----------
                              +---------+<---------\   \   create TCB
                                |     ^              \   \  snd SYN
                   passive OPEN |     |   CLOSE        \   \
                   ------------ |     | ----------       \   \
                    create TCB  |     | delete TCB         \   \
                                V     |                      \   \
                              +---------+            CLOSE    |    \
                              |  LISTEN |          ---------- |     |
                              +---------+          delete TCB |     |
                   rcv SYN      |     |     SEND              |     |
                  -----------   |     |    -------            |     V
 +---------+      snd SYN,ACK  /       \   snd SYN          +---------+
 |         |<-----------------           ------------------>|         |
 |   SYN   |                    rcv SYN                     |   SYN   |
 |   RCVD  |<-----------------------------------------------|   SENT  |
 |         |                    snd ACK                     |         |
 |         |------------------           -------------------|         |
 +---------+   rcv ACK of SYN  \       /  rcv SYN,ACK       +---------+
   |           --------------   |     |   -----------
   |                  x         |     |     snd ACK
   |                            V     V
   |  CLOSE                   +---------+
   | -------                  |  ESTAB  |
   | snd FIN                  +---------+
   |                   CLOSE    |     |    rcv FIN
   V                  -------   |     |    -------
 +---------+          snd FIN  /       \   snd ACK          +---------+
 |  FIN    |<-----------------           ------------------>|  CLOSE  |
 | WAIT-1  |------------------                              |   WAIT  |
 +---------+          rcv FIN  \                            +---------+
   | rcv ACK of FIN   -------   |                            CLOSE  |
   | --------------   snd ACK   |                           ------- |
   V        x                   V                           snd FIN V
 +---------+                  +---------+                   +---------+
 |FINWAIT-2|                  | CLOSING |                   | LAST-ACK|
 +---------+                  +---------+                   +---------+
   |                rcv ACK of FIN |                 rcv ACK of FIN |
   |  rcv FIN       -------------- |    Timeout=2MSL -------------- |
   |  -------              x       V    ------------        x       V
    \ snd ACK                 +---------+delete TCB         +---------+
     ------------------------>|TIME WAIT|------------------>| CLOSED  |
                              +---------+                   +---------+
```

最后, 当客户端进程退出后, 客户端保留的 FIN_WAIT2 状态自然被释放, 但服务端由于未获得 connection 的文件描述符无法主动调用 Close 函数, 因此服务端的 CLOSE_WAIT 将一直持续直到服务端进程退出.

# 如何处理该类型 CLOSE_WAIT?

在本文的例子中, 服务端没有能力进行处理(代码中没有拿到 conn), 因为 connection 归操作系统管.

但是如果程序是因为 `too many open files` 等错误导致 Accept 失败, 那么当操作系统的文件描述符数量下降时 Accept 函数将可以成功, 因此应用程序可以拿到引用该 connection 的文件描述符, 在程序代码中按照正常逻辑 Close 掉该文件描述符即可释放该 connection.
