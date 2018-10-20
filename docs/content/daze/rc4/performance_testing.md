# RC4 性能测试

在使用 python 版本 rc4 算法时发现性能较差, 几乎无法实时加解密播放 youtube 视频, 因此对 rc4 算法做了一次性能测试, 测试对象是自己写的 rc4 和其他语言版本.

```
$ dd if=/dev/urandom of=/tmp/src count=128 bs=1M
```

生成一个 128M 的测试文件. 编写如下测试代码:

# python

```py
import rc4

src = '/tmp/src'
dst = '/tmp/dst_py'
k = 'mohanson'

cipher = rc4.Cipher(k.encode())
with open(src, 'rb') as r, open(dst, 'wb') as w:
    cipher.stream(r, w)
```

# go

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
	w, err := os.OpenFile(dst, os.O_CREATE|os.O_WRONLY|os.O_TRUNC, 0666)
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

# rust

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
    let mut b_src = [0; 8192];
    let mut b_dst = [0; 8192];

    loop {
        let n = f_src.read(&mut b_src[..]).unwrap();
        if n == 0 {
            break;
        }
        cipher.process(&b_src[..n], &mut b_dst[..n]);
        f_dst.write(&b_dst[..n]).unwrap();
    }
}
```

# 测试小结

```sh
$ time python3 main.py
# 153.17s
$ go build -o main main.go && time ./main
# 1.34s
$ cargo build --release && time ./target/main
# 7.16s

# 计算输出 MD5 确保一致
$ md5sum /tmp/dst_*
# 7099dda7f9a5aa49d55a3f856f3f7aa5  /tmp/dst_py
# 7099dda7f9a5aa49d55a3f856f3f7aa5  /tmp/dst_go
# 7099dda7f9a5aa49d55a3f856f3f7aa5  /tmp/dst_rs
```

- python 版本只能做到 **0.836M/S** 的计算速度, 性能与 go 相差 114 倍! 怪不得看视频这么卡, 不能忍(事实上作者已经投入 go 的怀抱)...
- go 版本性能是 rust 的 5.3 倍, 很大原因在于 go 版本 rc4 其实是汇编实现(也包括很多其他算法).
