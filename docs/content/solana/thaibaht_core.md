# Solana/泰铢币/核心机制实现

这篇文章介绍泰铢币的实现原理, 核心机制和背后的一些趣事点.

## 指令路由

泰铢币的合约主函数 `process_instruction()`, 像个小开关盒子:

- 当第一个字节是 `0x00`, 就执行铸造操作, ada 亲自印钞, 往自己的账户里塞钱.
- 当第一个字节是 `0x01`, 就执行两个账户之间的转账操作.

切换指令全靠这一个字节, 简单粗暴, 也非常有 solana 的狂野风格.

```rs
#![allow(unexpected_cfgs)]

use solana_program::sysvar::Sysvar;

solana_program::entrypoint!(process_instruction);

pub fn process_instruction_mint(
    _: &solana_program::pubkey::Pubkey,
    _: &[solana_program::account_info::AccountInfo],
    _: &[u8],
) -> solana_program::entrypoint::ProgramResult {
    Ok(())
}

pub fn process_instruction_transfer(
    _: &solana_program::pubkey::Pubkey,
    _: &[solana_program::account_info::AccountInfo],
    _: &[u8],
) -> solana_program::entrypoint::ProgramResult {
    Ok(())
}

pub fn process_instruction(
    program_id: &solana_program::pubkey::Pubkey,
    accounts: &[solana_program::account_info::AccountInfo],
    data: &[u8],
) -> solana_program::entrypoint::ProgramResult {
    assert!(data.len() >= 1);
    match data[0] {
        0x00 => process_instruction_mint(program_id, accounts, &data[1..]),
        0x01 => process_instruction_transfer(program_id, accounts, &data[1..]),
        _ => unreachable!(),
    }
}
```

## 创建数据账户

在每次转账或铸币之前, 合约都会检查目标 pda 数据账户有没有被初始化. 如果没有的话, 立刻用 `invoke_signed()` 调用 `solana_program::system_instruction::create_account()` 创建账户并帮 pda 数据账户交齐租金, 保证租赁豁免.

数据账户里写上 8 字节的 u64::MIN, 表示 0 泰铢余额.

这个自动开户逻辑非常贴心, 让用户转账时不用先自己去初始化自己的数据账户. 铸造指令与转账指令初始化 pda 数据账户代码如下:

```rs
pub fn process_instruction_mint(
    program_id: &solana_program::pubkey::Pubkey,
    accounts: &[solana_program::account_info::AccountInfo],
    data: &[u8],
) -> solana_program::entrypoint::ProgramResult {
    let accounts_iter = &mut accounts.iter();
    let account_user = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_user_pda = solana_program::account_info::next_account_info(accounts_iter)?;
    let _ = solana_program::account_info::next_account_info(accounts_iter)?; // Program system
    let _ = solana_program::account_info::next_account_info(accounts_iter)?; // Program sysvar rent

    // Check accounts permissons.
    assert!(account_user.is_signer);
    let account_user_pda_calc =
        solana_program::pubkey::Pubkey::find_program_address(&[&account_user.key.to_bytes()], program_id);
    assert_eq!(account_user_pda.key, &account_user_pda_calc.0);

    // Data account is not initialized. Create an account and write data into it.
    if **account_user_pda.try_borrow_lamports().unwrap() == 0 {
        let rent_exemption = solana_program::rent::Rent::get()?.minimum_balance(8);
        let bump = account_user_pda_calc.1;
        solana_program::program::invoke_signed(
            &solana_program::system_instruction::create_account(
                account_user.key,
                account_user_pda.key,
                rent_exemption,
                8,
                program_id,
            ),
            accounts,
            &[&[&account_user.key.to_bytes(), &[bump]]],
        )?;
        account_user_pda.data.borrow_mut().copy_from_slice(&u64::MIN.to_be_bytes());
    }
}
```

