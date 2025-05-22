# Solana/程序开发入门/搭建初始目录结构

这篇文章, 我们来搭建一个干净的纯 rust 的 solana 程序项目目录结构, 作为我们的链上数据存储器项目的初始目录结构.

## 新建空白项目

我们先创建一个普通的 rust 库项目:

```sh
$ cargo new --lib pxsol-ss
$ cd pxsol-ss
```

这个项目会包含我们的主程序逻辑, 也就是将要部署到链上的合约. 项目名称 `pxsol-ss` 是 `pxsol-simple-storage` 的缩写.

## 配置编译目标

编辑 Cargo.toml, 添加如下设置:

```toml
[lib]
crate-type = ["cdylib", "lib"]
```

这个是告诉 cargo 我们要生成哪几种类型的 crate.

其中 `cdylib` 表示编译为一个 c 兼容的动态库. Solana 要求合约以 cdylib 形式编译为 `.so` 文件, 才能部署到链上. 这个 `.so` 文件会通过 `cargo build-bpf` 生成.

另外 `lib` 表示我们还希望编译成普通的 rust 库, 即 `.rlib`. 这有助于在本地测试时, 把合约逻辑当作普通 rust 模块来调用, 也方便写单元测试或集成测试.

总结的说: 您需要 cdylib 来部署, lib 来开发和测试.

## 添加依赖

我们需要引入 solana 的核心 sdk:

```toml
[dependencies]
solana-program = "1.18.0"
```

## 项目目录结构参考

最终的目录结构看起来可能像这样:

```
pxsol-ss/
├── Cargo.toml
└── src/
    └── lib.rs
```

其中 Cargo.toml 中的内容为

```toml
[package]
name = "pxsol-ss"
version = "0.1.0"
edition = "2021"

[lib]
crate-type = ["cdylib", "lib"]

[dependencies]
solana-program = "1.18"
```

## 创建 lib.rs 骨架

在 `src/lib.rs` 中, 先写一个最简单的入口:

```rs
solana_program::entrypoint!(process_instruction);

pub fn process_instruction(
    program_id: &solana_program::pubkey::Pubkey,
    accounts: &[solana_program::account_info::AccountInfo],
    data: &[u8],
) -> solana_program::entrypoint::ProgramResult {
    solana_program::msg!("Hello Solana!");
    Ok(())
}
```

这个程序目前什么也不做, 只会在调用时打印一句话. 但它已经可以被编译成 solana 支持的 bpf 程序了.

## 尝试编译

运行下面命令, 进行交叉编译:

```sh
$ cargo build-sbf -- -Znext-lockfile-bump
```

如果一切正常, 你会在 `target/deploy/` 目录下看到 `pxsol_ss.so` 文件, 这就是可以部署到 solana 的程序文件.

注意参数 `-Znext-lockfile-bump` 是一个临时参数, 因为 solana v1.18 依赖于 rustc 1.75, 如果您本地的 rust 版本大于 1.75, 存在一些兼容性问题, 因此需要传入该参数. 当您阅读本书时, 随着版本的更新, 此兼容问题很可能已经修复, 因此您也许可以尝试看看不加入该临时参数. 关于该问题的详细解释, 可以参考该 [github 页面](https://github.com/solana-foundation/anchor/issues/3392).

## 小结

到这里, 我们已经完成了一个最基本的, 使用原生 rust 编写的 solana 程序框架搭建. 这是实现我们用户自托管链上数据存储器的第一步.

下一步我们将实现账户派生和数据存储的逻辑, 开始真正和 solana 的账户模型打交道.
