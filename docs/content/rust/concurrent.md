# Rust 并发

并发与并行是计算机科学中相当重要的两个主题, 并且在当今生产环境中也十分热门. 计算机正拥有越来越多的核心, 然而很多程序员还没有准备好去完全的利用它们.
Rust 的内存安全功能也适用于并发环境.甚至并发的 Rust 程序也会是内存安全的, 并且没有数据竞争. Rust 的类型系统也能胜任, 并且在编译时能提供你强大的方式去推论并发代码.

#创建线程

```rust
use std::thread;

fn main() {
    let handle = thread::spawn(|| {
        println!("Hello from a thread!");
    });
    // 等待子线程结束
    handle.join().unwrap();
}
```

# move 闭包

使用 move 可以将变量从环境引用至自身.

```rust
use std::thread;

fn main() {
    let x = 1;
    thread::spawn(move || {
        println!("x is {}", x);
    }).join()
    .unwrap();
}
```

# 共享变量

因为 Rust 的所有权机制, 我们无法在多个线程间共享一个(可读)变量. 考虑如下代码:

```rust
use std::thread;
use std::time::Duration;

fn main() {
    let data = vec![1, 2, 3];
    for _ in 0..3 {
        thread::spawn(move || {
            println!("{:?}", data[0]);
        });
    }
    thread::sleep(Duration::from_secs(1));
}
```

他无法运行, 编译器会给出一个提示:

```
note: move occurs because `data` has type `std::vec::Vec<i32>`, which does not implement the `Copy` trait
```

为了解决这个问题, 我们使用 `Arc<T>`, Rust 标准的原子引用计数类型. `Arc<T>` 的原子部分可以在多线程中安全的访问. 为此编译器确保了内部计数的改变都是不可分割的操作这样就不会产生数据竞争. 本质上, `Arc<T>` 是一个可以让我们在线程间安全的共享所有权的类型.

```rust
use std::thread;
use std::sync::Arc;
use std::time::Duration;

fn main() {
    let data = Arc::new(vec![1, 2, 3]);
    for _ in 0..3 {
        let data = data.clone();
        thread::spawn(move || {
            println!("{:?}", data[0]);
        });
    }
    thread::sleep(Duration::from_secs(1));
}
```

`Arc<T>` 默认是不可变的, 为了获得可变变量, 我们使用 `Mutex<T>`

```rust
use std::thread;
use std::sync::{Arc, Mutex};
use std::time::Duration;

fn main() {
    let data = Arc::new(Mutex::new(vec![1, 2, 3]));
    for _ in 0..3 {
        let data = data.clone();
        thread::spawn(move || {
            let mut data = data.lock().unwrap();
            data[0] += 1;
        });
    }
    thread::sleep(Duration::from_secs(1));
    println!("{:?}", data.lock().unwrap()[0]);
}
```

这里我们 "锁定" 了互斥锁(mutex). 一个互斥锁, 正如其名, 同时只允许一个线程访问一个值. 当我们想要访问一个值时, 我们 lock() 它. 这会 "锁定" mutex, 并且其他线程不能锁定它(也就是改变它的值), 直到我们处理完之后. 如果一个线程尝试锁定一个已经被锁定的 mutex, 它将会等待直到其他线程释放这个锁为止.

# 信道

与 Go 里面的信道几乎一致. 任何实现了 `Send` 的数据都可以传入信道. 下面的代码演示了创建 10 个线程并等待 10 个线程全部执行完毕. 通常并不需要手动实现 Send 和 Sync trait, 因为由 Send 和 Sync 的类型组成的类型, 自动就是 Send 和 Sync 的. 因为他们是标记 trait, 甚至都不需要实现任何方法. 他们只是用来加强并发相关的不可变性的.

```rust
use std::sync::mpsc;
use std::thread;

fn main() {
    let (tx, rx) = mpsc::channel();
    for i in 0..10 {
        let tx = tx.clone();
        thread::spawn(move || {
            tx.send(i).unwrap();
        });
    }
    for _ in 0..10 {
        let r = rx.recv().unwrap();
        println!("{}", r);
    }
}
```

# 参考

- [1] kaisery: Rust 程序设计-5.6 并发 [https://kaisery.gitbooks.io/rust-book-chinese/content/content/Concurrency%20并发.html](https://kaisery.gitbooks.io/rust-book-chinese/content/content/Concurrency%20并发.html)
