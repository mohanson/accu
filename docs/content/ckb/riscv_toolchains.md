# CKB/RISC-V 工具链安装

## 通过源码编译

以下命令可以安装 RV64GC 版本的工具链.

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

## 编译并运行 RISC-V 程序

编写如下测试代码:

```c
int main() {
  return 42;
}
```

我们现在有两种方式编译代码. 首先使用 GCC 对其进行编译:

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

由于我们在编译工具链的时候添加了 `--enable-llvm` 参数, 所以也可以使用 Clang 编译:

```sh
$ clang --target=riscv64-unknown-elf
        -march=rv64imac_zba_zbb_zbc_zbs
        --sysroot=/home/ubuntu/app/riscv/riscv64-unknown-elf
        -o main main.c
```

注意, 如果你没有添加 `--enable-llvm` 参数, 而是自行安装了 Clang, 也是可以进行编译的. 假如使用 LLVM 的官方安装脚本 `https://apt.llvm.org/llvm.sh` 进行安装, 那么编译命令要额外加上 `--gcc-toolchain=/home/ubuntu/app/riscv`.

```sh
$ clang --target=riscv64-unknown-elf
        -march=rv64imac_zba_zbb_zbc_zbs
        --sysroot=/home/ubuntu/app/riscv/riscv64-unknown-elf
        --gcc-toolchain=/home/ubuntu/app/riscv
        -o main main.c
```
