# Solana/程序开发入门/升级程序

在 solana 中, 我们可以替换已部署的程序的代码. 不过要注意, solana 程序的部署和更新存在几个不同的版本演进, 在早期的版本里, 程序是不可升级的.

## 如何升级程序

升级程序可使用 `pxsol.wallet.Wallet.program_update()` 接口完成. 您可以修改我们的链上数据存储器代码, 然后使用如下的命令来升级链上程序版本. 升级程序不会修改程序的地址.

```py
import pathlib
import pxsol

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))
program_pubkey = pxsol.core.PubKey.base58_decode('DVapU9kvtjzFdH3sRd3VDCXjZVkwBR6Cxosx36A5sK5E')
program_data = pathlib.Path('target/deploy/pxsol_ss.so').read_bytes()
ada.program_update(program_pubkey, program_data)
```

## Solana 程序最早是不可更改的

Solana 早期负责**管理程序的程序**叫做 bpf loader, 也叫做 `v1`. 使用它部署的程序, 您的程序会被标记为所有数据不可写, 所有代码不可修改, 同时程序账户的 executable 被设置为 true. 所以这种部署方式下, 程序不能更新! 如果您想升级, 就只能部署一个新的程序, 并更新所有依赖它的账户或前端逻辑, 这无疑非常麻烦.

## 演进史

Solana 的 bpf loader 是一个特殊的原生程序, 专门用来加载并执行您上传的 bpf 字节码. Solana 发展过程中经历了三个主要版本的 loader:

|        Loader 名称        |                     地址                      |               特点               |
| ------------------------- | --------------------------------------------- | -------------------------------- |
| BPFLoader (v1)            | `BPFLoader1111111111111111111111111111111111` | 最早期版本, 部署后不可升级       |
| BPFLoader2 (v2)           | `BPFLoader2111111111111111111111111111111111` | 支持更高效的加载, 但依旧不可升级 |
| BPFLoaderUpgradeable (v3) | `BPFLoaderUpgradeab1e11111111111111111111111` | 当前默认, 支持程序升级和权限控制 |

也就是从 v3 开始, solana 引入了可升级程序的概念, 并将其作为**默认部署**方式.

## 可升级程序的结构图

Pxsol 默认使用 v3 来部署程序. 这会自动创建两个账户:

|       账户类型       |            作用            |
| -------------------- | -------------------------- |
| Program account      | 主地址, 对外暴露的程序入口 |
| Program data account | 存储实际代码字节码, 可变   |

```text
Program ID (e.g., MyProgram111...)
│
├──> Program Account
│     └── owner: BPFLoaderUpgradeable
│     └── executable: true
│     └── points to:
│
└──> ProgramData Account
      └── contains: .so 字节码
      └── contains: upgrade_authority pubkey
```

所谓的升级程序, 其实就是修改第二个账户的内容.
