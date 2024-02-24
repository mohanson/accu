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
	body := strings.Replace("------WebKitFormBoundaryF15rNsGN08qoXN2Z\r\nContent-Disposition: form-data; name=\"authenticity_token\"\r\n\r\n5aXlNWinJebbx/yVkzgwb2l8Bwwhkg0fgsveQm4+u9Wc1spycql8131Jr243x9Z3EY+Kfi4vP+dVjjXfgtxF5g==\r\n------WebKitFormBoundaryF15rNsGN08qoXN2Z\r\nContent-Disposition: form-data; name=\"value\"\r\n\r\njack\r\n------WebKitFormBoundaryF15rNsGN08qoXN2Z--\r\n", "jack", name, 1)
	requ, err := http.NewRequest(http.MethodPost, "https://github.com/signup_check/username", bytes.NewReader([]byte(body)))
	if err != nil {
		return 0, err
	}
	requ.Header.Set("accept", "*/*")
	requ.Header.Set("accept-language", "zh-CN,zh;q=0.9,en;q=0.8,en-GB;q=0.7,en-US;q=0.6,zh-TW;q=0.5")
	requ.Header.Set("content-type", "multipart/form-data; boundary=----WebKitFormBoundaryJ387fEq3mIJpLAfG")
	requ.Header.Set("sec-ch-ua", "\"Not A(Brand\";v=\"99\", \"Microsoft Edge\";v=\"121\", \"Chromium\";v=\"121\"")
	requ.Header.Set("sec-ch-ua-mobile", "?0")
	requ.Header.Set("sec-ch-ua-platform", "\"Windows\"")
	requ.Header.Set("sec-fetch-dest", "empty")
	requ.Header.Set("sec-fetch-mode", "cors")
	requ.Header.Set("sec-fetch-site", "same-origin")
	requ.Header.Set("cookie", "_octo=GH1.1.867648387.1708765773; logged_in=no; preferred_color_mode=light; tz=Asia%2FShanghai; _gh_sess=zjDsVXWemwKElzIr0bYNgR%2FRUZ34KY03HmmfUPjONO3%2B92DMW8%2F24p5kupdy5D0rUE4OtyBeOpDOKIC8PUcv5tIY5oz7W14bch5Jf72bOJeMbHbONnNyK69CjA%2BGRWI7BB%2FlC4L%2FnQtcfjUS69n3h2AEiPmMPumEwHxN%2FlLa8kyKVt4m%2FAzqqyvzXhSOQfCPTnhh%2BW8ciVwxWqJkPQute23j%2BMYg6MrrZb4fDpQbbsHi2duqWtjTK26diGqA%2BirURVF12T8EbCXhL90fuFsOFEvnCeCK%2BDOSiJlSQKPZy6y5VoRa--DavafQZCTdYzzivi--4JLPykEtSgSAkUNIJ32ANw%3D%3D")
	requ.Header.Set("Referer", "https://github.com/signup?ref_cta=Sign+up&ref_loc=header+logged+out&ref_page=%2F&source=header-home")
	requ.Header.Set("Referrer-Policy", "strict-origin-when-cross-origin")
	resp, err := http.DefaultClient.Do(requ)
	if err != nil {
		return 0, err
	}
	if resp.StatusCode == 200 {
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
