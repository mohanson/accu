# 概览

RC4 是对称流加密算法, 密文与明文长度均等. 密钥长度为 [1, 256]. 让它如此广泛分布和使用的主要因素是它**不可思议的简单和速度**.

RC4 生成伪随机比特流, 并于明文进行异或操作. 为了生成比特流, 加密算法使用由两部分组成内部状态:

1. 包含 1 至 255 的 256 位数组(称为 s 盒)
2. 2 个 8-bit 索引(称为 i 和 j)

首先, 初始化长度为256的 s 盒. 第一个 for 循环将 0 到 255 的互不重复的元素装入 s 盒. 第二个 for 循环根据密钥打乱 s 盒.

```
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
    i := (i + 1) mod 256   //a
    j := (j + S[i]) mod 256 //b
    swap values of S[i] and S[j]  //c
    k := inputByte ^ S[(S[i] + S[j]) % 256]
    output K
endwhile
```

此算法保证每256次循环中S盒的每个元素至少被交换过一次.

# 代码实现

下示 python 代码主要翻译自 go 标准库 `crypto/rc4`.

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

# 参考
- [1] 维基: RC4 [https://en.wikipedia.org/wiki/RC4](https://en.wikipedia.org/wiki/RC4)
- [2] Go: crypto/rc4 标准库 [https://github.com/golang/go/blob/master/src/crypto/rc4/rc4.go](https://github.com/golang/go/blob/master/src/crypto/rc4/rc4.go)
