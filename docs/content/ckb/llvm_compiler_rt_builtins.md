# CKB/将 LLVM compiler-rt builtins 编译为 RISC-V 静态库

## 什么是 compiler-rt/builtins

LLVM Compiler Runtime (compiler-rt) 是一个与 LLVM 编译器框架一起使用的项目, 它提供了一组与编译器生成的代码一起使用的运行时库函数. 这些运行时库函数的目的是提供对特定硬件体系结构和操作系统的低级支持, 以帮助编译器生成更高效, 更可靠的代码. 其中, compiler-rt 中的一部分是内建函数库(Builtins), 也称为编译器内建库.

内建函数库的作用包括以下几个方面:

- 低级操作支持: 内建函数库提供了对一些硬件操作的低级支持, 例如对特定指令的调用, 对硬件寄存器的操作等. 这对于一些需要与硬件直接交互的代码非常重要, 例如操作系统内核, 嵌入式系统或特定的系统级代码.
- 编译器优化支持: 编译器可以将一些高级操作转化为内建函数调用, 以便进行更好的代码优化. 这可以帮助生成更高效的机器码, 提高程序性能.
- 异常处理支持: 内建函数库还包括一些与异常处理相关的函数, 用于在运行时处理异常情况, 例如除零错误, 溢出等. 这些函数帮助编译器生成可靠的代码, 以应对各种运行时问题.
- 内存操作支持: 内建函数库还包括一些内存操作函数, 用于处理内存分配, 释放和复制等操作. 这有助于编译器生成更高效和可靠的内存操作代码.

## 将 builtins 库编译到 RISC-V

编译命令主要参考以下两个页面

0. <https://compiler-rt.llvm.org/>
0. <https://groups.google.com/g/llvm-dev/c/4KOCTVJVTT0>

```sh
$ git clone https://github.com/llvm/llvm-project --branch release/16.x --depth=1

$ mkdir build-compiler-rt
$ cd build-compiler-rt

$ FLAGS="--target=riscv64-unknown-elf -march=rv64imac -mabi=lp64"
$ cmake ../compiler-rt/lib/builtins \
    -DCMAKE_C_COMPILER=/usr/bin/clang-16 \
    -DCMAKE_AR=/usr/bin/llvm-ar-16 \
    -DCMAKE_NM=/usr/bin/llvm-nm-16 \
    -DCMAKE_RANLIB=/usr/bin/llvm-ranlib-16 \
    -DCMAKE_C_COMPILER_TARGET="riscv64-unknown-elf" \
    -DCMAKE_ASM_COMPILER_TARGET="riscv64-unknown-elf" \
    -DCOMPILER_RT_DEFAULT_TARGET_ONLY=ON \
    -DCMAKE_C_FLAGS="$FLAGS" \
    -DCMAKE_ASM_FLAGS="$FLAGS" \
    -DCOMPILER_RT_OS_DIR="baremetal" \
    -DCOMPILER_RT_BAREMETAL_BUILD=ON \
    -DLLVM_CONFIG_PATH=/usr/bin/llvm-config-16
$ make
```

编译结束后, 应当获得一个如下的目录结构, `libclang_rt.builtins-riscv64.a` 就是目标静态库文件.

```
build-compiler-rt/
├── CMakeCache.txt
├── CMakeFiles
├── cmake_install.cmake
├── lib
│   └── baremetal
│       └── libclang_rt.builtins-riscv64.a
├── Makefile
└── outline_atomic_helpers.dir
```
