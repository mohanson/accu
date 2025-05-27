# Solana/程序开发入门/获取完整源码

源码我已经打包好放上 gitHub 啦!

如果你懒得跟着一步步敲代码(我懂你), 可以直接去看我准备好的示例项目. 地址在这儿, 不用谢我, 除非你想请我喝杯奶茶.

```sh
$ git clone https://github.com/mohanson/pxsol-ss
$ cd pxsol-ss
```

```sh
$ python make.py deploy
# 2025/05/20 16:06:38 main: deploy program pubkey="T6vZUAQyiFfX6968XoJVmXxpbZwtnKfQbNNBYrcxkcp"
```

```sh
# Save some data.
$ python make.py save "The quick brown fox jumps over the lazy dog"

# Load data.
$ python make.py load
# The quick brown fox jumps over the lazy dog.

# Save some data and overwrite the old data.
$ python make.py save "待到秋来九月八, 我花开后百花杀. 冲天香阵透长安, 满城尽带黄金甲."
# Load data.
$ python make.py load
# 待到秋来九月八, 我花开后百花杀. 冲天香阵透长安, 满城尽带黄金甲.
```
