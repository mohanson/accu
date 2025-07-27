# Solana/在主网发行您的代币/获取完整源码

源码我已经打包好放上 github 啦!

如果你懒得跟着一步步敲代码(我懂你), 可以直接去看我准备好的示例项目. 地址在这儿, 不用谢我, 除非你想请我喝杯奶茶.

我知道许多开发者喜欢咖啡, 但对于我而言, 奶茶总是最好的.

```sh
$ git clone https://github.com/mohanson/pxsol-spl
$ cd pxsol-spl
```

您可以在本地开发网络发行代币并部署该空投合约:

```sh
$ python make.py deploy
# 2025/05/19 11:42:11 main: deploy mana pubkey="344HRAgWWiLuhUWTm9YNKWfhV5fWK26vx45vMxA9HyCE"
```

生成一个随机账户, 并发送空投:

```sh
$ python make.py genuser
# 2025/05/19 11:45:11 main: random user prikey="Dk5y9WDhMiX83VDPTfojkWgXt6KuBAYhQEgVRAKYGLYG"

$ python make.py --prikey Dk5y9WDhMiX83VDPTfojkWgXt6KuBAYhQEgVRAKYGLYG airdrop
# 2025/05/19 11:45:24 main: request spl airdrop done recv=5.0
```
