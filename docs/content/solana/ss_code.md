# Solana/程序开发入门/完整链上代码

在本小节中, 我们给出完整链上数据存储器的代码.

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

    // Check accounts permissons.
    assert!(account_user.is_signer);
    let account_data_calc =
        solana_program::pubkey::Pubkey::find_program_address(&[&account_user.key.to_bytes()], program_id);
    assert_eq!(account_data.key, &account_data_calc.0);

    let rent_exemption = solana_program::rent::Rent::get()?.minimum_balance(data.len());
    let bump = account_data_calc.1;

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
            &[&[&account_user.key.to_bytes(), &[bump]]],
        )?;
        account_data.data.borrow_mut().copy_from_slice(data);
        return Ok(());
    }

    // Fund the data account to let it rent exemption.
    if rent_exemption > account_data.lamports() {
        solana_program::program::invoke(
            &solana_program::system_instruction::transfer(
                account_user.key,
                account_data.key,
                rent_exemption - account_data.lamports(),
            ),
            accounts,
        )?;
    }
    // Withdraw excess funds and return them to users. Since the funds in the pda account belong to the program, we do
    // not need to use instructions to transfer them here.
    if rent_exemption < account_data.lamports() {
        **account_user.lamports.borrow_mut() = account_user.lamports() + account_data.lamports() - rent_exemption;
        **account_data.lamports.borrow_mut() = rent_exemption;
    }
    // Realloc space.
    account_data.resize(data.len())?;
    // Overwrite old data with new data.
    account_data.data.borrow_mut().copy_from_slice(data);

    Ok(())
}
```
