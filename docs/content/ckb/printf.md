# CKB/使用 printf 函数进行代码调试

[CKB Standalone Debugger](https://github.com/nervosnetwork/ckb-standalone-debugger) 是我们开发的一个 CKB 调试工具集合, 而其中 ckb-debugger 是最广泛被使用的一款工具. 通过 ckb-debugger, 你可以直接运行一个 RISC-V 程序, 或是在链下执行一个 CKB 交易以协助开发或者调试.

在编写 C 合约代码时, 我们可以使用 printf 函数向 ckb-debugger 打印调试信息. 首先下载 [ckb-c-stdlib](https://github.com/nervosnetwork/ckb-c-stdlib):

```sh
$ git clone https://github.com/nervosnetwork/ckb-c-stdlib
```

编写一个测试文件, 暂时命名为 `main.c`

```c
#include "ckb_syscalls.h"

int main() {
  printf("Hello World!");
}
```

使用 clang 对其进行编译. 注意编译参数, 必须添加 `-DCKB_C_STDLIB_PRINTF=1` 才能使用 `printf` 函数. 相关条件编译代码可在 `ckb-c-stdlib/libc/src/impl.c` 中找到.

```sh
$ clang --target=riscv64 -march=rv64imac_zba_zbb_zbc_zbs \
      -nostdinc -nostdlib \
      -DCKB_C_STDLIB_PRINTF=1 \
      -I ckb-c-stdlib/libc -I ckb-c-stdlib \
      -o main \
      main.c
```

待编译完成后, 即可使用 ckb-debugger 执行程序, 执行命令如下:

```sh
$ ckb-debugger --bin main

Hello World!
Run result: 0
Total cycles consumed: 7059(6.9K)
Transfer cycles: 4537(4.4K), running cycles: 2522(2.5K)
```
