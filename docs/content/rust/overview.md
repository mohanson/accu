由于新公司使用 Rust 栈, 因此学习 Rust 成为当务之急. Rust 系列第一篇文章大概是作者学习 Rust 的第 4 周, 短暂接触过程中, Rust 有其惊艳的地方, 也有其令人不满的地方. 当前的一个现状是 Rust 使用者(包括人与公司)远不如 Go, 在杭州搜索 Rust 岗位, 在拉钩上尽然只有一家公司在招聘 Rust 开发者...

# Rust 介绍

Rust 是一种系统编程语言. 它有着惊人的运行速度, 能够防止段错误, 并保证线程安全.

特点:

- 零开销抽象
- 转移语义
- 保证内存安全
- 线程无数据竞争
- 基于 trait 的泛型
- 模式匹配
- 类型推断
- 极小运行时
- 高效 C 绑定

```rust
fn main() {
    let greetings = ["Hello", "Hola", "Bonjour",
                     "Ciao", "こんにちは", "안녕하세요",
                     "Cześć", "Olá", "Здравствуйте",
                     "Chào bạn", "您好", "Hallo",
                     "Hej", "Ahoj", "سلام","สวัสดี"];

    for (num, greeting) in greetings.iter().enumerate() {
        print!("{} : ", greeting);
        match num {
            0 =>  println!("This code is editable and runnable!"),
            1 =>  println!("¡Este código es editable y ejecutable!"),
            2 =>  println!("Ce code est modifiable et exécutable !"),
            3 =>  println!("Questo codice è modificabile ed eseguibile!"),
            4 =>  println!("このコードは編集して実行出来ます！"),
            5 =>  println!("여기에서 코드를 수정하고 실행할 수 있습니다!"),
            6 =>  println!("Ten kod można edytować oraz uruchomić!"),
            7 =>  println!("Este código é editável e executável!"),
            8 =>  println!("Этот код можно отредактировать и запустить!"),
            9 =>  println!("Bạn có thể edit và run code trực tiếp!"),
            10 => println!("这段代码是可以编辑并且能够运行的！"),
            11 => println!("Dieser Code kann bearbeitet und ausgeführt werden!"),
            12 => println!("Den här koden kan redigeras och köras!"),
            13 => println!("Tento kód můžete upravit a spustit"),
            14 => println!("این کد قابلیت ویرایش و اجرا دارد!"),
            15 => println!("โค้ดนี้สามารถแก้ไขได้และรันได้"),
            _ =>  {},
        }
    }
}
```

# 安装-windows

[TODO] 安装方式

# 安装-linux

[TODO] 安装方式
[TODO] Vim 自动补全配置

# 参考

- [1] Rust: 首页 [https://www.rust-lang.org/zh-CN/](https://www.rust-lang.org/zh-CN/)
