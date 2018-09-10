# RFC1928: SOCKS Protocol Version 5

# 介绍

使用网络防火墙, 系统可以有效地将内部网络从外部网络结构(比如正变得越来越受欢迎的 INTERNET)中隔离出来. 这些防火墙系统通常充当应用程序层网关网络, 提供受控的 TELNET、FTP 和 SMTP 访问. 随着更复杂的应用层协议的出现, 为了便于全球信息检索, 存在需要为这些协议提供一个通用框架来透明和安全地穿过防火墙.

此处描述的协议旨在提供一个框架, 为 TCP 和 UDP 协议中的客户端-服务器应用程序方便, 安全地使用网络防火墙的服务. 该协议在概念上是应用程序之间的 "中介层" 和传输层, 并因此不提供网络层网关服务, 如发送 ICMP 消息.

相比起 SOCKS Version 4, SOCKS Version 5 提供了 UDP 和 IPV6 支持.

NOTE: 除非另行说明, 否则后续出现的数字全部为 16 进制字节.

# 客户端

当 TCP 客户端希望通过防火墙建立与远程对象的链接时, 它必须打开一个 TCP 连接到 SOCKS 服务. SOCKS 服务通常位于 TCP 端口 1080 上. 如果连接请求成功, 客户端输入要使用的身份验证方法, 并使用所选的方法, 发送一个中继请求. SOCKS 服务器评估请求, 建立适当的连接或拒绝它.

当客户端连接至 SOCKS 服务器, 发送一个包含版本和验证方法的消息:


VER | NMETHODS | METHODS
----| -------- | --------
1   | 1        | 1 to 255


- VER 是 SOCKS 版本, 这里应该是0x05
- NMETHODS 是 METHODS 部分的字节长度
- METHODS 是客户端支持的认证方式列表, 每个方法占 1 字节. 当前的定义是：
    - 0x00 不需要认证
    - 0x01 GSSAPI
    - 0x02 用户名、密码认证
    - 0x03 0x7F由IANA分配（保留）
    - 0x80 0xFE为私人方法保留
    - 0xFF 无可接受的方法


服务器从客户端提供的方法中选择一个并通过以下消息通知客户端:

VER | METHODS
----| -------
1   | 1

如果返回 0xFF 表示没有一个认证方法被选中, 客户端需要关闭连接.

# 请求

SOCKS 请求格式:

VER | CMD |	RSV  | ATYP | DST.ADDR | DST.PORT
--- | --- | ---- | ---- | -------- | --------
1   | 1   | 0x00 | 1    | Variable | 2


- VER是 SOCKS 版本, 这里应该是0x05
- CMD是 SOCK 的命令码
    - 0x01 表示 CONNECT 请求
    - 0x02 表示 BIND 请求
    - 0x03 表示 UDP 转发
- RSV 0x00 保留
- ATYP DST.ADDR 类型
    - 0x01 IPv4地址, DST.ADDR 部分 4 字节长度
    - 0x03 域名, DST.ADDR 部分第一个字节为域名长度, DST.ADDR 剩余的内容为域名, 没有\0结尾
    - 0x04 IPv6地址, 16个字节长度
- DST.ADDR 目的地址
- DST.PORT 网络字节序表示的目的端口

服务器按以下格式回应客户端的请求:

VER | REP | RSV  | ATYP | BND.ADDR | BND.PORT
--- | --- | ---- | ---- | -------- | --------
1   | 1   | 0x00 | 1    | Variable | 2


- VER 是 SOCKS 版本, 这里应该是 0x05
- REP应答字段
    - 0x00 表示成功
    - 0x01 普通SOCKS服务器连接失败
    - 0x02 现有规则不允许连接
    - 0x03 网络不可达
    - 0x04 主机不可达
    - 0x05 连接被拒
    - 0x06 TTL超时
    - 0x07 不支持的命令
    - 0x08 不支持的地址类型
    - 0x09 未定义
    - 0xFF 未定义
- RSV 0x00 保留
- ATYP BND.ADDR 类型
    - 0x01 IPv4地址, DST.ADDR 部分 4 字节长度
    - 0x03 域名, DST.ADDR 部分第一个字节为域名长度, DST.ADDR 剩余的内容为域名, 没有\0结尾
    - 0x04 IPv6地址, 16个字节长度
- BND.ADDR 服务器绑定的地址
- BND.PORT 网络字节序表示的服务器绑定的端口

# SOCKS 用户名密码认证方式

在客户端, 服务端协商使用用户名密码认证后, 客户端发出用户名密码, 格式为:

VER | NUSERNAME | USERNAME | NPASSWORD | PASSWORD
--- | --------- | -------- | --------- | --------
1   | 1         | Variable | 1         | Variable


- VER 协议版本目前为 0x01

服务器鉴定后发出如下回应:

VER | STATUS
--- | ------
1   | 1

- STATUS 鉴定状态
    - 0x00 成功
    - 0x01 失败

# 参考

- [1] Network Working Group: SOCKS Protocol Version 5 [https://tools.ietf.org/html/rfc1928](https://tools.ietf.org/html/rfc1928)
- [2] 维基: SOCKS5 [https://zh.wikipedia.org/zh-hans/SOCKS](https://zh.wikipedia.org/zh-hans/SOCKS)
