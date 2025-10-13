# Solana/更多开发者工具/Pinocchio? Pinocchio!

Solana 开发团队正在积极打造更多工具, 帮助开发者更高效地编写和测试链上程序. 其中一个有趣的项目是 [pinocchio](https://github.com/anza-xyz/pinocchio), 它在本书创作期间首次发布版本, 因此我也对它进行了探索, 并且迫不及待的想将它纳入本书的内容里.

## Pinocchio?

Pinocchio 是一个零依赖(zero-dependency), no_std 的 rust 库, 用来编写 solana 链上程序. 它不依赖 [solana-program](https://crates.io/crates/solana-program), 而是直接契合 svm loader 与程序之间的原始 abi(一个序列化后的字节数组), 通过零拷贝解析把输入映射为程序可用的类型, 从而在以下方面受益:

- 更小二进制: 避免引入庞大的 sdk 依赖
- 更低资源消耗: 入口解析与 cpi 过程更省计算
- 更强掌控: 按需解析输入, 可禁用内存分配器(allocator), 强化可预测性
- 适合追求极致体积与性能, 或被依赖地狱困扰的项目

零依赖是 pinocchio 的核心卖点, 使用 pinocchio 时不像使用 solana-program, 不需要引入上百个依赖, 但它的功能确是和 solana-program 相当的. 它提供了类似的类型与功能, 在实际开发过程中可以平替 solana-program, 也可以很方便的从现有的 solana-program 代码迁移过来.

但是需要搞清楚一个区别, pinocchio 和 solana-program 一样, 是一个链上程序开发库, 而不是一个完整的类似 anchor 的开发框架. 它不提供类似 anchor 的宏与代码生成, 也不提供类似 anchor 的本地测试与部署工具. 它只是一个更轻量的链上程序开发库, 让你可以更高效地编写链上程序.

## 快速开始

要在项目中使用 pinocchio, 只需添加其为依赖即可. 在本文档创作时, pinocchio 的最新版本是 0.9.2, 你可以根据需要选择合适的版本.

```toml
[dependencies]
pinocchio = "0.9"
```

之后在 `src/lib.rs` 中使用 pinocchio 替代 solana-program, 例如:

```rust
use pinocchio::{
  account_info::AccountInfo,
  entrypoint,
  msg,
  ProgramResult,
  pubkey::Pubkey
};

entrypoint!(process_instruction);

pub fn process_instruction(
  _program_id: &Pubkey,
  _accounts: &[AccountInfo],
  _instruction_data: &[u8],
) -> ProgramResult {
  msg!("Hello from my program!");
  Ok(())
}
```

熟悉 solana-program 的同学会觉得这段非常眼熟, 只是类型与宏来自 pinocchio.

Pinocchio 还有一些进阶的用法, 允许你更灵活地控制入口与解析过程, 或者禁用一些不需要的功能, 以进一步减小二进制体积与降低计算消耗. 我们在这里不去赘述, 你可以参考 [pinocchio 的文档](https://docs.rs/pinocchio/latest/pinocchio/) 了解更多. 作为对初学者的建议, 如果你只是想快速上手, 可以先按上面的方式使用 pinocchio, 之后再根据需要逐步探索更高级的用法.

## 迁移指南: 从 solana-program 到 pinocchio

如果你已经有一个使用 solana-program 的链上程序, 想要迁移到 pinocchio, 这里有一些建议的步骤:

**入口替换**

原先的 `solana_program::entrypoint::process_instruction` -> 使用 pinocchio 的 `entrypoint!` 或 `lazy_program_entrypoint!` 宏.

**类型替换**

大多数 solana_program 的类型在 pinocchio 中都有对应的替代品, 只需将导入路径替换即可. 例如:

- `solana_program::pubkey::Pubkey` -> `pinocchio::pubkey::Pubkey`
- `solana_program::account_info::AccountInfo` -> `pinocchio::account_info::AccountInfo`

**日志替换**

- `solana_program::msg!` -> `pinocchio::msg!`
- 如果需要格式化, 那么需要引入 `pinocchio-log` 的 `log!` 宏

**cpi 与 sysvars**

- 将 `solana_program::program::invoke*` 与 `sysvar` 访问, 替换为 pinocchio 提供的接口(命名与用法保持直觉, 一般改动不大)

从作者的直觉角度来看, pinocchio 本质上并不是另一个 solana program sdk, 而是更靠近 abi 的最小集合. 它只提供了写链上程序所需的核心拼装件, 但把控制权还给了你, 它不会对这些链上概念进行过多的包装, 也不会对它们进行过多的抽象. 对追求极致与可控的 solana 开发者来说, 它能在可观地降低二进制体积与计算资源消耗的同时, 让工程更简洁, 更稳定.

在下一小节, 我们将使用 pinocchio 来重写前面章节的链上数据存储程序, 以展示它的实际用法与效果.
