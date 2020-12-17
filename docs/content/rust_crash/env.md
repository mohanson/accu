# Rust 速成课/开发环境搭建

各位 Rust 的朋友们大家好, 我是 Yeah 老师. 这次我们将约定俗成的用 Rust 写出 Hello World! 代码. 当然啦, 首先我们应该做的是下载并安装 Rust. 正如你在视频前看到的, 我现在正在使用 Windows 操作系统录制这次课程, 但我平常更加常用的开发系统是 Linux. 所以我将先打开 [https://www.rust-lang.org/tools/install](https://www.rust-lang.org/tools/install) 这个网页, 如果你想在 Windows 上安装 Rust, 那么可以直接点击页面上的 "DOWNLOAD RUSTUP-INIT.EXE (64-BIT)" 按钮下载. 或者你和我一样在使用 Linux, 那么点击 "Other Installation Methods", 找到页面上的 `curl https://sh.rustup.rs -sSf | sh -s -- --help`, 将它敲入你的 shell 中.

通常情况下, 我们只需要一直按 Enter 键. 如果一切顺利的话, 只需要打开 shell, 输入 `rustc --version`, 这会打印出当前的 Rust 版本, 我这里显示的是

```text
$ rustc --version
rustc 1.45.0 (5c1f21c3b 2020-07-13)
```

如您所见, 我已经安装好了 Rust.

## Rust 开发环境

我相信每个人都有自己习惯的开发环境, 在很久之前, 我曾经习惯使用 IDE, 之后我又切换成了 Vim, 至于现在, 我更加习惯使用 vscode. 因此, 我会向您介绍我目前的开发环境, 作为一个可选的参考. 首先你得安装 vscode, 这是没什么用的废话, 然后在它插件市场中搜索 Rust, 您会看到有两个插件排在最前面, 一个是加了小星星的 Rust, 另一个是 rust-analyzer. 我建议是安装第二个啦, 因为第一个插件的性能实在是不好, 它在打开大型项目时需要很长时间构建索引, 后者则快得多.

## Hello World!

OK, 接下来我们来创建一个 Rust 项目, 我使用的命令是

```text
$ cargo new hello
```

这会在文档中创建一个名叫 hello 的文件夹, 我们用 vscode 打开这个项目. 基本上这个命令的作用是创建一个最小型的 Rust 应用程序, 它里面的结构还可以. 当前的结构中你将看到 `Cargo.toml` 和 `src` 两个文件和文件夹.

```text
.
├── Cargo.toml
└── src
    └── main.rs
```

`Cargo.toml` 是项目的描述文件, 您应该在很多语言中看到过类似作用的配置文件, 例如 Golang 里面的 "go.mod". 它里面保存了项目的依赖库, 项目的名称, 版本号等信息, 我们可以在这个文件里面做很多事情, 但现在我们先专注于一些简单的东西. 然后您将看到 src 源码目录, 它里面有个 `main.rs` 文件. 我们打开这个文件, 会看到它里面包含一个 main 函数. 没错啦, 它就是 Rust 项目的入口函数. 代码很简单, 打印出 Hello World 字符串. 但我们现在会改进这个项目, 在这个字符串屁股后面加上你喜欢的文字, 是我的话我就会加上 42 这个数字, 这个数字很棒.

稍等一下, 我们保存它, 然后编译这个项目. 这里我使用的命令是

```text
$ cargo build
```

我们会看到一些信息, 但是现在我们忽略它. 编译后的文件被保存在 `target/debug/hello` 中, 我们运行这个文件, 你将收到一条来自 Rust 的问候, 虽然问候语是你自己写的.

我们已经完成了 Rust 的第一步, 看吧, 我们用 Rust 写出了第一个程序. 这很棒, 我们将在下个课程中讲解 Rust 里的常量和变量.
