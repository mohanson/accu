# 交叉编译

自从 Go version 1.5 开始, 交叉编译变的非常容易. 假设你在 linux 下进行开发:

```go
package main

import "fmt"

func main() {
        fmt.Printf("Hello\n")
}
```

```sh
GOOS=windows GOARCH=386 go build -o hello.exe hello.go
```

现在你就可以在 windows 的机器上执行 `hello.exe` 了.

---

环境变量 | 可选值(部分)
--- | ---
GOOS | linux, windows
GOARCH | arm, arm64, 386, amd64

完整列表参见: [https://golang.org/doc/install/source#environment](https://golang.org/doc/install/source#environment)

吐槽: 虽然大体上没什么用处, 但有时用到又记不起来~
