# Go/按行读取文件

最近在处理一些日志分析的任务, 需要按行读取文件. 虽然平时遇到这种需求我都习惯性地上 python, 但既然用了 go, 就顺便整理一下 go 里面几种读取文件的方式. 其实选择还挺多的, 根据实际情况选就好.

## 使用 bufio.Scanner

大部分情况下我都用这个. `bufio.Scanner` 的 api 很简洁, 会自动帮你去掉换行符, 而且内存效率也不错.

```go
package main

import (
    "bufio"
    "log"
    "os"
)

func main() {
    f, err := os.Open("main.go")
    if err != nil {
        log.Fatalln(err)
    }
    defer f.Close()

    // scanner, 启动!
    scanner := bufio.NewScanner(f)
    for scanner.Scan() {
        // 这里注意, scanner.Text() 不会返回换行符
        log.Println(scanner.Text())
    }
    if scanner.Err() != nil {
        log.Fatalln(scanner.Err())
    }
}
```

这里要注意一点, `scanner.Text()` 返回的字符串是不带换行符的, 这在大多数情况下很方便, 不用再去手动 trim.

不过 scanner 有个限制, 默认单行最大只能处理 64kb. 如果你的文件某一行特别长(比如处理某些日志或者 json), 可以通过 `scanner.Buffer()` 来调整缓冲区大小:

```go
scanner := bufio.NewScanner(f)
// 设置初始缓冲区为 1mb,最大 10mb
buf := make([]byte, 1024*1024)
max := 10 * 1024 * 1024
scanner.Buffer(buf, max)

for scanner.Scan() {
    fmt.Println(scanner.Text())
}
```

## 使用 bufio.Reader.ReadString

有时候你可能需要保留换行符, 或者想要更细粒度的控制, 这时候 `bufio.Reader.ReadString` 就派上用场了.

```go
package main

import (
	"bufio"
	"fmt"
	"io"
	"log"
	"os"
)

func main() {
	f, err := os.Open("main.go")
	if err != nil {
		log.Fatalln(err)
	}
	defer f.Close()

	reader := bufio.NewReader(f)
	for {
		// ReadString 读取直到遇到分隔符('\n'). 返回的字符串包含换行符.
		line, err := reader.ReadString('\n')
		if err != nil {
			if err == io.EOF {
				// 处理最后一行(可能没有换行符)
				if len(line) > 0 {
					fmt.Printf("%s", line)
				}
				break
			}
			log.Fatalln(err)
		}
		fmt.Printf("%s", line)
	}
}
```

和 scanner 不同, `ReadString` 返回的字符串是包含换行符的, 记得处理一下. 另外你可以传入任意分隔符, 不一定要用 `\n`, 这个比较灵活. 这种方式对超长行没有限制, 不过需要手动处理 eof, 写起来相对繁琐一些.

## 使用 bufio.Reader.ReadLine

如果你需要更精确的控制, 比如要处理特别长的行, 可以用 `ReadLine`. 它返回的是 `[]byte` 而不是字符串, 性能会好一些.

```go
package main

import (
	"bufio"
	"fmt"
	"io"
	"log"
	"os"
)

func main() {
	f, err := os.Open("main.go")
	if err != nil {
		log.Fatalln(err)
	}
	defer f.Close()

	reader := bufio.NewReader(f)

	for {
		// ReadLine 返回字节切片,不包含换行符. Prefix 表示是否读取了完整的行. 如果为 true,说明行太长,需要多次读取.
		line, _, err := reader.ReadLine()
		if err != nil {
			if err == io.EOF {
				break
			}
			log.Fatalln(err)
		}
		fmt.Printf("%s\n", string(line))
	}
}
```
