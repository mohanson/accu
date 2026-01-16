# Solana/程序开发入门/数据账户内容更新及动态租赁调节

Solana 的账户存储需要租金, 数据越长, 租金越贵. 如果数据更新后变长了, 数据账户租金不够, 账户就不再租赁豁免; 如果数据更新后变短了, 那用户其实多交了租金, 程序可以把多余的部分还给用户!

本篇文章就来教您如何实现动态租赁调节.

## 更新数据账户内容

链上账户可以使用 `.data.borrow_mut()` 来更新内容, 但大小不能变, 所以通常需要重新创建或使用 `.resize()` 重分配数据账户空间.

```rs
// Realloc space.
account_data.resize(data.len())?;
// Overwrite old data with new data.
account_data.data.borrow_mut().copy_from_slice(data);
```

## 租金补足

如果新数据比老数据更长, 您需要使用系统程序 `solana_program::system_instruction::transfer` 为 pda 账户添加更多租金.

```rs
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
```

## 租金退款

如果新数据比老数据更短, 则从 pda 账户中获取退款. 获取退款不需要执行系统程序, 您只需要修改两个账户中的余额即可.

```rs
// Withdraw excess funds and return them to users. Since the funds in the pda account belong to the program, we do
// not need to use instructions to transfer them here.
if rent_exemption < account_data.lamports() {
    **account_user.lamports.borrow_mut() = account_user.lamports() + account_data.lamports() - rent_exemption;
    **account_data.lamports.borrow_mut() = rent_exemption;
}
```

您可能好奇, 为什么这个时候不需要使用 `solana_program::system_instruction::transfer`? 问题的答案在于权限. 您是否还记得每个数据账户都拥有所有者程序? 所谓的所有者程序, 就是能自由操控数据账户而不需要额外的权限.

- 租金补足过程中, 程序转移了您的钱包账户的资金, 因此必须得到您的授权.
- 租金退款过程中, 程序转移了自己控制的数据账户的资金, 因此无需您授权.
