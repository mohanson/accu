# CKB/CKB-VM/使用标准 Rust 环境编写 CKB 脚本(二)

在上一篇文章中, 我们已经完成了最小可运行脚本. 但要顺畅地编写 Rust 脚本, 还需要启用动态内存分配. 大多数人已经习惯在 Rust 中使用 `String` 和 `Vec`, 但在 `no_std` 环境下, 这些类型默认不可用.

如果您试图编写以下代码, 就会遇到编译错误:

```rs
#[unsafe(no_mangle)]
pub extern "C" fn _start() {
    let s = String::from("Hello, CKB-VM!");
    syscall_exit(0);
}
```

```sh
$ cargo run
   Compiling always_success v0.1.0 (/tmp/always_success)
error[E0433]: cannot find type `String` in this scope
  --> src/main.rs:35:13
   |
35 |     let s = String::from("Hello, CKB-VM!");
   |             ^^^^^^ use of undeclared type `String`

For more information about this error, try `rustc --explain E0433`.
error: could not compile `always_success` (bin "always_success") due to 1 previous error
```

为了解决这个问题, 我们需要从 `alloc` crate 引入 `String`:

```rs
extern crate alloc;
use alloc::string::String;

#[unsafe(no_mangle)]
pub extern "C" fn _start() {
    let s = String::from("Hello, CKB-VM!");
    syscall_exit(0);
}
```

但这还不够, 因为 `String` 依赖全局分配器才能工作. 如果我们直接编译上面的代码, 就会遇到另一个编译错误:

```sh
$ cargo run
   Compiling always_success v0.1.0 (/tmp/always_success)
error: no global memory allocator found but one is required; link to std or add `#[global_allocator]` to a static item that implements the GlobalAlloc trait

warning: unused variable: `s`
  --> src/main.rs:38:9
   |
38 |     let s = String::from("Hello, CKB-VM!");
   |         ^ help: if this is intentional, prefix it with an underscore: `_s`
   |
   = note: `#[warn(unused_variables)]` (part of `#[warn(unused)]`) on by default

warning: `always_success` (bin "always_success") generated 1 warning
error: could not compile `always_success` (bin "always_success") due to 1 previous error; 1 warning emitted
```

为了解决上面的问题, 核心步骤有 3 个:

1. 引入分配器实现;
2. 提供一段可用作堆的内存;
3. 在程序入口处初始化分配器.

## 添加分配器依赖

在 `Cargo.toml` 中加入依赖:

```toml
[dependencies]
linked_list_allocator = "*"
```

> 为了保持示例简洁, 这里沿用 `"*"` 写法. 在生产项目中建议固定版本号, 以避免构建结果随时间变化.

`linked_list_allocator` 是一个基于链表的堆分配器实现. 它本身偏教学用途, 不建议直接用于生产环境, 但实现足够简单, 很适合在示例中演示如何启用堆分配器.

## 定义堆和全局分配器

在 `src/main.rs` 顶部增加以下代码:

```rs
#![no_main]
#![no_std]

extern crate alloc;
use alloc::string::String;
use alloc::vec::Vec;

static mut HEAPS: [u8; 1024] = [0; 1024];
#[global_allocator]
static ALLOC: linked_list_allocator::LockedHeap = linked_list_allocator::LockedHeap::empty();
```

这里的 `HEAPS` 是一段静态字节数组, 作为示例堆空间. 1024 字节仅用于演示, 你可以按脚本复杂度调整大小, 但不建议超过 2MB. 原因是 CKB-VM 的总内存限制为 4MB, 堆空间过大可能导致整体内存不足.

## 初始化分配器

仅声明 `#[global_allocator]` 还不够, 还需要在入口逻辑中初始化堆, 否则运行时仍无法正常分配内存. 例如:

```rs
#[unsafe(no_mangle)]
unsafe extern "C" fn main(argc: u64, argv: *const *const i8) -> u64 {
   unsafe {
      ALLOC.lock().init(HEAPS.as_mut_ptr(), 1024);
   }

   let mut args = Vec::new();
   for i in 1..argc {
      let argn = core::ffi::CStr::from_ptr(argv.add(i as usize).read());
      args.push(String::from(argn.to_string_lossy()));
   }

   let mut data = args.join(" ");
   data.push('\n');
   syscall_write(1, data.as_ptr(), data.len() as u64);
   0
}
```

完成这一步后, `String` 和 `Vec` 才能真正可用.

## 小结

动态内存分配是 CKB-VM 脚本开发中的关键能力. 如果没有它, 很多复杂逻辑都难以实现, 例如参数解析、序列化, 或引入部分依赖堆内存的数据结构与库.
