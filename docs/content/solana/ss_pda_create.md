# Solana/程序开发入门/创建数据账户并使其达成租赁豁免

我们开始实现链上数据存储器的第一个功能. 用户首次使用该存储器, 并尝试写入数据到自己的专属数据账户中时. 我们要完成以下几个功能:

0. 用户第一次上传时, 程序会帮他创建一个 pda 数据账户.
0. 上传的数据长度可以自定义.
0. 创建的账户会自动达成租赁豁免, 避免日后被清理.

## 涉及到的账户

在编写具体功能之前, 我们先思考一下该功能会涉及到哪些账户.

0. 用户的普通钱包账户. 创建 pda 数据账户需要使用到用户的普通钱包账户作为种子, 同时需要用户的普通钱包账户提供 lamport 以达成数据账户租赁豁免. 该账户的权限应当是可写, 需要签名.
0. 用户新生成的数据账户. 我们会新建一个 pda 数据账户并在此账户中写入数据. 该账户的权限应当是可写, 无需签名.
0. 系统账户. 只有系统账户才能创建新的账户. 该账户的权限应当是只读, 无需签名.
0. Sysvar rent 账户. Solana 通过 sysvar 帐户向程序公开各种集群状态数据. 在本例子中, 我们需要知道需要多少 lamport 才能使数据账户达成租赁豁免, 而这个数字可能由集群动态改变. 因此需要访问 sysvar rent 账户. 该账户的权限应当是只读, 无需签名. 您可以访问[此页面](https://docs.anza.xyz/runtime/sysvars)了解更多关于 sysvar 账户的信息.

总结账户列表如下:

| 账户索引 |      地址       | 需要签名 | 可写 | 权限(0-3) |        角色        |
| -------- | --------------- | -------- | ---- | --------- | ------------------ |
| 0        | ...             | 是       | 是   | 3         | 用户的普通钱包账户 |
| 1        | ...             | 否       | 是   | 1         | 用户的数据账户     |
| 2        | `1111111111...` | 否       | 否   | 0         | System             |
| 3        | `SysvarRent...` | 否       | 否   | 0         | Sysvar rent        |

从入口函数 process_instruction 的 accounts 参数中获取各个账户信息代码如下:

```rs
let accounts_iter = &mut accounts.iter();
let account_user = solana_program::account_info::next_account_info(accounts_iter)?;
let account_data = solana_program::account_info::next_account_info(accounts_iter)?;
let _ = solana_program::account_info::next_account_info(accounts_iter)?; // Program system
let _ = solana_program::account_info::next_account_info(accounts_iter)?; // Program sysvar rent
```

## 计算租赁豁免

Solana 提供了一个函数可以查询系统规定的租赁豁免门槛:

```rs
let rent_exemption = solana_program::rent::Rent::get()?.minimum_balance(data.len());
```

参数 `data.len()` 是您准备在 pda 账户中存储的字节数, 返回值 rent_exemption 是为租赁豁免所需的 lamport 数量.

## 派生 PDA 数据账户地址

您需要使用 `solana_program::pubkey::Pubkey::find_program_address` 来获取 pda 账户地址以及其 bump 值. 在本示例中, 我们只需要使用到 bump 的值.

```rs
let bump_seed = solana_program::pubkey::Pubkey::find_program_address(&[&account_user.key.to_bytes()], program_id).1;
```

## 判断 PDA 是否已经存在

Solana 的 sdk 里并没有直接提供可供判断一个账户是否存在的函数, 因此我们使用以下方式来进行判断. 这行代码的依据是任何存在的账户都必须达成租赁豁免, 因此存在的账户的余额必不可能为零.

```rs
if **account_data.try_borrow_lamports().unwrap() == 0 {
    // Data account is not initialized.
}
```

## 创建 PDA 账户

您需要使用系统程序 `solana_program::system_instruction::create_account` 创建账户.

```rs
solana_program::system_instruction::create_account(
    account_user.key,
    account_data.key,
    rent_exemption,
    data.len() as u64,
    program_id,
)
```

由于 pda 没有私钥, 不能自己签名, 所以要用程序的签名种子进行签名.

```rs
solana_program::program::invoke_signed(
    &solana_program::system_instruction::create_account(
        account_user.key,
        account_data.key,
        rent_exemption,
        data.len() as u64,
        program_id,
    ),
    accounts,
    &[&[&account_user.key.to_bytes(), &[bump_seed]]],
)?;
```

Solana rust sdk 中有一个与 `invoke_signed()` 函数非常相似的 `invoke()` 函数, 它们的作用都是用于执行一个指令, 但是功能上存在细微的差异. 在这个例子中, 我们要操作的账户是 pda, 也就是说这个账户没有私钥, 不能真正签名,  但您(程序)作为它的所有者, 有权代表它执行操作. 这个时候就不能用普通的 `invoke()`, 而是要用 `invoke_signed()`, 让 solana 系统知道: "这个账户虽然没有签名, 但我是它的创建者, 我现在代表它签名了".

完成! 您现在拥有了一个租赁豁免的 pda 数据账户.

## 写入数据

最后, 我们向数据账户写入数据. 很简单, 对吧?

```rs
account_data.data.borrow_mut().copy_from_slice(data);
```

## 完整代码

```rs
#![allow(unexpected_cfgs)]

use solana_program::sysvar::Sysvar;

solana_program::entrypoint!(process_instruction);

pub fn process_instruction(
    program_id: &solana_program::pubkey::Pubkey,
    accounts: &[solana_program::account_info::AccountInfo],
    data: &[u8],
) -> solana_program::entrypoint::ProgramResult {
    let accounts_iter = &mut accounts.iter();
    let account_user = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_data = solana_program::account_info::next_account_info(accounts_iter)?;
    let _ = solana_program::account_info::next_account_info(accounts_iter)?; // Program system
    let _ = solana_program::account_info::next_account_info(accounts_iter)?; // Program sysvar rent

    let rent_exemption = solana_program::rent::Rent::get()?.minimum_balance(data.len());
    let bump_seed = solana_program::pubkey::Pubkey::find_program_address(&[&account_user.key.to_bytes()], program_id).1;

    // Data account is not initialized. Create an account and write data into it.
    if **account_data.try_borrow_lamports().unwrap() == 0 {
        solana_program::program::invoke_signed(
            &solana_program::system_instruction::create_account(
                account_user.key,
                account_data.key,
                rent_exemption,
                data.len() as u64,
                program_id,
            ),
            accounts,
            &[&[&account_user.key.to_bytes(), &[bump_seed]]],
        )?;
        account_data.data.borrow_mut().copy_from_slice(data);
        return Ok(());
    }
    Ok(())
}
```
