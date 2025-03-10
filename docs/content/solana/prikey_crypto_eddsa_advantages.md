# Solana/私钥, 公钥与地址/私钥的密码学解释(八)

这是一项了不起的成就: 我们花了整整八章的时间来学习 Ed25519. 我们能坚持到这里, 相信未来无论什么艰难困阻都无法阻挡我们了. 我最后想和您谈一下 Ed25519 的优势, 有些优势是显而易见的, 而有些优势是隐藏的.

发明 Ed25519 的最大原因就是为了取代美国国家标准系列椭圆曲线. 爱德华兹本人对其的评价是:

0. 完全开放设计, 算法各参数的选择直截了当, 非常明确, 没有任何可疑之处, 相比之下, 目前广泛使用的椭圆曲线是美国国家标准系列标准, 方程的系数是使用来历不明的随机种子生成, 而至于这个种子的来历没有资料介绍.
0. 安全性高, 一个椭圆曲线加密算法就算在数学上是安全的, 在实用上也并不一定安全, 有很大的概率通过缓存, 时间, 恶意输入摧毁安全性, 而 Ed25519 系列椭圆曲线经过特别设计, 尽可能的将出错的概率降到了最低, 可以说是实践上最安全的加密算法. 例如, 任何一个 32 位随机数都是一个合法的 Ed25519 公钥, 因此通过恶意数值攻击是不可能的, 算法在设计的时候刻意避免的某些分支操作, 这样在编程的时候可以不使用 if , 减少了不同 if 分支代码执行时间不同的时序攻击概率, 相反, 美国国家标准系列椭圆曲线算法在实际应用中出错的可能性非常大, 而且对于某些理论攻击的免疫能力不高.

从开发者的角度来看, 它具有一些额外的隐藏优点.

0. Ed25519 签名过程不依赖随机数生成器. 因此我们可以不必假设必须存在一个安全的随机数发生器. 密码学基本原理: 假设越少, 问题越少!
0. Ed25519 的私钥空间是 0 <= prikey <= 0xffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffffff, 而 secp256k1 的私钥空间是 0 <= prikey <= 0xfffffffffffffffffffffffffffffffebaaedce6af48a03bbfd25e8cd0364141. 您可以看到 Ed25519 的私钥空间是非常规整的, 这能避免许多潜在的错误.
0. Ed25519 公钥只有 32 字节, 而 secp256k1 的非压缩表示公钥是 64 字节, 压缩表示公钥是 33 字节. 在系统底层里具有一些隐藏的好处. 例如常用的内存拷贝函数 memcpy, 通常会对长度小于等于 32 的字节数组使用特别的 small copy 算法, 典型例子如 glibc 的 aarch64 代码中 <https://github.com/bminor/glibc/blob/master/sysdeps/aarch64/memcpy.S>. 在一些高级语言中也会额外照顾长度小于等于 32 的字节数组, 例如 rust 就只会为这类小数组实现 clone 和 copy.
0. Ed25519 曲线上的点群运算是完备的, 也即对于所有的点群中元素都成立, 计算时无需做额外的判断, 意味着运算时不需要对不受信的外部值做昂贵的点的验证.
0. Ed25519 签名机制本身安全性不受哈希碰撞的影响.
