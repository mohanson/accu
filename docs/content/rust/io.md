# 文件读写

Everything is a file.

这里不得不提一下 Unix 哲学: "一切皆文件". 它描述了 Unix 的特性--所有输入/输出资源, 如文档, 目录, 硬盘驱动器, 调制解调器, 键盘, 打印机甚至一些进程间和网络通信, 都是通过文件系统描述的简单的字节流.

Rust 初学也将从文件读写开始.

**字节读取**

```rust
use std::fs::File;
use std::io::prelude::*;


fn main() {
    let mut f = File::open("/tmp/src").unwrap();
    let mut buf = vec![0; 8];
    let n = f.read(&mut buf[..]).unwrap();
    println!("{:?}", &buf[..n]);
}
```

**读取全部**

```rust
use std::fs::File;
use std::io::prelude::*;


fn main() {
    let mut f = File::open("/tmp/src").unwrap();
    let mut buf = String::new();
    f.read_to_string(&mut buf).unwrap();
    println!("{}", buf);
}
```

**逐行读取**

```rust
use std::fs::File;
use std::io::prelude::*;
use std::io::BufReader;

fn main() {
    let f = File::open("/tmp/src").unwrap();
    let reader = BufReader::new(f);
    for line in reader.lines() {
        // line 是 std::result::Result<std::string::String, std::io::Error> 类型
        // line 不包含换行符
        let line = line.unwrap();
        println!("{}", line);
    }
}
```

**写入文件**

```rust
use std::fs::File;
use std::io::prelude::*;

fn main() {
    let mut f = File::create("/tmp/dst").unwrap();
    f.write("Hello\n".as_bytes()).unwrap();
    f.write("你好\n".as_bytes()).unwrap();
    f.write("안녕하세요\n".as_bytes()).unwrap();
}
```

**追加文件**

```rust
use std::fs::OpenOptions;
use std::io::prelude::*;

fn main() {
    let mut f = OpenOptions::new().create(true).append(true).open("/tmp/dst").unwrap();
    f.write("Hello\n".as_bytes()).unwrap();
    f.write("你好\n".as_bytes()).unwrap();
    f.write("안녕하세요\n".as_bytes()).unwrap();
}
```
