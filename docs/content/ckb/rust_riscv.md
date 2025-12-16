# CKB/Rust 裸金属编程

我们将在本文中验证是否能用 Rust 编写一个 RISC-V 程序. 本文的目的是探索有关 Rust 交叉编译的功能, 并在编译 Rust 程序时为 RISC-V 提供确切的步骤和配置.

## 环境准备

为 Rust 安装 riscv64imac-unknown-none-elf target

```sh
$ rustup target add riscv64imac-unknown-none-elf
```

## 创建项目

创建一个名称为 rust-riscv64imac-unknown-none-elf 的 Rust 项目

```sh
$ cargo new --bin rust-riscv64imac-unknown-none-elf
```

为此项目指定默认编译目标. 创建 `.cargo/config.toml` 并写入以下内容

```toml
[build]
target = "riscv64imac-unknown-none-elf"
```

## 构建最小可行程序

将以下内容写入 `src/main.rs`, 这就是一个最小的可成功编译的 Rust 程序.

```rs
#![no_main]
#![no_std]

#[panic_handler]
fn panic_handler(_: &core::panic::PanicInfo) -> ! {
    loop {}
}
```

使用 `cargo build --release` 编译它, 并使用 `riscv64-unknown-elf-objdump` 检查编译结果

```sh
$ riscv64-unknown-elf-objdump -d target/riscv64imac-unknown-none-elf/release/rust-riscv64imac-unknown-none-elf

target/riscv64imac-unknown-none-elf/release/rust-riscv64imac-unknown-none-elf:     file format elf64-littleriscv
```

结果显示它是一个空的二进制文件, 内部甚至没有一条指令.

## 添加系统调用

我们日常使用的大多数程序都会返回退出码, 提示您程序是执行成功还是失败: 通常情况下, 0 代表成功, 任意非 0 值代表程序执行失败. 现在我们要在此 Rust 程序中增加一个功能: 它永远返回 42 退出码.

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

#[no_mangle]
pub extern "C" fn _start() {
    syscall_exit(42);
}
```

如果我们使用 `riscv64-unknown-elf-objdump` 重新检查它, 会发现它现在已经有代码块了.

```sh
$ riscv64-unknown-elf-objdump -d target/riscv64imac-unknown-none-elf/release/rust-riscv64imac-unknown-none-elf

target/riscv64imac-unknown-none-elf/release/rust-riscv64imac-unknown-none-elf:     file format elf64-littleriscv


Disassembly of section .text:

0000000000011120 <_ZN33rust_riscv64imac_unknown_none_elf12syscall_exit17ha3fdb87b6fbf14e5E>:
   11120:       05d00893                li      a7,93
   11124:       4581                    li      a1,0
   11126:       4601                    li      a2,0
   11128:       4681                    li      a3,0
   1112a:       4701                    li      a4,0
   1112c:       4781                    li      a5,0
   1112e:       4801                    li      a6,0
   11130:       00000073                ecall
   11134:       a001                    j       11134

0000000000011136 <_start>:
   11136:       02a00513                li      a0,42
   1113a:       00000097                auipc   ra,0x0
   1113e:       fe6080e7                jalr    -26(ra)
