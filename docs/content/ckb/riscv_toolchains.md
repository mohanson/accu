# CKB/RISC-V 工具链安装

CKB 早期使用 riscv-gnu-toolchain 来进行 C 合约编译, 在 2023 年之后新项目原则上均采用 clang. 下面我会分别介绍一下两种方案的详细步骤, 来展示它们的不同.

## 使用 riscv-gnu-toolchain

以下命令可以安装 RV64GC 版本的工具链. 如果安装过程遇到问题, 可以前往 <https://github.com/riscv/riscv-gnu-toolchain> 页面寻找解决方案.

```sh
$ sudo apt install autoconf automake autotools-dev curl libmpc-dev libmpfr-dev libgmp-dev gawk build-essential bison flex texinfo gperf libtool patchutils bc zlib1g-dev libexpat-dev ninja-build git cmake libglib2.0-dev
```

```sh
$ git clone https://github.com/riscv/riscv-gnu-toolchain
$ cd riscv-gnu-toolchain
$ git checkout 2023.09.13
$ git submodule update --init --recursive
# 添加参数 --with-arch 可以选择要编译的指令集扩展
#   --with-arch=rv64imac
#   --with-arch=rv64imac_zba_zbb_zbc_zbs
# 添加参数 --enable-llvm 允许使用 clang 构建 C 和 C++ 应用程序
$ ./configure --prefix=/home/ubuntu/app/riscv --with-arch=rv64imac_zba_zbb_zbc_zbs --enable-llvm
$ make -j $(nproc)

# 额外安装模拟器 qemu
$ make report SIM=qemu
# 额外安装模拟器 spike
$ make report SIM=spike
```

安装完成工具链后, 编写如下测试代码:

```c
int main() {
  return 42;
}
```

使用 riscv64-unknown-elf-gcc 对其进行编译, 并使用 Spike 或者 Qemu 运行它.

```sh
$ riscv64-unknown-elf-gcc -o main main.c

# 使用 Spike 运行
# 使用参数 --isa 选择扩展
#   --isa RV64GC_ZBA_ZBB_ZBC_ZBS
#   --isa RV64GC
$ spike --isa $ISA pk64 main
$ echo $?

# 使用 Qemu 运行
$ qemu-riscv64 main
$ echo $?
```

## 使用 clang in riscv-gnu-toolchain

由于我们在编译工具链的时候添加了 `--enable-llvm` 参数, 所以也可以使用附带安装的 Clang 进行编译. 注意此处的 Clang 和你通过系统包管理工具安装的 Clang 是不同的.

```sh
$ clang --target=riscv64
        -march=rv64imac_zba_zbb_zbc_zbs
        --sysroot=/home/ubuntu/app/riscv/riscv64-unknown-elf
        -o main main.c
```

## 使用 clang

如果我们没有在安装 riscv-gnu-toolchain 添加 `--enable-llvm` 参数, 而是自行安装了 Clang, 也是可以进行编译的. 假如使用 LLVM 的官方安装脚本 `https://apt.llvm.org/llvm.sh` 进行安装, 那么编译命令只需要额外加上 `--gcc-toolchain=/home/ubuntu/app/riscv` 即可.

```sh
$ clang --target=riscv64
        -march=rv64imac_zba_zbb_zbc_zbs
        --sysroot=/home/ubuntu/app/riscv/riscv64-unknown-elf
        --gcc-toolchain=/home/ubuntu/app/riscv
        -o main main.c
```

可以看到上面的命令仍然使用的是 riscv-gnu-toolchain 的 stdlib. 我们可使用 [ckb-c-stdlib](https://github.com/nervosnetwork/ckb-c-stdlib) 彻底替换掉它们, 下载 ckb-c-stdlib 后使用如下命令进行编译:

```sh
$ clang --target=riscv64
        -march=rv64imc
        -nostdlib
        -ffunction-sections
        -I/home/ubuntu/src/ckb-c-stdlib/
        -I/home/ubuntu/src/ckb-c-stdlib/libc
        -Wl,--gc-sections
        -o main main.c
```
