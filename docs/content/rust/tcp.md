# TCP

使用 Rust 实现一个 ping/pong 服务器. 目前实现是一个连接一个线程, 性能感觉相当不靠谱.

# TCP Server

```rust
use std::io::prelude::*;
use std::io::BufReader;
use std::io::BufWriter;
use std::net::TcpListener;
use std::thread;

fn main() {
    let l = TcpListener::bind("127.0.0.1:8080").unwrap();
    for stream in l.incoming() {
        thread::spawn(move || {
            let stream = stream.unwrap();
            let reader = BufReader::new(&stream);
            let mut writer = BufWriter::new(&stream);
            for line in reader.lines() {
                let line = line.unwrap();
                println!("{}", line);
                if line == "ping" {
                    writer.write_all(b"pong\n").unwrap();
                    writer.flush().unwrap();
                }
            }
        });
    }
}
```

# TCP Client

```rust
use std::io::prelude::*;
use std::io::BufReader;
use std::io::BufWriter;
use std::net::TcpStream;

fn main() {
    let stream = TcpStream::connect("127.0.0.1:8080").unwrap();
    let mut reader = BufReader::new(&stream);
    let mut writer = BufWriter::new(&stream);
    writer.write_all(b"ping\n").unwrap();
    writer.flush().unwrap();
    let mut line = String::new();
    reader.read_line(&mut line).unwrap();
    println!("{}", line);
}
```
