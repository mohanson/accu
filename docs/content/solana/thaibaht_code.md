# Solana/泰铢币/完整链上代码

在本小节中, 我们给出完整泰铢币的代码.

```rs
#![allow(unexpected_cfgs)]

use solana_program::sysvar::Sysvar;

solana_program::entrypoint!(process_instruction);

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

    // Only Ada can mint more Thai Baht.
    assert_eq!(*account_user.key, solana_program::pubkey!("6ASf5EcmmEHTgDJ4X4ZT5vT6iHVJBXPg5AN5YoTCpGWt"));

    // Data account is not initialized. Create an account and write data into it.
    if **account_user_pda.try_borrow_lamports().unwrap() == 0 {
        let rent_exemption = solana_program::rent::Rent::get()?.minimum_balance(8);
        let bump_seed =
            solana_program::pubkey::Pubkey::find_program_address(&[&account_user.key.to_bytes()], program_id).1;
        solana_program::program::invoke_signed(
            &solana_program::system_instruction::create_account(
                account_user.key,
                account_user_pda.key,
                rent_exemption,
                8,
                program_id,
            ),
            accounts,
            &[&[&account_user.key.to_bytes(), &[bump_seed]]],
        )?;
        account_user_pda.data.borrow_mut().copy_from_slice(&u64::MIN.to_be_bytes());
    }

    // Mint.
    let mut buf = [0u8; 8];
    buf.copy_from_slice(&account_user_pda.data.borrow());
    let old = u64::from_be_bytes(buf);
    buf.copy_from_slice(&data);
    let inc = u64::from_be_bytes(buf);
    let new = old.checked_add(inc).unwrap();
    account_user_pda.data.borrow_mut().copy_from_slice(&new.to_be_bytes());
    Ok(())
}

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

    let account_need_pda =
        solana_program::pubkey::Pubkey::find_program_address(&[&account_user.key.to_bytes()], program_id).0;
    assert_eq!(account_user_pda.key, &account_need_pda);

    // Data account is not initialized. Create an account and write data into it.
    if **account_into_pda.try_borrow_lamports().unwrap() == 0 {
        let rent_exemption = solana_program::rent::Rent::get()?.minimum_balance(8);
        let bump_seed =
            solana_program::pubkey::Pubkey::find_program_address(&[&account_into.key.to_bytes()], program_id).1;
        solana_program::program::invoke_signed(
            &solana_program::system_instruction::create_account(
                account_user.key,
                account_into_pda.key,
                rent_exemption,
                8,
                program_id,
            ),
            accounts,
            &[&[&account_into.key.to_bytes(), &[bump_seed]]],
        )?;
        account_into_pda.data.borrow_mut().copy_from_slice(&u64::MIN.to_be_bytes());
    }

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
