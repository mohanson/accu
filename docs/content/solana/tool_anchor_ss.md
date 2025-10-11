# Solana/更多开发者工具/Anchor 里的简单数据存储合约

本章节的配套代码在[这里](https://github.com/mohanson/pxsol-ss-anchor).

这一节, 我们用 anchor 实现一个数据存储合约, 走一遍从建模到程序构建的过程. 你会看到三个关键点: 账户心智模型, 两条指令(init/update), 以及动态重分配与租金的细枝末节. 代码出自 `programs/pxsol-ss-anchor/src/lib.rs`, 但我们以文字的方式来理解它.

## 数据存储格式设计

我们知道用户数据实际上是存储在 pda 程序扩展账户里的. 在我们使用原生 rust 编写该程序时, 我们其实并没有对 pda 账户里的数据格式做过多约束, 只要能序列化与反序列化就行. 但在 anchor 里, 我们可以定义一个结构体来描述它, 并用 `#[account]` 标记它. 这种做法可以方便我们后续的开发, 也方便我们对链上数据的分析和理解.

```rust
#[account]
pub struct Data {
    pub auth: Pubkey, // The owner of this pda account
    pub bump: u8,     // The bump to generate the PDA
    pub data: Vec<u8> // The content, arbitrary bytes
}

impl Data {
    pub fn space_for(data_len: usize) -> usize {
        // 8 (discriminator) + 32 (auth) + 1 (bump) + 4 (vec len) + data_len
        8 + 32 + 1 + 4 + data_len
    }
}
```

方法 `space_for()` 用来计算账户所需空间. 这里的空间由五部分组成. 我们需要使用该函数来计算账户的租赁豁免金额.

## 指令: 初始化程序扩展账户

我们设计了两条指令: `init` 和 `update`. `init` 用来初始化程序扩展账户, `update` 用来更新内容. 下面我们逐一分析它们的实现.

指令 init 做了三件事: 记住谁是拥有者, 记录 bump, 并把内容置空.

```rust
pub fn init(ctx: Context<Init>) -> Result<()> {
    let account_user = &ctx.accounts.user;
    let account_user_pda = &mut ctx.accounts.user_pda;
    account_user_pda.auth = account_user.key();
    account_user_pda.bump = ctx.bumps.user_pda;
    account_user_pda.data = Vec::new();
    Ok(())
}
```

账户约束里, `init` 会在第一次调用时分配账户与租金, 由拥有者 `payer = user` 支付:

```rust
#[derive(Accounts)]
pub struct Init<'info> {
    #[account(mut)]
    pub user: Signer<'info>,
    #[account(
        init,
        payer = user,
        seeds = [SEED, user.key().as_ref()],
        bump,
        space = Data::space_for(0)
    )]
    pub user_pda: Account<'info, Data>,
    pub system_program: Program<'info, System>,
}
```

此时程序扩展账户里的数据字段是空的, 但已具备完整身份与归属, 并达成了租赁豁免.

## 指令: 存储或更新数据

更新内容时, 我们允许程序扩展账户变大或变小. 变大需要补齐租金, 变小则把多出来的 lamports 退给拥有者. 逻辑可以读作三步: 验权, 重分配, 找零. Anchor 框架会帮我们处理租赁豁免与扣费, 但找零需要我们自己来做. 也就是当新数据比老数据大时, 我们不需要做什么, anchor 会自动帮我们补齐租赁豁免资金; 但当新数据比老数据小时, 我们要把多出来的 lamports 退给拥有者.

```rust
pub fn update(ctx: Context<Update>, data: Vec<u8>) -> Result<()> {
    let account_user = &ctx.accounts.user;
    let account_user_pda = &mut ctx.accounts.user_pda;
    // Authorization: only the stored authority can update.
    require_keys_eq!(account_user_pda.auth, account_user.key(), PxsolError::Unauthorized);
    // At this point, Anchor has already reallocated the account according to the `realloc = ...` constraint
    // (using `new_data.len()`), pulling extra lamports from auth if needed to maintain rent-exemption.
    account_user_pda.data = data;
    // If the account was shrunk, Anchor won't automatically refund excess lamports. Refund any surplus (over the
    // new rent-exempt minimum) back to the user.
    let account_user_pda_info = account_user_pda.to_account_info();
    let rent = Rent::get()?;
    let rent_exemption = rent.minimum_balance(account_user_pda_info.data_len());
    let hold = **account_user_pda_info.lamports.borrow();
    if hold > rent_exemption {
        let refund = hold.saturating_sub(rent_exemption);
        // Transfer lamports from PDA to user using the PDA as signer.
        let signer_seeds: &[&[u8]] = &[SEED, account_user.key.as_ref(), &[account_user_pda.bump]];
        let signer = &[signer_seeds];
        let cpictx = CpiContext::new_with_signer(
            ctx.accounts.system_program.to_account_info(),
            system_program::Transfer { from: account_user_pda_info.clone(), to: account_user.to_account_info() },
            signer,
        );
        // It's okay if refund equals current - min_rent; system program enforces balances.
        system_program::transfer(cpictx, refund)?;
    }
    Ok(())
}
```

相配套的账户约束清晰地约定了该指令的一些策略细节.

```rust
#[derive(Accounts)]
#[instruction(new_data: Vec<u8>)]
pub struct Update<'info> {
    #[account(mut)]
    pub user: Signer<'info>,
    #[account(
        mut,
        seeds = [SEED, user.key().as_ref()],
        bump = user_pda.bump,
        realloc = Data::space_for(new_data.len()),
        realloc::payer = user,
        realloc::zero = false,
        constraint = user_pda.auth == user.key() @ PxsolError::Unauthorized,
    )]
    pub user_pda: Account<'info, Data>,
    pub system_program: Program<'info, System>,
}
```

## 常用技巧与注意事项

- 授权必检: `require_keys_eq!(…)`
- PDA 做签名者: 用 `new_with_signer`, seeds 里别忘了 `bump`.
- 伸缩成本与上限: 一次极大扩容会受限制, 必要时分片或多次更新.
- 资金来源: 扩容的 rent 差额由 `user` 出, 余额不足会失败.

## 收束

我们 anchor 版本的数据存储器很平凡, 却把 anchor 最常用的几块能力都连接在了一起: 账户约束, 动态重分配, pda 代签. 把它跑通之后, 我们可以继续加上一些更加复杂的逻辑. 代码总共只有不到 100 行, 但它是个很好的起点. 您应该能很快阅读懂它, 因此在这里不再过多赘述.
