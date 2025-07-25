# Solana/在主网发行您的代币/实现空投程序

我们要实现的空投程序非常简单: 任意调用该空投程序的用户, 程序会自动为其创建一个关联代币账户, 并转账 5 pxs 给他.

```rs
solana_program::entrypoint!(process_instruction);

pub fn process_instruction(
    _: &solana_program::pubkey::Pubkey,
    accounts: &[solana_program::account_info::AccountInfo],
    _: &[u8],
) -> solana_program::entrypoint::ProgramResult {
    let accounts_iter = &mut accounts.iter();
    let account_user = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_user_spla = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_mana = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_mana_auth = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_mana_spla = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_mint = solana_program::account_info::next_account_info(accounts_iter)?;
    let _ = solana_program::account_info::next_account_info(accounts_iter)?;
    let account_spl = solana_program::account_info::next_account_info(accounts_iter)?;
    let _ = solana_program::account_info::next_account_info(accounts_iter)?;

    solana_program::program::invoke(
        &spl_associated_token_account::instruction::create_associated_token_account_idempotent(
            &account_user.key,
            &account_user.key,
            &account_mint.key,
            &account_spl.key,
        ),
        accounts,
    )?;
    let account_seed = &[];
    let account_bump = solana_program::pubkey::Pubkey::find_program_address(&[account_seed], account_mana.key).1;
    solana_program::program::invoke_signed(
        &spl_token_2022::instruction::transfer_checked(
            &account_spl.key,
            &account_mana_spla.key,
            &account_mint.key,
            &account_user_spla.key,
            &account_mana_auth.key,
            &[],
            5000000000,
            9,
        )?,
        accounts,
        &[&[account_seed, &[account_bump]]],
    )?;

    Ok(())
}
```

在主网上的部署信息如下:

- 程序合约: `HgatfFyGw2bLJeTy9HkVd4ESD6FkKu4TqMYgALsWZnE6`
- 程序 pda 账户: `5yAqR4gSYfs7CqpR4mgN5DNT4xczwiATuybaAa33xGip`
- 关联代币账户: `G7C9Px4x1G5YE2NmUHG6BeuqavoDsQQsHGpfs7nvMcq9`
