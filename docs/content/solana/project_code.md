# Solana/在主网发行您的代币/实现空投程序

我们要实现的空投程序主要包含两个功能.

0. 任意调用该空投程序的用户, 程序会自动为其创建一个关联代币账户.
0. 转账 5 pxs 给他.

合约程序实现如下. 程序内部会调用两条指令来实现上述的功能.

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

编译程序后, 使用下面的代码将其部署在主网.

```py
import pxsol
pxsol.config.current = pxsol.config.mainnet

user = pxsol.wallet.Wallet(pxsol.core.PriKey.base58_decode('Put your private key here'))
with open('target/deploy/pxsol_spl.so', 'rb') as f:
    data = bytearray(f.read())
mana = user.program_deploy(data)
print(mana) # HgatfFyGw2bLJeTy9HkVd4ESD6FkKu4TqMYgALsWZnE6
```

我们的空投合约在主网上的部署地址为 `HgatfFyGw2bLJeTy9HkVd4ESD6FkKu4TqMYgALsWZnE6`.

简要分析下该空投程序的涉及账户:

|          账户          | 权限 |                          说明                           |
| ---------------------- | ---- | ------------------------------------------------------- |
| 用户账户               | 3    | 必须拥有足够的 sol 余额来支付创建新账户所需的费用       |
| 用户关联代币账户       | 1    | /                                                       |
| 程序账户               | 0    | 主网地址 `HgatfFyGw2bLJeTy9HkVd4ESD6FkKu4TqMYgALsWZnE6` |
| 程序 pda 账户          | 0    | 主网地址 `5yAqR4gSYfs7CqpR4mgN5DNT4xczwiATuybaAa33xGip` |
| 程序 pda 关联代币账户  | 1    | 主网地址 `G7C9Px4x1G5YE2NmUHG6BeuqavoDsQQsHGpfs7nvMcq9` |
| spl token mint 账户    | 0    | 主网地址 `6B1ztFd9wSm3J5zD5vmMNEKg2r85M41wZMUW7wXwvEPH` |
| 系统程序               | 0    | 主网地址 `11111111111111111111111111111111`             |
| 原生程序: Token-2022   | 0    | 主网地址 `TokenzQdBNbLqP5VEhdkAS6EPFLC1PHnBqCXEpPxuEb`  |
| 原生程序: 关联代币程序 | 0    | 主网地址 `ATokenGPvbdGVxr1b2hvZbsiqW5xWH25efTNsLJA8knL` |

最后, 不要忘记, 我们还需要将一些代币转账到**程序 pda 账户**. 转账操作如下:

```py
import pxsol
pxsol.config.current = pxsol.config.mainnet

user = pxsol.wallet.Wallet(pxsol.core.PriKey.base58_decode('Put your private key here'))
pubkey_mint = pxsol.core.PubKey.base58_decode('6B1ztFd9wSm3J5zD5vmMNEKg2r85M41wZMUW7wXwvEPH')
pubkey_mana = pxsol.core.PubKey.base58_decode('HgatfFyGw2bLJeTy9HkVd4ESD6FkKu4TqMYgALsWZnE6')
pubkey_mana_seed = bytearray([])
pubkey_mana_auth = pubkey_mana.derive_pda(pubkey_mana_seed)
user.spl_transfer(pubkey_mint, pubkey_mana_auth, 90000000 * 10**9)
```

我们初始转入九千万 pxs 代币给空投程序. 您可以通过[此页面](https://explorer.solana.com/address/5yAqR4gSYfs7CqpR4mgN5DNT4xczwiATuybaAa33xGip/tokens)查看空投程序当前拥有的 pxs 代币余额.
