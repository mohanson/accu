# Go/按行读取文件

Go 中按行读取文件方法还是比较多的, 但最简单也是最优雅的方式是使用 `bufio.Scanner`. 我平时很少用 Go 去按行处理文件, 基本上有这方面需求也是上 python, 恰巧今天遇到, 所以记录以下

```go
package main

import (
	"bufio"
	"log"
	"os"
)

func main() {
	f, err := os.Open("run.go")
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
