# 以太坊: 账号

以太坊地址是一个长度为 20 的 bytes 数组, 它同时可以表示为长度为 42 的 0x + 16 进制字符串形式, 如  0xEB1379888f6117386043b1E50Aafa983006958d8.

地址是持有 ETH 的凭证. 一般状况下, 拥有 10 个 ETH 的正确描述是"A 地址拥有 10 个 ETH, 而您拥有 A 地址的使用权". 地址的使用权由私钥确认. 私钥是一个长度为 32 的 bytes 数组, 一个私钥唯一确定一个地址(但是由于私钥位数高于地址位数, 因此一个地址可能对应多个私钥).

使用如下代码生成以太私钥和其对应地址:

```go
package main

import (
	"fmt"

	"github.com/ethereum/go-ethereum/crypto"
)

func main() {
	priv, _ := crypto.GenerateKey()
	addr := crypto.PubkeyToAddress(priv.PublicKey)
	fmt.Printf("私钥: %x\n地址: %s\n", crypto.FromECDSA(priv), addr.Hex())
}
```

```no-highlight
私钥: e52fca8c99e36f02671f3fccd5b0d2388f95ec61d3c6e53a3e6cdb2189943048
地址: 0x7350Fc0B526a01EFe4ff8b952873BE0255b261f0
```

使用任意以太钱包导入该私钥, 即可获得地址 0x7350Fc0B526a01EFe4ff8b952873BE0255b261f0 的使用权. 如下是我使用 geth 导入私钥的结果, 可以看到最后生成的地址一致.

```sh
$ geth account import priv.txt
INFO [06-26|16:10:57] Maximum peer count                       ETH=25 LES=0 total=25
Your new account is locked with a password. Please give a password. Do not forget this password.
Passphrase:
Repeat passphrase:
Address: {82c5d41c443c42e4dd075516c5fccbb53ebb98f7}
```

> 私钥拥有对该地址的绝对控制权, 因此请不要随意泄露私钥.
