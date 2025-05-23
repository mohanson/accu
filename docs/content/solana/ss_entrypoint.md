# Solana/程序开发入门/入口函数解释

Solana 的每一笔交易中都包含一个或多个指令. 一个指令是对链上某个程序账户的调用, 包含三部分, [源码](https://github.com/anza-xyz/solana-sdk/blob/1276772ee61fbd1f8a60cfec7cd553aa4f6a55f3/instruction/src/lib.rs#L97-L104):

```rs
pub struct Instruction {
    /// Pubkey of the program that executes this instruction.
    pub program_id: Pubkey,
    /// Metadata describing accounts that should be passed to the program.
    pub accounts: Vec<AccountMeta>,
    /// Opaque data passed to the program for its own interpretation.
    pub data: Vec<u8>,
}
```

所以, 当一个指令被执行时, 它就会被送给您写的程序的入口函数 `process_instruction()`.

## 程序入口函数签名

```rs
solana_program::entrypoint!(process_instruction);

pub fn process_instruction(
    program_id: &solana_program::pubkey::Pubkey,
    accounts: &[solana_program::account_info::AccountInfo],
    data: &[u8],
) -> solana_program::entrypoint::ProgramResult {
    solana_program::msg!("Hello Solana!");
    Ok(())
}
```

我们一一解释.

**参数** `program_id: &solana_program::pubkey::Pubkey` 是当前这个合约(程序账户)本身的地址. 在链上, 每个部署的程序都有一个账户地址(公钥). 当交易指令调用这个程序时, solana 会把它写进 `program_id` 字段中. 您可以用它来做校验, 比如检查某个账户是否是由这个程序创建的 pda.  比如:

```rs
let expected_pda = solana_program::pubkey::Pubkey::create_program_address(&[seed], program_id)?;
```

**参数** `accounts: &[solana_program::account_info::AccountInfo]` 是指令中涉及的账户列表, 对应 `Instruction.accounts` 里的 `Vec<AccountMeta>` 项. 这些账户由调用方指定, 并且程序不能随便添加账户, 只能用这些已传入的账户.

每个 AccountInfo 包含:

0. 账户地址 (key)
0. 是否是签名者 (is_signer)
0. 是否是可写账户 (is_writable)
0. Lamports 余额 (lamports)
0. 数据 (data)
0. 所属程序 (owner)
0. ...

程序通常需要自己根据账户位置索引来解读这些账户. 比如:

```rs
let account_user = &accounts[0];
let account_user_pda = &accounts[1];
```

注意账户的顺序非常重要, 您必须和调用方传入的顺序一一对应.

**参数** `data: &[u8]` 是调用方自定义的指令数据. 通常我们会自己设计一个结构, 然后用 borsh, serde 等序列化方案或手动解析来从字节数组中提取内容. 您可以把它理解为"程序要执行什么操作 + 参数", 类似函数调用时传参.

这个模式和其他链, 比如以太坊的函数调用, 很不一样, solana 追求高性能, 所以要求调用方把所有要用的账户和数据一次性传进来, 程序自己不会查链, 也不扫账户, 而是基于这些参数做纯函数式的运算.
