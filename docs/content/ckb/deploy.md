# CKB/部署脚本

本文涵盖了使用 ckb-cli 部署 CKB 脚本的方法, 涉及 ckb-cli 的基本使用, 以及如何将其用于构建 CKB 应用程序. 在开始本文内容之前, 首先确保您已完成了开发网络的搭建.

我们将部署一个简单的脚本, 该脚本将始终返回 0. 我们使用 always_success 为其命名.

```c
int main() {
    return 0;
}
```

这是一个 C 程序. 我们需要使用 riscv64-unknown-elf-gcc 编译它, 获得二进制文件. 如果您还未曾使用过 riscv64-unknown-elf-gcc, 可以在[此处](https://github.com/riscv-collab/riscv-gnu-toolchain)获取关于它的一些信息. 概括的说, 它和我们平时使用的 gcc 非常相似, 区别在于它的编译结果是 RISC-V 机器码.

```sh
$ riscv64-unknown-elf-gcc -o always_success always_success.c
```

在完成以上步骤之后, 我们将尝试把 always_success 部署到开发网络. 使用 ckb-cli 创建一个配置文件.

```sh
$ ckb-cli deploy init-config --deployment-config deployment.toml
```

在执行完以上命令后, 当前目录下可以找到一个新创建的 deployment.toml 文件. 对它做一些修改. 我们的目的是创建一个 cell, cell 的内容是 always_success 的二进制程序, 并且该 cell 使用 secp256k1(code_hash = 0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8) 锁定, 只有我们的矿工账户 0x75178f34549c5fe9cd1a0c57aebd01e7ddf9249e 可以解锁它.

```toml
[[cells]]
name = "always_success"
enable_type_id = true
location = { file = "always_success" }

[lock]
code_hash = "0x9bd7e06f3ecf4be0f2fcd2188b23f1b9fcc88e5d4b65a8637b17723bbda3cce8"
args = "0x75178f34549c5fe9cd1a0c57aebd01e7ddf9249e"
hash_type = "type"
```

使用 ckb-cli 生成交易信息.

```sh
$ mkdir migrations
$ ckb-cli deploy gen-txs \
    --deployment-config ./deployment.toml \
    --migration-dir ./migrations \
    --from-address ckt1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqt4z78ng4yutl5u6xsv27ht6q08mhujf8s2r0n40 \
    --sign-now \
    --info-file info.json
```

然后, 对交易进行签名.

```sh
$ ckb-cli deploy sign-txs \
    --from-account ckt1qzda0cr08m85hc8jlnfp3zer7xulejywt49kt2rr0vthywaa50xwsqt4z78ng4yutl5u6xsv27ht6q08mhujf8s2r0n40 \
    --add-signatures \
    --info-file info.json
```

将签名后的交易发布到开发网络.

```sh
$ ckb-cli deploy apply-txs --migration-dir ./migrations --info-file info.json
```

发布交易后我们将得到一个交易哈希. 通过该交易哈希可查询该交易的信息.

```sh
$ ckb-cli rpc get_transaction  --hash 0x1213465d98cdee9f8c05afbe6882b23a08504676cae8540b068d19a1850905ed
```
