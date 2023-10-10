# Rust/泛型类型

在开始这次的课程之前呢, 我们先来活动一下手指. 我遇到了一个问题, 我需要写一个函数, 这个函数接收两个数字, 然后返回较大的那个数字. 我不想说大话, 但这实在是太简单了, 我的编程功力很深厚, 所以, 我们可以很快写下这个函数:

```rs
fn largest(a: u32, b: u32) -> u32 {
    if a > b {
        a
    } else {
        b
    }
}
```

这个函数能工作, 但我觉得不太好, 因为它只能比较两个 u32 类型数字的大小. 我现在除了想比较两个 u32 外, 还想比较两个 f32. 有一种可以行的办法, 我们可以定义多个 largest 函数, 让它们分别叫做 largest_u32, largest_f32, 这很简单, 只要变成一个无情的复制粘贴机器, 你还能写出 largest_u64 和 largest_f64. 这能工作, 但不美观. 有没有一种方法, 只使用 largest 这个函数名, 就能同时支持所有类型呢?

答案是有的, Rust 的编译器已经想到了这一点, 只要你使用泛型语法.

```rs
fn largest<T: std::cmp::PartialOrd>(a: T, b: T) -> T {
    if a > b {
        a
    } else {
        b
    }
}

fn main() {
    println!("{}", largest::<u32>(1, 2));
    println!("{}", largest::<f32>(1.0, 2.1));
}
```

## 泛型语法

泛型, 直观的表示就是它的类型是不确定的, 也可以理解为, 类型也是一个函数的参数. 为了参数化函数中的这些类型, 我们也需要为类型参数取个名字, 道理和给函数的形参起名一样. 任何标识符都可以作为类型参数的名字, 这里选用 T, 因为传统上来说, Rust 的参数名字都比较短, 通常就只有一个字母, 同时, Rust 类型名的命名规范是骆驼命名法, T 作为 type 的缩写是大部分 Rust 程序员的首选.

如果要在函数体中使用参数, 就必须在函数签名中声明它的名字, 好让编译器知道这个名字指代的是什么. 同理, 当在函数签名中使用一个类型参数时, 必须在使用它之前就声明它. 为了定义泛型版本的 largest 函数, 类型参数声明位于函数名称与参数列表中间的尖括号中. 同时, 我们约定类型参数必须是可比较的, 这里使用 std::cmp::PartialOrd 进行约束.

## Option 和 Result

我们几乎可以在任何地方使用泛型, 但此时我们先主要关注一下标准库中最重要的两个泛型. 它们分别是 Option 和 Result. 许多语言使用 null, nil 或者 undefined 类型表示空输出, 并使用 Exception 处理错误. Rust 没有使用这两者, 这主要基于安全性考虑. 因为这很容易出现空指针错误, 或者数据泄漏等问题. Rust 提供了两个特殊的通用枚举: Option 和 Result 来处理上述情况.

```rs
enum Option<T> {
    Some(T),
    None,
}

enum Result<T, E> {
    Ok(T),
    Err(E),
}
```

Option 类型代表一个可选值: 每个 Option 要么是 Some, 并且包含一个值, 要么是 None. Option 类型在 Rust 代码中非常常见, 通常它们会配合匹配语法一起使用. Result 通常作为函数的返回值, 如果这个函数可能产生错误, 则必须通过将有效输出的数据类型和错误的数据类型结合使用 Result 类型. 我们直观的感受下应该如何使用它们.

```rs
fn main() {
    match std::env::home_dir() {
        Some(data) => println!("option is some, data = {:?}", data),
        None => println!("option is none"),
    }

    match std::env::var("LANG") {
        Ok(data) => println!("ok! {:?}", data),
        Err(err) => println!("err {}", err),
    }
}
```
