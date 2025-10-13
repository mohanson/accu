# Solana/更多开发者工具/Pinocchio 重写简单数据存储合约

本节内容基于 [pxsol-ss](https://github.com/mohanson/pxsol-ss), 旨在展示如何使用 pinocchio 重写它. 最终成品课程代码位于 [pxsol-ss-pinocchio](https://github.com/mohanson/pxsol-ss-pinocchio) 仓库.

## 迁移工作

我们遇到的第一个问题是要修改 `rent_exemption` 和 `bump_seed` 的获取方式. 下面是修改前后的对比.

**旧**

```rs
let rent_exemption = solana_program::rent::Rent::get()?.minimum_balance(data.len());
let bump_seed = solana_program::pubkey::Pubkey::find_program_address(&[&account_user.key.to_bytes()], program_id).1;
```

**新**

```rs
let rent_exemption = pinocchio::sysvars::rent::Rent::get()?.minimum_balance(data.len());
let bump_seed = &[pinocchio::pubkey::find_program_address(&[&account_user.key()[..]], program_id).1];
```

判断程序扩展账户是否已经存在.

**旧**

```rs
if **account_data.try_borrow_lamports().unwrap() == 0 { ...
```

**新**

```rs
if account_data.lamports() == 0 { ...
```

调用系统程序, 创建程序扩展账户. 在 pinocchio 中, 相关的系统调用被封装在 `pinocchio_system` crate 中, 并且提供了更简洁的用法. 下面是修改前后的对比.

**旧**

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

**新**

```rs
pinocchio_system::instructions::CreateAccount {
    from: &account_user,
    to: &account_data,
    lamports: rent_exemption,
    space: data.len() as u64,
    owner: program_id,
}
.invoke_signed(&[signer])?;
```

修改程序扩展账户的数据

**旧**

```rs
account_data.data.borrow_mut().copy_from_slice(data);
```

**新**

```rs
account_data.try_borrow_mut_data().unwrap().copy_from_slice(data);
```

修改账户余额

**旧**

```rs
**account_user.lamports.borrow_mut() = account_user.lamports() + account_data.lamports() - rent_exemption;
**account_data.lamports.borrow_mut() = rent_exemption;
```

**新**

```rs
*account_user.try_borrow_mut_lamports().unwrap() += account_data.lamports() - rent_exemption;
*account_data.try_borrow_mut_lamports().unwrap() = rent_exemption;
```

我们的迁移工作已经完成, 下面是完整代码.

```rs
use pinocchio::sysvars::Sysvar;

pinocchio::entrypoint!(process_instruction);

pub fn process_instruction(
    program_id: &pinocchio::pubkey::Pubkey,
    accounts: &[pinocchio::account_info::AccountInfo],
    data: &[u8],
) -> pinocchio::ProgramResult {
    let account_user = accounts[0];
    let account_data = accounts[1];

    let rent_exemption = pinocchio::sysvars::rent::Rent::get()?.minimum_balance(data.len());
    let bump_seed = &[pinocchio::pubkey::find_program_address(&[&account_user.key()[..]], program_id).1];
    let signer_seed = pinocchio::seeds!(account_user.key(), bump_seed);
    let signer = pinocchio::instruction::Signer::from(&signer_seed);

    // Data account is not initialized. Create an account and write data into it.
    if account_data.lamports() == 0 {
        pinocchio_system::instructions::CreateAccount {
            from: &account_user,
            to: &account_data,
            lamports: rent_exemption,
            space: data.len() as u64,
            owner: program_id,
        }
        .invoke_signed(&[signer])?;
        account_data.try_borrow_mut_data().unwrap().copy_from_slice(data);
        return Ok(());
    }

    // Fund the data account to let it rent exemption.
    if rent_exemption > account_data.lamports() {
        pinocchio_system::instructions::Transfer {
            from: &account_user,
            to: &account_data,
            lamports: rent_exemption - account_data.lamports(),
        }
        .invoke()?;
    }

    // Withdraw excess funds and return them to users. Since the funds in the pda account belong to the program, we do
    // not need to use instructions to transfer them here.
    if rent_exemption < account_data.lamports() {
        *account_user.try_borrow_mut_lamports().unwrap() += account_data.lamports() - rent_exemption;
        *account_data.try_borrow_mut_lamports().unwrap() = rent_exemption;
    }
    // Realloc space.
    account_data.resize(data.len())?;
    // Overwrite old data with new data.
    account_data.try_borrow_mut_data().unwrap().copy_from_slice(data);

    Ok(())
}
```

最后我们来测试一下这个程序是否能正常工作. 运行以下命令, 进行编译, 部署和测试.

```sh
$ python make.py deploy
# 2025/05/20 16:06:38 main: deploy program pubkey="T6vZUAQyiFfX6968XoJVmXxpbZwtnKfQbNNBYrcxkcp"

# Save some data.
$ python make.py save "The quick brown fox jumps over the lazy dog"

# Load data.
$ python make.py load
# The quick brown fox jumps over the lazy dog.

# Save some data and overwrite the old data.
$ python make.py save "片云天共远, 永夜月同孤."
# Load data.
$ python make.py load
# 片云天共远, 永夜月同孤.
```

## 关键数据对比

|      /       | pxsol-ss  | pxsol-ss-pinocchio |
| ------------ | --------- | ------------------ |
| 编译时间     | 1m10.242s | 0m1.930s           |
| 编译产物大小 | 75K       | 29K                |
| 依赖项目数量 | 189       | 7                  |

通过以上这些关键数据对比, 我们可以看到使用 pinocchio 重写后的程序在编译时间, 编译产物大小和依赖项目数量上都有显著的提升. 这也说明了 pinocchio 作为 solana-program 的替代品, 在简化开发流程和提升效率方面具有很大的优势. 我们强烈推荐在新的 solana 程序开发中使用 pinocchio.
