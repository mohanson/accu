# HTTP 请求

记录一下使用 `reqwest` 库进行 HTTP 请求的操作.

# GET

发送 GET 请求该死的简单:

```rust
extern crate reqwest;

fn main()  {
    let res = reqwest::get("https://httpbin.org/get").unwrap();
    println!("{}", res.status());
}
```

其中 `reqwest::get` 是如下代码的简写:

```rust
let res = reqwest::Client::new().get(URL).send();
```

# GET Stream

流式下载, 存储 GET 请求的 Body 至文件:

```rust
extern crate reqwest;

use std::io;
use std::fs::File;

fn main()  {
    let mut res = reqwest::get("https://httpbin.org/get").unwrap();
    println!("{}", res.status());
    let mut f = File::create("/tmp/dst").unwrap();
    io::copy(&mut res, &mut f).unwrap();
}
```

# POST

发送/解析 JSON 格式的输入输出:

```rust
extern crate reqwest;
#[macro_use]
extern crate serde_derive;
extern crate serde_json;

use std::collections::HashMap;


#[derive(Deserialize)]
struct URL {
    url: String,
}

fn main() {
    let mut data = HashMap::new();
    data.insert("from", "rust");
    let mut res = reqwest::Client::new()
        .post("https://httpbin.org/post")
        .json(&data)
        .send()
        .unwrap();
    println!("{}", res.status());
    let json: URL = res.json().unwrap();
    println!("{}", json.url);
}
```
