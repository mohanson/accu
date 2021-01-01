# 杂项/RC4

RC4 是对称流加密算法, 密文与明文长度均等. 密钥长度为 [1, 256]. 让它如此广泛分布和使用的主要因素是它不可思议的简单和速度. 但注意, RC4 已经被证明不安全, 因此, 除非你知道自己在干什么, 否则不要使用它!

## 算法介绍

RC4 生成伪随机比特流, 并与明文进行异或操作. 为了生成比特流, 加密算法使用由两部分组成内部状态:

0. 包含 1 至 255 的 256 位数组(称为 s 盒)
0. 2 个 8-bit 索引(称为 i 和 j)

首先, 初始化长度为 256 的 s 盒. 第一个 for 循环将 0 到 255 的互不重复的元素装入 s 盒. 第二个 for 循环根据密钥打乱 s 盒.

```text
for i from 0 to 255
    S[i] := i
endfor
j := 0
for i from 0 to 255
    j := (j + S[i] + key[i mod keylength]) mod 256
    swap values of S[i] and S[j]
endfor
```

下面 i, j 是两个指针. 每收到一个字节, 就进行一次循环.

```
i := 0
j := 0
while GeneratingOutput:
    i := (i + 1) mod 256
    j := (j + S[i]) mod 256
    swap values of S[i] and S[j]
    k := inputByte ^ S[(S[i] + S[j]) % 256]
    output K
endwhile
```

此算法保证每 256 次循环中 S 盒的每个元素至少被交换过一次.

## 代码实现

下示 Python 代码主要翻译自 go 标准库 `crypto/rc4`.

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

    def crypto(self, src, dst):
        i, j = self.i, self.j
        for k, v in enumerate(src):
            i = (i + 1) % 256
            j = (j + self.s[i]) % 256
            self.s[i], self.s[j] = self.s[j], self.s[i]
            dst[k] = v ^ self.s[(self.s[i] + self.s[j]) % 256] % 256
        self.i, self.j = i, j

    def stream(self, src, dst):
        c = 8192
        buf = list(range(c))
        while True:
            ctx = src.read(c)
            if not ctx:
                break
            n = len(ctx)
            self.crypto(ctx, buf)
            dst.write(bytes(buf[:n]))

if __name__ == '__main__':
    c = Cipher(b'secret')
    src = b'The quick brown fox jumps over the lazy dog'
    dst = list(range(len(src)))
    c.crypto(src, dst)
    print(bytes(dst))
```

## 性能测试

笔者最初将 RC4 用于网络流量的加密, 在使用 Python 版本 RC4 算法时发现性能较差, 几乎无法实时加解密播放 Youtube 视频, 因此对 Python, Go 和 Rust 的 RC4 算法实现做了一次性能测试.

首先生成一个 128 MB 的随机数据测试文件当作输入.

```sh
$ dd if=/dev/urandom of=/tmp/src count=128 bs=1M
```

**Python**

```py
import rc4

src = '/tmp/src'
dst = '/tmp/dst_py'
k = 'mohanson'

cipher = rc4.Cipher(k.encode())
with open(src, 'rb') as r, open(dst, 'wb') as w:
    cipher.stream(r, w)
```

**Go**

```go
package main

import (
	"crypto/cipher"
	"crypto/rc4"
	"io"
	"log"
	"os"
)

var (
	src = "/tmp/src"
	dst = "/tmp/dst_go"
	k   = "mohanson"
)

func main() {
	r, err := os.Open(src)
	if err != nil {
		log.Fatalln(err)
	}
	defer r.Close()
	w, err := os.OpenFile(dst, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0644)
	if err != nil {
		log.Fatalln(err)
	}
	defer w.Close()

	c, _ := rc4.NewCipher([]byte(k))
	if _, err := io.Copy(w, cipher.StreamReader{S: c, R: r}); err != nil {
		log.Fatalln(err)
	}
}
```

**Rust**

```ini
[dependencies]
rust-crypto = "^0.2"
```

```rs
extern crate crypto;

use std::fs::File;
use std::io::prelude::*;

use crypto::symmetriccipher::SynchronousStreamCipher;

fn main() {
    let src = "/tmp/src";
    let dst = "/tmp/dst_rs";
    let k = "mohanson";

    let mut f_src = File::open(src).unwrap();
    let mut f_dst = File::create(dst).unwrap();
    let mut cipher = crypto::rc4::Rc4::new(k.as_bytes());
    let mut b_src = [0; 4096];
    let mut b_dst = [0; 4096];
    let mut n: usize;

    loop {
        n = f_src.read(&mut b_src[..]).unwrap();
        if n == 0 {
            break;
        }
        cipher.process(&b_src[..n], &mut b_dst[..n]);
        f_dst.write(&b_dst[..n]).unwrap();
    }
}
```

测试结果如下:

```sh
$ time python3 main.py
# 153.17s

$ go build -o main main.go
$ time ./main
# 1.34s

$ cargo build --release
$ time ./target/main
# 7.16s

# 计算输出 MD5 确保一致
$ md5sum /tmp/dst_*
# 7099dda7f9a5aa49d55a3f856f3f7aa5  /tmp/dst_py
# 7099dda7f9a5aa49d55a3f856f3f7aa5  /tmp/dst_go
# 7099dda7f9a5aa49d55a3f856f3f7aa5  /tmp/dst_rs
```

自己实现的 Python 版本只能做到 0.836 MB/S 的计算速度, 性能与 Go 相差 114 倍! 怪不得看视频这么卡, 不能忍... 另一方面, Go 版本性能是 Rust 的 5.3 倍, 应该很大原因在于 Go 版本 RC4 其实是汇编实现的. 但是可惜的是, 在我写完这篇文章后的 2018 年 Go 已经将 RC4 的汇编实现移除改为原生 Go 实现了.
