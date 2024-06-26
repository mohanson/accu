# Go/Github 用户名可用性并发检测

一个简单的脚本, 用来并发检测 Github 用户名是否可被注册.

```go
package main

import (
	"bytes"
	"log"
	"net/http"
	"os"
	"strings"
	"sync"
)

func nameUsableOnce(name string) (int, error) {
	requ, err := http.NewRequest(http.MethodGet, "https://github.com/signup_check/username?value="+name, nil)
	if err != nil {
		return 0, err
	}
	requ.Header.Set("accept", "*/*")
	requ.Header.Set("accept-language", "zh-CN,zh;q=0.9")
	requ.Header.Set("cookie", "_octo=GH1.1.457252931.1719380713; logged_in=no; preferred_color_mode=light; tz=Asia%2FShanghai; _gh_sess=HF644%2F8U8ywdKlMp715RGYQkUpyS8vQW3FtmZD%2BZ2QlLpkX98KzAOkgJe%2F9EL9xm2NDeRviHfJoX3TseQ%2Ft2vBZF69RdBj7sjo2VqZFbwwLOpbFng2oKnOju1V7O4cTwXtE1ST%2FNrzspUv8ORQr%2FH0T89cbXNtRvBpRBeE2Li7%2BbEjw2plV1QqUeHft%2BvmN8VHy4g21Z%2FrdiElsCn%2BSdR3CcRy5II6QJGlglHzbBiRK3zEdMkDrkscAN9u2cddJjOBCU6Vb9vfqeS%2F4ld%2BTxTsUqeYFp9ZXWNUe6KQaX244Nmwu8--I89PWqORMAs7DW0y--Pb25BtIFFlyGMCfy%2BenVrw%3D%3D")
	requ.Header.Set("priority", "u=1, i")
	requ.Header.Set("referer", "https://github.com/signup?ref_cta=Sign+up&ref_loc=header+logged+out&ref_page=%2F&source=header-home")
	requ.Header.Set("sec-ch-ua", "\"Not A(Brand\";v=\"8\", \"Microsoft Edge\";v=\"126\", \"Chromium\";v=\"126\"")
	requ.Header.Set("sec-ch-ua-mobile", "?0")
	requ.Header.Set("sec-ch-ua-platform", "\"Windows\"")
	requ.Header.Set("sec-fetch-dest", "empty")
	requ.Header.Set("sec-fetch-mode", "cors")
	requ.Header.Set("sec-fetch-site", "same-origin")
	requ.Header.Set("user-agent", "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36 Edg/126.0.0.0")
	resp, err := http.DefaultClient.Do(requ)
	if err != nil {
		return 0, err
	}
	doa.Doa(resp.StatusCode == http.StatusOK)
	defer resp.Body.Close()
	body := string(doa.Try(io.ReadAll(resp.Body)))
	if strings.Contains(body, "is available") {
		return 1, nil
	} else {
		return 0, nil
	}
}

func nameUsableReno(name string) (int, error) {
	for {
		r, err := nameUsableOnce(name)
		if err != nil {
			log.Println(err)
			continue
		}
		return r, nil
	}
}

func nameStable(name string) {
	w, err := os.OpenFile("/tmp/github", os.O_CREATE|os.O_WRONLY|os.O_APPEND, 0644)
	if err != nil {
		panic(err)
	}
	defer w.Close()
	w.Write([]byte(name))
	w.Write([]byte("\n"))
}

func main() {
	source := make(chan string, 8)
	result := make(chan string, 8)

	w0 := sync.WaitGroup{}
	w1 := sync.WaitGroup{}

	go func() {
		source <- "ada"
		source <- "bob"
		close(source)
	}()

	go func() {
		for name := range result {
			nameStable(name)
			w1.Done()
		}
	}()

	for i := 0; i < 4; i++ {
		w0.Add(1)
		go func() {
			for name := range source {
				b, _ := nameUsableReno(name)
				log.Println(name, b)
				if b != 0 {
					w1.Add(1)
					result <- name
				}
			}
			w0.Done()
		}()
	}
	w0.Wait()
	close(result)
	w1.Wait()
}
```

以上的示例代码会检测 "ada" 和 "bob" 两个用户名是否用. 可用的用户名将以文本形式写入 "/tmp/github" 文件内.
