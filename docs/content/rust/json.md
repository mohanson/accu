# JSON 处理

JSON 是一种无处不在的开放标准格式, 它使用人类可读的文本来传输由键值对组成的数据对象.

这里借助一下 `serde_json` 这个库.

```yml
[dependencies]
serde = "*"
serde_derive = "*"
serde_json = "*"
```

假设有如下文件:

```json
{
    "name": "John Doe",
    "age": 43,
    "address": {
        "street": "10 Downing Street",
        "city": "London"
    },
    "phones": [
        "+44 1234567",
        "+44 2345678"
    ]
}
```

# 解析为脏类型

```rs
extern crate serde_json;

use std::fs::File;

fn main() {
    let f = File::open("sample.json").unwrap();
    let v: serde_json::Value = serde_json::from_reader(f).unwrap();
    println!("{:?}", v["name"].as_str().unwrap());
    println!("{:?}", v["age"].as_i64().unwrap());
}
```

# 解析为强类型

```rs
extern crate serde;
#[macro_use]
extern crate serde_derive;
extern crate serde_json;

use std::fs::File;

#[derive(Debug, Serialize, Deserialize)]
struct Address {
    street: String,
    city: String,
}

#[derive(Debug, Serialize, Deserialize)]
struct Person {
    name: String,
    age: u8,
    address: Address,
    phones: Vec<String>,
}

fn main() {
    let f = File::open("/src/sandbox/main.json").unwrap();
    let v: Person = serde_json::from_reader(f).unwrap();
    println!("{:?}", v);
}
```
