# Cryptography/谷歌两步验证算法实现

谷歌的两步验证器现在的应用太广泛了, 但凡稍微认真点的站点在登陆时都会要求输入两步验证码, 但是这也带来一个问题, 就是登录网站时要多操作一步, 而且更难受的是--我需要掏手机.

所以为什么不写一个命令行的两步验证器工具呢?

## HOTP: HMAC-Based One-Time Password (HOTP) algorithm

谷歌的两步验证器基于两个算法: HOTP 和 TOTP. 我们先来介绍 HTOP, 因为后者仅仅是前者的简单扩展. HOTP 被 [RFC4226](https://datatracker.ietf.org/doc/html/rfc4226) 描述, 为了简单起见, 我只记录其中的关键算法部分.

0. 当网站要求我们添加两步验证时, 网站会生成一个随机密码 K. 随后, 我们通过扫秒二维码或者手动输入的方式将密码 K 记录在两步验证工具中. 除了密码 K 之外, 服务器和我们还都需要记录另一个数字: 该密码被使用的次数 C. 通常, K 使用 base32 进行编码, C 则是一个 uint64 整数.
0. HOTP 算法基于密码 K 和单调递增的 C, 其公式为: `HOTP(K,C) = Truncate(HMAC-SHA-1(K,C))`. 由于 HMAC-SHA-1 计算的输出是160 位(20 个 byte), 因此我们需要对结果进行截断, 以便用户输入.

截断步骤如下:

0. `offset = hmac_result[19] & 0xf`
0. 从 `hmac_result[offset:offset+4]` 还原出一个大端序的 uint32 `dbc(dynamic binary code)`
0. `dbc = dbc & 0x7fffffff`. 屏蔽 dbc 的最高有效位的原因是为了避免关于有符号和无符号模计算的混淆. 不同的处理器以不同的方式执行取模操作, 这一步可以消除关于符号整数取模计算的歧义.
0. 生成 6-digits 长度的两步验证码: `dbc = dbc % 1000000`.

当两步验证通过后, 服务器和客户端都需要对 C 进行一次自增操作.

**Go 代码实现**

```go
func main() {
	secret := "ECM5HE2DKHAFJT4ZEFA9PK4A3Q"
	c := uint64(0)

	// 对 K 进行 Base32 解码, 需要在密码尾部添加 = 使得其长度为 8 的倍数
	secret += strings.Repeat("=", -len(secret)&7)
	k, _ := base32.StdEncoding.DecodeString(secret)
	h := hmac.New(sha1.New, k)
	binary.Write(h, binary.BigEndian, c)
	sum := h.Sum(nil)
	v := binary.BigEndian.Uint32(sum[sum[19]&0x0F:]) & 0x7FFFFFFF
	fmt.Println(v % 1000000)
}
```

## TOTP: Time-Based One-Time Password

TOTP 是 HOTP 的简单简单扩展, 其定义在 [RFC6238](https://datatracker.ietf.org/doc/html/rfc6238). 简单来说, TOTP 使用当前的时间步长来替换自增的 C. TOTP 解决了以下几个问题:

0. HOTP 两步验证码基于自增的 C, 它在生成两步验证码后除非被使用, 否则永远有效.
0. 服务端与客户端需要维护自增的 C 且始终保持一致: 这很难做到, 需要实现一种同步协议处理双方的 C 值不一致的情况.

算法步骤如下:

0. 约定 X 为以秒为单位的时间步长, 默认 X = 30
1. 约定 T 为 Unix Time
2. C = T / X

**Go 代码实现**

```go
// 将上述代码的第二行修改为以下代码即可
c := time.Now().Unix() / 30
```