```

## 执行程序

我们可以使用 QEMU 模拟器来执行编译好的程序.

```sh
$ apt install qemu
$ qemu-riscv64 target/riscv64imac-unknown-none-elf/release/rust-riscv64imac-unknown-none-elf
$ echo $?
42
```

如果我们配置好相关的环境变量, 也可以直接使用 `cargo run` 来运行程序:

```sh
$ export CARGO_TARGET_RISCV64IMAC_UNKNOWN_NONE_ELF_RUNNER=qemu-riscv64
$ cargo run
$ echo $?
42
```

如果您希望省却环境变量的配置工作, 还可以选择将信息长久写入 `.cargo/config.toml` 配置文件中.

```sh
[target.riscv64imac-unknown-none-elf]
runner = "qemu-riscv64"
```

## 重构 panic_handler

在我们先前的最小可行程序中, panic_handler 是一个死亡循环: 这不是我们希望的. 重构它, 让它以 101 退出:

```rs
#[panic_handler]
fn panic_handler(_: &core::panic::PanicInfo) -> ! {
    // If the main thread panics it will terminate all your threads and end your program with code 101.
    // See: https://github.com/rust-lang/rust/blob/master/library/core/src/macros/panic.md
    syscall_exit(101)
}
```

为什么要在 panic 时让程序以 101 退出? 这其实并没有什么意义, 只是因为 Rust 目前就是这么做的: <https://github.com/rust-lang/rust/blob/master/library/core/src/macros/panic.md>

> If the main thread panics it will terminate all your threads and end your program with code 101.

## 命令行参数回显

我们将继续完善现有代码. 我们尝试从命令行解析参数, 然后在标准输出回显所有接收的参数. 为了实现此功能, 我们首先实现一个新的系统调用:

```rs
// Linux system calls for the RISC-V architecture: Write.
// See: https://github.com/westerndigitalcorporation/RISC-V-Linux/blob/master/riscv-pk/pk/syscall.h
fn syscall_write(fd: u64, buf: *const u8, count: u64) -> u64 {
    // Stdin is defined to be fd 0, stdout is defined to be fd 1, and stderr is defined to be fd 2.
    syscall(fd, buf as u64, count, 0, 0, 0, 0, 64)
}

```

随后我们在 `_start` 函数中从栈中解析参数, 并将参数传递给 `main` 函数. 函数 `main` 的签名会类似于 C 语言中的 `main` 函数. 要阅读以下代码, 您需要一些前置知识:

- [内联汇编](https://doc.rust-lang.org/nightly/rust-by-example/unsafe/asm.html)
- [参数在栈中的存储方式](https://www.win.tue.nl/~aeb/linux/hh/stack-layout.html)

```rs
#[no_mangle]
pub unsafe extern "C" fn _start() {
    core::arch::asm!(
        "lw a0,0(sp)", // Argc.
        "add a1,sp,8", // Argv.
        "li a2,0",     // Envp.
        "call main",
        "li a7, 93",
        "ecall",
    );
}

#[no_mangle]
unsafe extern "C" fn main(argc: u64, argv: *const *const i8) -> u64 {
    for i in 1..argc {
        let argn = core::ffi::CStr::from_ptr(argv.add(i as usize).read());
        let argn = argn.to_bytes();
        syscall_write(1, argn.as_ptr(), argn.len() as u64);
        if i != argc - 1 {
            syscall_write(1, [32].as_ptr(), 1);
        }
    }
    syscall_write(1, [10].as_ptr(), 1);
    return 0;
}
```

测试:

```sh
$ cargo run -- Hello World!
   Compiling rust-riscv64imac-unknown-none-elf v0.1.0 (/tmp/rust-riscv64imac-unknown-none-elf)
    Finished dev [unoptimized + debuginfo] target(s) in 0.09s
     Running `qemu-riscv64 target/riscv64imac-unknown-none-elf/debug/rust-riscv64imac-unknown-none-elf Hello 'World'\!''`
