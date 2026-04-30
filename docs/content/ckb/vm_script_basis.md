# CKB/CKB-VM/使用标准 Rust 环境编写 CKB 脚本(一)

说实话, 我见过太多教程, 它们总是在一开始就要求我安装一大堆工具链, 还要配置环境变量, 甚至还要安装一个虚拟机. 这总会让我觉得这件事太麻烦, 麻烦到不想开始, 因为我可能只是想先试一下, 不一定会长期使用. 我常常会担心这些事情:

- 这些安装命令会不会弄坏我的系统?
- 会不会和我系统上已经安装的工具冲突?
- 我可以轻松地移除这些工具吗?

很不幸, 这些担心都很有道理. 绝大多数教程开头提供的"快速安装"命令都不带卸载说明, 这就意味着一旦你敲下这些命令, 就很难彻底移除它们. 这也是为什么我决定在本文中使用标准的 Rust 环境来编写 CKB 脚本: 我们不需要安装任何额外的工具链或虚拟机, 也不需要担心复杂的环境配置. 只要你已经安装了 Rust, 就可以直接开始编写 CKB 脚本.

> 教程并非完全只依赖 Rust: 你还需要安装 LLVM 来检查编译结果, 以及安装 QEMU 来执行编译好的程序. 不过这两者都是很常见的工具, 你可以通过系统包管理器安装它们, 通常既安全, 也容易移除.

## 环境准备

首先, 我们需要为 Rust 安装 `riscv64imac-unknown-none-elf` target, 以便编译出标准 RISC-V 二进制文件. CKB-VM 能执行任何符合 RISC-V 规范的二进制文件, 因此我们不需要安装任何特定于 CKB-VM 的工具链.

```sh
$ rustup target add riscv64imac-unknown-none-elf

# 使用下面的命令可以移除这个 target, 以节省磁盘空间.
# rustup target remove riscv64imac-unknown-none-elf
```

以上就是全部环境准备工作. 现在, 你已经可以开始使用 Rust 编写 CKB 脚本了.

## 创建项目

我们准备实现一个简单的 CKB 脚本, 它总是执行成功, 也就是返回 0. 这意味着任何人都不需要满足额外条件就能通过该脚本, 因此我们将其命名为 `always_success`. 如果把这个脚本作为某个 Cell 的 Lock Script, 那么任何人都可以拿走这个 Cell 上的资产. 通常来说, 这类脚本非常危险, 几乎不会在生产环境中使用, 也没有实际业务价值; 但它非常适合用来演示如何使用标准 Rust 编写 CKB 脚本.

首先, 创建一个名为 `always_success` 的 Rust 项目:

```sh
$ cargo new --bin always_success
```

为该项目指定默认编译目标. 创建 `.cargo/config.toml` 并写入以下内容:

```toml
[build]
target = "riscv64imac-unknown-none-elf"
```

这样, 当你使用 `cargo build` 或 `cargo run` 时, Cargo 会自动使用 `riscv64imac-unknown-none-elf` 作为编译目标, 从而省去每次手动指定 `--target` 参数的麻烦.

## 构建最小可行程序

将以下内容写入 `src/main.rs`, 这就是一个最小的, 可成功编译的 Rust 程序.

```rs
#![no_main]
#![no_std]

#[panic_handler]
fn panic_handler(_: &core::panic::PanicInfo) -> ! {
    loop {}
}
```

```sh
$ cargo build --release
   Compiling always_success v0.1.0 (/tmp/always_success)
    Finished `release` profile [optimized] target(s) in 0.11s
```

这个程序虽然可以成功编译, 但它没有实际功能, 因此也无法正常结束执行. 我们可以使用 `llvm-objdump` 检查编译结果, 确认它确实是一个极简二进制文件. 如果你没有安装 `llvm-objdump`, 可以使用 `sudo apt install llvm` 安装.

```sh
$ llvm-objdump -d target/riscv64imac-unknown-none-elf/release/always_success

target/riscv64imac-unknown-none-elf/release/always_success:     file format elf64-littleriscv
```

## 添加退出码

我们日常使用的大多数程序都会返回退出码, 用于提示程序执行成功还是失败: 通常情况下, 0 代表成功, 任意非 0 值代表失败. 在没有操作系统的环境中, 退出码通常通过一个特殊的系统调用返回. 在 RISC-V 架构中, 这个系统调用被称为 `ecall`, 它允许程序向宿主发出请求, 以执行特定操作. 在这个例子中, 我们将使用 `ecall` 返回退出码.

将下面的代码写入 `src/main.rs`, 并重新编译.

```rs
fn syscall(mut a0: u64, a1: u64, a2: u64, a3: u64, a4: u64, a5: u64, a6: u64, a7: u64) -> u64 {
    unsafe {
        core::arch::asm!(
          "ecall",
          inout("a0") a0,
          in("a1") a1,
          in("a2") a2,
          in("a3") a3,
          in("a4") a4,
          in("a5") a5,
          in("a6") a6,
          in("a7") a7
        )
    }
    a0
}

// Linux system calls for the RISC-V architecture: Exit.
// See: https://github.com/westerndigitalcorporation/RISC-V-Linux/blob/master/riscv-pk/pk/syscall.h
fn syscall_exit(code: u64) -> ! {
    syscall(code, 0, 0, 0, 0, 0, 0, 93);
    loop {}
}

#[unsafe(no_mangle)]
pub extern "C" fn _start() {
    syscall_exit(0);
}
```

我们再次使用 `llvm-objdump` 检查, 可以发现它现在已经包含可执行代码了.