```rs
pub fn process_instruction_transfer(
    program_id: &solana_program::pubkey::Pubkey,
    accounts: &[solana_program::account_info::AccountInfo],
    data: &[u8],
) -> solana_program::entrypoint::ProgramResult {
    let accounts_iter = &mut accounts.iter();
    let account_user = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_user_pda = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_into = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_into_pda = solana_program::account_info::next_account_info(accounts_iter)?;
    let _ = solana_program::account_info::next_account_info(accounts_iter)?; // Program system
    let _ = solana_program::account_info::next_account_info(accounts_iter)?; // Program sysvar rent

    // Check accounts permissons.
    assert!(account_user.is_signer);
    let account_user_pda_calc =
        solana_program::pubkey::Pubkey::find_program_address(&[&account_user.key.to_bytes()], program_id);
    assert_eq!(account_user_pda.key, &account_user_pda_calc.0);
    let account_into_pda_calc =
        solana_program::pubkey::Pubkey::find_program_address(&[&account_into.key.to_bytes()], program_id);
    assert_eq!(account_into_pda.key, &account_into_pda_calc.0);

    // Data account is not initialized. Create an account and write data into it.
    if **account_into_pda.try_borrow_lamports().unwrap() == 0 {
        let rent_exemption = solana_program::rent::Rent::get()?.minimum_balance(8);
        let bump = account_into_pda_calc.1;
        solana_program::program::invoke_signed(
            &solana_program::system_instruction::create_account(
                account_user.key,
                account_into_pda.key,
                rent_exemption,
                8,
                program_id,
            ),
            accounts,
            &[&[&account_into.key.to_bytes(), &[bump]]],
        )?;
        account_into_pda.data.borrow_mut().copy_from_slice(&u64::MIN.to_be_bytes());
    }
}
```

## 只有 Ada 能印钱

别以为谁都能在 ada 的世界里印泰铢币! 在铸造操作的开头, 我们来一段硬性校验:

```rs
assert_eq!(*account_user.key, solana_program::pubkey!("6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt"));
```

只能 ada 本人签名, 才能铸币. 别想偷懒, 别想作弊, 防止通胀从根本做起(注: 此限制对 ada 无效)!

铸造流程也很简单, 首先读取 ada 的余额, 之后交易 data 参数里取出要铸造的金额, 两数相加, 写回 pda 数据账户. 在这个例子里, 数字以大端序存储.

```rs
// Mint.
let mut buf = [0u8; 8];
buf.copy_from_slice(&account_user_pda.data.borrow());
let old = u64::from_be_bytes(buf);
buf.copy_from_slice(&data);
let inc = u64::from_be_bytes(buf);
let new = old.checked_add(inc).unwrap();
account_user_pda.data.borrow_mut().copy_from_slice(&new.to_be_bytes());
```

## 转账指令

对于转账操作的话, 先把收款方的 pda 账户初始化好(如果还没开过户), 之后读取发送方和接收方 pda 数据账户里的余额, 接着从交易 data 里取出转账金额, 双方余额做加减, 最后写回各自的 pda 数据账户.

要注意的是, 转账操作时必须验证发送人的 pda 账户确实属于发送人, 防止让他人扣了您的钱!

```rs
let account_user_pda_calc =
    solana_program::pubkey::Pubkey::find_program_address(&[&account_user.key.to_bytes()], program_id);
assert_eq!(account_user_pda.key, &account_user_pda_calc.0);
```

Rust 的 `.checked_sub()` 和 `.checked_add()` 有溢出检测, 可以防止你搞个负数变成链上亿万富翁. 转账流程如下:

```rs
// Transfer.
let mut buf = [0u8; 8];
buf.copy_from_slice(&account_user_pda.data.borrow());
let old_user = u64::from_be_bytes(buf);
buf.copy_from_slice(&account_into_pda.data.borrow());
let old_into = u64::from_be_bytes(buf);
buf.copy_from_slice(&data);
let inc = u64::from_be_bytes(buf);
let new_user = old_user.checked_sub(inc).unwrap();
let new_into = old_into.checked_add(inc).unwrap();
account_user_pda.data.borrow_mut().copy_from_slice(&new_user.to_be_bytes());
account_into_pda.data.borrow_mut().copy_from_slice(&new_into.to_be_bytes());
Ok(())
```
