# Solana/私钥, 公钥与地址/公私钥对

在 solana 生态系统, 尤其是钱包应用中, 您可能更经常遇到一个叫做公私钥对的概念. 所谓的公私钥对, 其本质上就是将私钥(在前)与公钥(在后)简单的链接起来. 这个被链接起来的字节串经常以不同的名称和形象出现在网络上, 迷惑着前赴后继的新手们.

## Keypair(id.json)

Solana 的官方发行包中存在一个命令行钱包实现, 可以前往源代码仓库下载并安装它: <https://github.com/anza-xyz/agave>

在安装完成后, 您应当能找到一个叫做 solana-keygen 的工具, 我们可以使用该工具生成一个新的钱包:

```sh
$ solana-keygen new
```

工具会生成一个新的密钥对, 并将公钥和私钥保存在一个 json 文件中(通常是 ~/.config/solana/id.json). 您会看到类似以下的输出:

```text
Wrote new keypair to /home/ubuntu/.config/solana/id.json
==============================================================================
pubkey: 6ASf...GWt
==============================================================================
Save this seed phrase and your BIP39 passphrase to recover your new keypair:
smart mutual resist shrimp fever parrot suit kidney public unhappy fringe kiwi
==============================================================================
```

文件中保存的是一个长度为 64 的字节数组. 该数组前 32 位是私钥, 后 32 位则是该私钥对应的公钥.

```sh
$ cat ~/.config/solana/id.json

[0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 0, 1, 76, 181, 171, 246, 173, 121, 251, 245, 171, 188, 202, 252, 194, 105, 216, 92, 210, 101, 30, 212, 184, 133, 181, 134, 159, 36, 26, 237, 240, 165, 186, 41]
```

例: 以上 id.json 所对应的私钥是什么? 账户地址是什么?

答:

```py
import pxsol

idjson = bytearray([
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
    0x4c, 0xb5, 0xab, 0xf6, 0xad, 0x79, 0xfb, 0xf5, 0xab, 0xbc, 0xca, 0xfc, 0xc2, 0x69, 0xd8, 0x5c,
    0xd2, 0x65, 0x1e, 0xd4, 0xb8, 0x85, 0xb5, 0x86, 0x9f, 0x24, 0x1a, 0xed, 0xf0, 0xa5, 0xba, 0x29,
])

prikey = pxsol.core.PriKey(idjson[:32])
pubkey = pxsol.core.PubKey(idjson[32:])
assert prikey.pubkey() == pubkey
print(prikey) # 11111111111111111111111111111112
print(pubkey) # 6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt
```

## Keypair 的 base58 表示

在 solana 生态里, 普通用户可能更多的使用浏览器钱包, 例如流行的 phantom 钱包. 这类钱包的一个常用功能就是可以导入或者导出私钥.

但是这类浏览器钱包大都犯了一个错误: 他们导入或导出的实际上是公私钥对, 而不是私钥, 尽管您在页面上看到的提示词语是私钥.

就作者所观察的几个钱包, 当您试图导入"私钥"时, 应当复制到输入框中的是公私钥对的 base58 表示; 而钱包导出的"私钥"其实也是公私钥对的 base58 表示.

例: 小明使用 solana-keygen 生成了一个新的钱包, 他应当如何将该钱包导入到 phantom 钱包里?

答: 使用 base58 编码 ~/.config/solana/id.json 文件中的数据, 得到字符串, 复制到 phantom 钱包的"私钥"框框里即可. 代码如下:

```py
import pxsol

idjson = bytearray([
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00,
    0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0x01,
    0x4c, 0xb5, 0xab, 0xf6, 0xad, 0x79, 0xfb, 0xf5, 0xab, 0xbc, 0xca, 0xfc, 0xc2, 0x69, 0xd8, 0x5c,
    0xd2, 0x65, 0x1e, 0xd4, 0xb8, 0x85, 0xb5, 0x86, 0x9f, 0x24, 0x1a, 0xed, 0xf0, 0xa5, 0xba, 0x29,
])
print(pxsol.base58.encode(idjson)) # 1111111111111111111111111111111PPm2a2NNZH2EFJ5UkEjkH9Fcxn8cvjTmZDKQQisyLDmA
```

例: 有私钥 `11111111111111111111111111111112`, 应当如何将其导入到 phantom 钱包里?

答: 我们通过私钥来生成 keypair 的 base58 表示.

```py
import pxsol

prikey = pxsol.core.PriKey.base58_decode('11111111111111111111111111111112')
pubkey = prikey.pubkey()
print(pxsol.base58.encode(prikey.p + pubkey.p))
# 1111111111111111111111111111111PPm2a2NNZH2EFJ5UkEjkH9Fcxn8cvjTmZDKQQisyLDmA
```

## Keypair 的 base64 表示

Solana 在历史上还存在过一种以 base64 表示的公私钥对格式, 该格式是将公私钥对以 base64 编码而成.

提醒: 以 **base64** 编码而成.

当您使用 solana 生态里的应用时, 应当特别当心这种格式. 我在使用某个 solana 钱包时, 数次尝试导入私钥无果, 遂无能狂怒研究其源代码, 发现其采用了这种编码格式.

幸运的是, 经我考证, 该格式仅在 solana 极早期有过小范围的使用, 在当前时间节点下除非是考古人员否则很难再遇到它.