```sh
$ llvm-objdump -d target/riscv64imac-unknown-none-elf/release/always_success

target/riscv64imac-unknown-none-elf/release/always_success:     file format elf64-littleriscv

Disassembly of section .text:

0000000000011158 <_start>:
   11158: 05d00893      li      a7, 0x5d
   1115c: 4581          li      a1, 0x0
   1115e: 4601          li      a2, 0x0
   11160: 4681          li      a3, 0x0
   11162: 4701          li      a4, 0x0
   11164: 4781          li      a5, 0x0
   11166: 4801          li      a6, 0x0
   11168: 4501          li      a0, 0x0
   1116a: 00000073      ecall
   1116e: a001          j       0x1116e <_start+0x16>
```

## 执行程序

现在, 我们已经成功编译出一个可执行程序. 整个过程没有使用任何 CKB 特定工具或依赖库, 全部基于标准 Rust 环境和通用开源工具链. 这展示了 CKB-VM 的兼容性: 只要你能编译出符合 RISC-V 规范的二进制文件, 就可以在 CKB-VM 上执行它.

你也许会想, 既然已经编译出了可执行程序, 是不是就可以直接在 CKB-VM 上运行? 确实可以, 但我不希望本文依赖任何 CKB 专用工具, 所以这里不介绍如何在 CKB-VM 上执行它, 而是介绍如何在通用 RISC-V 模拟器中运行.

QEMU 是一个开源且通用的模拟器与虚拟化工具. 它能够在你现有的电脑(如 x86 Windows/Linux)上虚拟出另一种完全不同架构的计算机环境(如 RISC-V 或 ARM). 这使得我们在没有真实 RISC-V 硬件的情况下, 也能直接在本机执行编译好的 RISC-V 程序.

```sh
$ sudo apt install qemu-user-static
$ qemu-riscv64-static target/riscv64imac-unknown-none-elf/release/always_success
$ echo $?
0
```

如果配置好相关环境变量, 也可以直接使用 `cargo run` 运行程序:

```sh
$ export CARGO_TARGET_RISCV64IMAC_UNKNOWN_NONE_ELF_RUNNER=qemu-riscv64-static
$ cargo run
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.01s
     Running `qemu-riscv64-static target/riscv64imac-unknown-none-elf/debug/always_success`
$ echo $?
0
```

如果你希望省去环境变量配置, 也可以把配置长期写入 `.cargo/config.toml`, 添加下面内容即可.

```toml
[target.riscv64imac-unknown-none-elf]
runner = "qemu-riscv64-static"
```

这样, 你只需要执行 `cargo run` 就可以直接运行程序.

```sh
$ cargo run
    Finished `dev` profile [unoptimized + debuginfo] target(s) in 0.01s
     Running `qemu-riscv64-static target/riscv64imac-unknown-none-elf/debug/always_success`
$ echo $?
0
```

## 重构 panic_handler

在此前的最小可行程序中, `panic_handler` 是一个死循环, 这通常不是我们希望的行为. 我们可以重构它, 让它以 101 退出:

```rs
#[panic_handler]
fn panic_handler(_: &core::panic::PanicInfo) -> ! {
    // If the main thread panics it will terminate all your threads and end your program with code 101.
    // See: https://github.com/rust-lang/rust/blob/master/library/core/src/macros/panic.md
    syscall_exit(101)
}
```

为什么要在 panic 时让程序以 101 退出? 这里主要是为了与 Rust 的默认约定保持一致: <https://github.com/rust-lang/rust/blob/main/library/core/src/macros/panic.md>

> If the main thread panics it will terminate all your threads and end your program with code 101.

## 完整代码参考

**.cargo/config.toml**

```toml
[build]
target = "riscv64imac-unknown-none-elf"

[target.riscv64imac-unknown-none-elf]
runner = "qemu-riscv64-static"
```

**src/main.rs**

```rs
#![no_main]
#![no_std]

#[panic_handler]
fn panic_handler(_: &core::panic::PanicInfo) -> ! {
    syscall_exit(101)
}

fn syscall(mut a0: u64, a1: u64, a2: u64, a3: u64, a4: u64, a5: u64, a6: u64, a7: u64) -> u64 {
    unsafe {
        core::arch::asm!(
          "ecall",
          inout("a0") a0,
          in("a1") a1,
          in("a2") a2,
          in("a3") a3,
          in("a4") a4,
          in("a5") a5,
          in("a6") a6,
          in("a7") a7
        )
    }
    a0
}

// Linux system calls for the RISC-V architecture: Exit.
// See: https://github.com/westerndigitalcorporation/RISC-V-Linux/blob/master/riscv-pk/pk/syscall.h
fn syscall_exit(code: u64) -> ! {
    syscall(code, 0, 0, 0, 0, 0, 0, 93);
    loop {}
}

#[unsafe(no_mangle)]
pub extern "C" fn _start() {
    syscall_exit(0);
}
```

## 小结

在本文中, 我们展示了如何使用标准 Rust 环境编写 CKB 脚本, 以及如何用 QEMU 执行编译后的 RISC-V 程序. 通过这个示例可以看到 CKB-VM 的兼容性, 这为后续开发带来了很高的灵活性: 我们可以使用自己熟悉的工具链和开发环境来编写 CKB 脚本, 而不必依赖某种特定的黑箱工具.

在下一节中, 我们将介绍如何通过引入内存分配器来支持动态内存分配, 以便使用 Rust 的一些高级数据结构, 例如 `String` 和 `Vec`, 从而让 CKB 脚本更丰富, 功能更完整.
