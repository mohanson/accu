# Rust 速成课/流程控制

我们继续我们的 Rust 速成课, 我们将主要探讨一下流程控制. 流程控制主要分成两个部分, 一个是条件, 另一个是分支. 条件的话, 它大多数情况下是一个布尔值, 而分支的书写, Rust 与其它语言的表达方式上会有一些略微的不同. 事不宜迟, 我们开始吧.

## 判断

我们打开先前的 hello 项目, 让我们修改一点逻辑. 我想判断两个数的大小, 当第一个数比第二个数小时, 打印出条件成立的字符串; 条件不成立时, 打印出否定的结果.

OK, 显而易见的, 我们可以使用 if 表达式. if 表达式可以根据条件执行分支代码, 我们提供一个条件, 然后说: "如果满足此条件, 请运行此代码块. 如果不满足条件, 请不要运行此代码块."

```rs
fn main() {
    let number = 3;

    if number < 5 {
        println!("condition was true");
    } else {
        println!("condition was false");
    }
}
```

你应该注意到, if 表达式的条件没有加括号, 你不需要写 `if (number < 5)`, 而只需要 `if number < 5`. 这个特性非常棒, 它有效延长了我的键盘寿命. else 经常和 if 一起出现, 就像上面的代码写的那样. 但是 else 代码块是可以被忽略的, 这样的话, 当条件不满足时, 任何事情都不会发生.

尝试运行下代码, 你应该能看到以下输出

```sh
$ cargo run
   Compiling branches v0.1.0 (file:///projects/branches)
    Finished dev [unoptimized + debuginfo] target(s) in 0.31s
     Running `target/debug/branches`
condition was true
```

我们尝试将 number 修改为 7, 这样条件就不会成立, 看看会发生什么.

```sh
$ cargo run
   Compiling branches v0.1.0 (file:///projects/branches)
    Finished dev [unoptimized + debuginfo] target(s) in 0.31s
     Running `target/debug/branches`
condition was false
```

要注意, Rust 条件表达式的条件只能是布尔值. 与 C 语言不同, Rust 是强类型语言, 它不会做自动类型转换. 在很多其它语言中, 比如 JavaScript 或 Python, 条件表达式的条件可以是一个整数, 或其他的什么对象, 但 Rust 不行, 它有且只能是布尔值.

我们会讨论一个 if 有趣的应用, 在 Rust 中, if 是一个表达式, 这意味着 if 可以有返回值. 我们可以使用 if 完成类似 C 语言中三值表达式的功能, 就像这样:

```rs
fn main() {
    let condition = true;
    let number = if condition { 5 } else { 6 };

    println!("The value of number is: {}", number);
}
```

现在, 我会出一道题, 你们将会有 10 秒钟的时间思考. 如果我将上面代码中的 6 改为字符串的 six, 请问代码能被编译和运行吗. 10, 9, 8, 7, 6, 5, 4, 3, 2, 1, 好的, 时间结束. 我希望你得出了和我一样的答案, 答案是不能. 因为 Rust 必须在编译期确认所有变量的类型, 当你在一个条件表达式中既给出数字又给出字符串, 这会让编译器迷惑.

## 循环

多次执行代码块通常很有用. 对于此任务, Rust 提供了几个循环. Rust 具有三种循环, 分别是 loop, while 和 for. 让我们都来尝试下.

loop 表示一次又一次的执行代码, 直到你明确表示应该停止循环为止. 我写下了下面这样的代码, 但是我并不想运行它, 因为它会刷爆我的屏幕. 所以我们可以假装我已经运行过它了, OK? 很好, 我们来看下一个.

```rs
fn main() {
    loop {
        println!("again!");
    }
}
```

while 循环, 可以直接理解为带停止条件的 loop 的循环. 它的标准写法就像下面这样:

```rs
fn main() {
    let mut number = 3;
    while number != 0 {
        println!("{}!", number);
        number -= 1;
    }
}
```

至于 for 循环, 它通常用来遍历一个集合, 例如数组. 通常情况下, 面对数组我都建议用 for 啦, 因为这样会有更高的安全性, 如果你用 loop 或者 while 的话, 有可能写出越界访问的代码.

```rs
fn main() {
    let a = [10, 20, 30, 40, 50];

    for element in a.iter() {
        println!("the value is: {}", element);
    }
}
```
