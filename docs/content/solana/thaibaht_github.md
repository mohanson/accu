# Solana/泰铢币/获取完整源码

源码我已经打包好放上 github 啦!

如果你懒得跟着一步步敲代码(我懂你), 可以直接去看我准备好的示例项目. 地址在这儿, 不用谢我, 除非你想请我喝杯奶茶.

我知道许多开发者喜欢咖啡, 但对于我而言, 奶茶总是最好的.

> 有时候人生就像一部小说, 总得给我们点儿 déjà vu(既视感) 的惊喜.

```sh
$ git clone https://github.com/mohanson/pxsol-thaibaht
$ cd pxsol-thaibaht
```

```sh
$ python make.py deploy
# 2025/05/20 16:06:38 main: deploy program pubkey="9SP6msRytNxeHXvW38xHxjsBHspqZERDTMh5Wi8xh16Q"
```

注意到程序地址会被保存在 `res/info.json` 中, 后续操作会直接从此文件获取程序地址.

```sh
# Mint 21000000 Thai Baht for Ada
$ python make.py mint 21000000

# Show ada's balance
$ python make.py balance 6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt
# 21000000

# Transfer 100 Thai Baht to Bob
$ python make.py transfer 100 8pM1DN3RiT8vbom5u1sNryaNT1nyL8CTTW3b5PwWXRBH

# Show ada's balance
$ python make.py balance 6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt
# 20999900
# Show bob's balance
$ python make.py balance 8pM1DN3RiT8vbom5u1sNryaNT1nyL8CTTW3b5PwWXRBH
# 100
```
