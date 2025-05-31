# Solana/程序开发入门/编译并部署程序

## 编译

使用下面的命令编译程序代码.

```sh
$ cargo build-sbf -- -Znext-lockfile-bump
```

## 部署程序

使用下面的 python 代码部署目标程序上链:

```py
import pathlib
import pxsol

# Enable log
pxsol.config.current.log = 1

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))

program_data = pathlib.Path('target/deploy/pxsol_ss.so').read_bytes()
program_pubkey = ada.program_deploy(bytearray(program_data))
print(program_pubkey) # DVapU9kvtjzFdH3sRd3VDCXjZVkwBR6Cxosx36A5sK5E
```

在部署过程中, 您会在日志中看到大量的交易. 在 solana 上部署一个程序和其他区块链(如以太坊)相比, 流程略有不同. 部署过程分为多个步骤, 每一步基本上对应一个或多个交易:

0. 创建一个程序账户.
1. 分段上传程序代码(分片写入). Solana 的单笔交易大小有限, 一个交易序列化后最多不超过 1232 字节, 而你的程序代码可能有几万字节或更多. 所以必须把 bpf 字节码分片后, 分多次交易写入账户的数据区.
2. 所有字节都写完之后, 需要最后一步: 调用 bpf loader 程序的 finalize 方法, 把账户标记为 finalized. 从这个时候开始, 它才会变成一个真正的 solana 程序了.

虽然流程复杂一些, 但这是高性能设计的一部分.
