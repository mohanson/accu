# Solana/程序开发入门/获取完整源码

源码我已经打包好放上 github 啦!

如果你懒得跟着一步步敲代码(我懂你), 可以直接去看我准备好的示例项目. 地址在这儿, 不用谢我, 除非你想请我喝杯奶茶.

我知道许多开发者喜欢咖啡, 但对于我而言, 奶茶总是最好的.

```sh
$ git clone https://github.com/mohanson/pxsol-ss
$ cd pxsol-ss
```

```sh
$ python make.py deploy
# 2025/05/20 16:06:38 main: deploy program pubkey="T6vZUAQyiFfX6968XoJVmXxpbZwtnKfQbNNBYrcxkcp"
```

注意到程序地址会被保存在 `res/info.json` 中, 后续操作会直接从此文件获取程序地址.

```sh
# Save some data.
$ python make.py save "The quick brown fox jumps over the lazy dog"

# Load data.
$ python make.py load
# The quick brown fox jumps over the lazy dog.

# Save some data and overwrite the old data.
$ python make.py save "片云天共远, 永夜月同孤."
# Load data.
$ python make.py load
# 片云天共远, 永夜月同孤.
```