Hello World!
```

## 动态内存分配: 使用 Vec 和 String 简化处理流程

在 Rust 的 no-std 模式下, 由于 Vec 和 String 被定义在 `std::vec` 和 `std::string`, 因此您无法使用他们. 为了解决这个问题, 您首先需要定义一个 `global_allocator`. 将以下代码加入 `Cargo.toml`:

```toml
[dependencies]
linked_list_allocator = "*"
```

同时将以下代码写入 `src/main.rs`. 注意, 您可以根据硬件条件自定义 `HEAPS` 的大小, 在本示例中, 我仅仅为其定义了 1024 个字节.

```rs
static mut HEAPS: [u8; 1024] = [0; 1024];
#[global_allocator]
static ALLOC: linked_list_allocator::LockedHeap = linked_list_allocator::LockedHeap::empty();
```

从 `alloc` 包引入 `Vec` 和 `String`:

```rs
extern crate alloc;
use alloc::string::String;
use alloc::vec::Vec;
```

重构 `main` 函数. 在 main 函数的起始处, 我们首先需要初始化 `ALLOC`. 然后, 就可以在代码中使用 `Vec` 和 `String` 了.

```rs
#[no_mangle]
unsafe extern "C" fn main(argc: u64, argv: *const *const i8) -> u64 {
    unsafe {
        ALLOC.lock().init(HEAPS.as_mut_ptr(), 1024);
    }
    let mut args = Vec::new();
    for i in 1..argc {
        let argn = core::ffi::CStr::from_ptr(argv.add(i as usize).read());
        let argn = String::from(argn.to_string_lossy());
        args.push(argn);
    }
    let mut data = args.join(" ");
    data.push('\n');
    syscall_write(1, data.as_ptr(), data.len() as u64);
    return 0;
}
```

测试:

```sh
$ cargo run -- Hello World!
   Compiling rust-riscv64imac-unknown-none-elf v0.1.0 (/tmp/rust-riscv64imac-unknown-none-elf)
    Finished dev [unoptimized + debuginfo] target(s) in 0.15s
     Running `qemu-riscv64 target/riscv64imac-unknown-none-elf/debug/rust-riscv64imac-unknown-none-elf Hello 'World'\!''`
Hello World!
```

## 完整代码参考

```rs
#![no_main]
#![no_std]

extern crate alloc;
use alloc::string::String;
use alloc::vec::Vec;

static mut HEAPS: [u8; 1024] = [0; 1024];
#[global_allocator]
static ALLOC: linked_list_allocator::LockedHeap = linked_list_allocator::LockedHeap::empty();

#[panic_handler]
fn panic_handler(_: &core::panic::PanicInfo) -> ! {
    // If the main thread panics it will terminate all your threads and end your program with code 101.
    // See: https://github.com/rust-lang/rust/blob/master/library/core/src/macros/panic.md
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

// Linux system calls for the RISC-V architecture: Write.
// See: https://github.com/westerndigitalcorporation/RISC-V-Linux/blob/master/riscv-pk/pk/syscall.h
fn syscall_write(fd: u64, buf: *const u8, count: u64) -> u64 {
    // Stdin is defined to be fd 0, stdout is defined to be fd 1, and stderr is defined to be fd 2.
    syscall(fd, buf as u64, count, 0, 0, 0, 0, 64)
}

#[no_mangle]
pub unsafe extern "C" fn _start() {
    core::arch::asm!(
        "lw a0,0(sp)", // Argc.
        "add a1,sp,8", // Argv.
        "li a2,0",     // Envp.
        "call main",
        "li a7, 93",
        "ecall",
    );
}

#[no_mangle]
unsafe extern "C" fn main(argc: u64, argv: *const *const i8) -> u64 {
    unsafe {
        ALLOC.lock().init(HEAPS.as_mut_ptr(), 1024);
    }
    let mut args = Vec::new();
    for i in 1..argc {
        let argn = core::ffi::CStr::from_ptr(argv.add(i as usize).read());
        let argn = String::from(argn.to_string_lossy());
        args.push(argn);
    }
    let mut data = args.join(" ");
    data.push('\n');
    syscall_write(1, data.as_ptr(), data.len() as u64);
    return 0;
}
```

完整项目托管于 Github: <https://github.com/libraries/rust-riscv64imac-unknown-none-elf>

## 参考

- [1] [Build CKB contract with Rust - part 1, jjy](https://talk.nervos.org/t/build-ckb-contract-with-rust-part-1/4064)
- [2] [RISC-V Bytes: Rust Cross-Compilation, DANIEL MANGUM](https://danielmangum.com/posts/risc-v-bytes-rust-cross-compilation/)
