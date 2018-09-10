# RC4 性能测试

在使用 python 版本 rc4 算法时发现性能较差, 几乎无法实时加解密播放 youtube 视频, 因此对 rc4 算法做了一次性能测试, 测试对象是自己写的 rc4 和 go 标准库中的 rc4.

首先利用 `dd if=/dev/urandom of=/tmp/128m count=128 bs=1M` 生成一个 128M 的测试文件. 编写如下 python 和 go 两份代码:

**python**
```py
import time

import rc4

cipher = rc4.Cipher(b'mohanson')

with open('/tmp/128m', 'rb') as r, open('/tmp/128mpy', 'wb') as w:
    tic = time.time()
    while True:
        src = r.read(8192)
        if not src:
            break
        dst = cipher.crypto(src)
        w.write(dst)
    toc = time.time() - tic
    print(toc)
```

**go**
```go
package main

import (
	"crypto/rc4"
	"io"
	"log"
	"os"
	"time"
)

func main() {
	r, err := os.Open("/tmp/128m")
	if err != nil {
		log.Fatalln(err)
	}
	defer r.Close()
	w, err := os.OpenFile("/tmp/128mgo", os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0666)
	if err != nil {
		log.Fatalln(err)
	}
	defer w.Close()

	c, _ := rc4.NewCipher([]byte("mohanson"))
	buf := make([]byte, 8192)
	tic := time.Now()
	for {
		n, err := r.Read(buf)
		if err != nil {
			if err == io.EOF {
				break
			}
			log.Fatalln(err)
		}
		c.XORKeyStream(buf[:n], buf[:n])
		w.Write(buf[:n])
	}
	toc := time.Since(tic)
	log.Println(toc)
}
```

```sh
# 执行测试
python3 rc4run.py
# 153.17044019699097

go run rc4run.go
# 2018/01/17 11:54:09 1.33959818s

# 计算输出 MD5 确保一致
md5sum /tmp/128mpy /tmp/128mgo
# 7099dda7f9a5aa49d55a3f856f3f7aa5  /tmp/128mpy
# 7099dda7f9a5aa49d55a3f856f3f7aa5  /tmp/128mgo
```

计算发现 python 版本只能做到 **0.836M/S** 的计算速度, 性能与 go 相差 114 倍! 怪不得看视频这么卡, 不能忍...

# RC4 性能优化

主要优化了 `crypto()` 函数的 dst 变量, 使其无需每次调用都新建. 这一步骤大概使性能提升了 `1/15`. 同时加了 `stream()` 方法, 算是最终版本了. 尝试了多种方式, 比如使用 numpy 和 numba, 效果提升有限但会多一个依赖库, 因此未采用. 下示为最终代码:

```py
class KeySizeError(Exception):
    pass


class Cipher:
    def __init__(self, key):
        assert isinstance(key, bytes)
        self.s = list(range(256))
        self.i = 0
        self.j = 0
        self.key = key

        k = len(key)
        if k < 1 or k > 256:
            raise KeySizeError('crypto/rc4: invalid key size ' + str(k))

        j = 0
        for i in range(256):
            j = (j + self.s[i] + key[i % k]) % 256
            self.s[i], self.s[j] = self.s[j], self.s[i]

    def __str__(self):
        return f'rc4.Cipher(key={self.key})'

    def crypto(self, dst, src):
        i, j = self.i, self.j
        for k, v in enumerate(src):
            i = (i + 1) % 256
            j = (j + self.s[i]) % 256
            self.s[i], self.s[j] = self.s[j], self.s[i]
            dst[k] = v ^ self.s[(self.s[i] + self.s[j]) % 256] % 256
        self.i, self.j = i, j

    def stream(self, dst, src):
        c = 8192
        buf = list(range(c))
        while True:
            ctx = src.read(c)
            if not ctx:
                break
            n = len(ctx)
            self.crypto(buf, ctx)
            dst.write(bytes(buf[:n]))
```
