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

Anchor 生成的 pda 账户, 账户数据的前 8 字节固定用来标识账户的具体类型, 保证 anchor 在反序列化时类型安全. 它的算法是对字符串 "account:Data" 做 sha256 哈希, 取前 8 字节. 这 8 个字节被称作 account discriminator. 您可以用下面的 python 代码来计算它:

```py
import hashlib

r = hashlib.sha256(b'account:Data').digest()[:8]
print(list(r)) # [206, 156, 59, 188, 18, 79, 240, 232]
```

举一个实际的例子, 假设我们要存储 "Hello World!" 字节的数据, 那么我们实际存储在 pda 账户里的内容是:

```text
discriminator: [206, 156, 59, 188, 18, 79, 240, 232]
         auth: [32 bytes of auth pubkey]
         bump: [1 byte of bump]
     data_len: [12, 0, 0, 0]
         data: [72, 101, 108, 108, 111, 32, 87, 111, 114, 108, 100, 33]
```

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

在设计好指令后, 我们需要定义它的账户列表以及账户约束.

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

下面介绍下这些账户的含义以及通过 `#[account(...)]` 规定的约束:

- `user` 是调用者.
    - `Signer<'info>` 表示账户的基本类型, 即需要签名, 因为它要支付创建账户的租金与手续费.
    - `#[account(mut)]` 表示可写.
- `user_pda` 是要新建的 pda 账户
    - `Account<Data>` 表示账户的基本类型
    - `#[account(init)]` 标记表示该账户需要在本次指令中被创建.
    - `#[account(payer = user)]` 标记创建 user_pda 时的租金与手续费由 user 支付.
    - `#[account(seeds = [SEED, user.key().as_ref()])]` pda 的种子数组, 这里用常量 seed 与 user 公钥派生唯一地址.
    - `#[account(bump)]` 让 anchor 自动求解并记录该 pda 的 bump, 用于签名和地址唯一性. 通常总是和 seeds 一起使用.
    - `#[account(space = Data::space_for(0))]` 为账户预留的字节数.
- `system_program` 是系统合约.
    - `Program<'info, System>` 表示系统程序的账户, 供 anchor 代为调用系统指令(如创建账户, 转账, 分配空间).

## 指令: 存储或更新数据

更新内容时, 我们允许程序扩展账户变大或变小. 变大需要补齐租金, 变小则把多出来的 lamports 退给拥有者. 逻辑可以读作三步: 验权, 重分配, 找零. Anchor 框架会帮我们处理租赁豁免与扣费, 但找零需要我们自己来做. 也就是当新数据比老数据大时, 我们不需要做什么, anchor 会自动帮我们补齐租赁豁免资金; 但当新数据比老数据小时, 我们要把多出来的 lamports 退给拥有者.

```rust
pub fn update(ctx: Context<Update>, data: Vec<u8>) -> Result<()> {
    let account_user = &ctx.accounts.user;
    let account_user_pda = &mut ctx.accounts.user_pda;

    // Update the data field with the new data.
    account_user_pda.data = data;

    // If the account was shrunk, Anchor won't automatically refund excess lamports. Refund any surplus (over the
    // new rent-exempt minimum) back to the user.
    let account_user_pda_info = account_user_pda.to_account_info();
    let rent_exemption = Rent::get()?.minimum_balance(account_user_pda_info.data_len());
    let hold = **account_user_pda_info.lamports.borrow();
    if hold > rent_exemption {
        let refund = hold.saturating_sub(rent_exemption);
        **account_user_pda_info.lamports.borrow_mut() = rent_exemption;
        **account_user.lamports.borrow_mut() = account_user.lamports().checked_add(refund).unwrap();
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

下面介绍这些账户的含义以及通过 `#[account(...)]` 规定的约束:

- `user` 是调用者.
    - `Signer<'info>` 表示账户的基本类型, 即需要签名.
    - `#[account(mut)]` 表示可写, 因为如果 pda 账户扩容, user 需要补缴租金; 如果 pda 账户缩小, 多余的 lamports 会退还给 user.
- `user_pda` 是要更新的 pda 账户
    - `Account<Data>` 表示账户的基本类型
    - `#[account(mut)]` 表示可写, 因为我们要修改其中的数据内容.
    - `#[account(seeds = [SEED, user.key().as_ref()])]` pda 的种子数组, 必须与创建时一致, 用于验证地址派生的正确性.
    - `#[account(bump = user_pda.bump)]` 使用之前存储在账户中的 bump 值, 确保 pda 地址的唯一性与合法性. 这个 bump 是在 init 时记录的.
    - `#[account(realloc = Data::space_for(new_data.len()))]` 动态重新分配账户空间. Anchor 会根据新数据的长度自动调整账户大小. 如果新空间大于旧空间, 会从 `realloc::payer` 扣除额外的租金; 如果新空间小于旧空间, 账户会缩小, 但多余的 lamports 不会自动退还(需要在指令逻辑中手动处理).
    - `#[account(realloc::payer = user)]` 指定当账户需要扩容时, 由 user 支付额外的租金. 如果 user 余额不足, 交易会失败.
    - `#[account(realloc::zero = false)]` 表示重新分配空间时不需要将新增的字节清零. 设为 false 可以节省计算单元, 因为我们会立即用新数据覆盖这些字节. 如果您需要确保新增空间初始化为零, 应设为 true.
    - `#[account(constraint = user_pda.auth == user.key() @ PxsolError::Unauthorized)]` 自定义约束检查, 验证调用者 user 的公钥必须与 pda 账户中存储的 auth 字段一致. 如果不一致, 会抛出 `PxsolError::Unauthorized` 错误. 这是一个关键的权限检查, 确保只有账户的拥有者才能更新数据.
- `system_program` 是系统合约.
    - `Program<'info, System>` 表示系统程序的账户, 用于账户重新分配和 lamports 转账操作.

## 收束

我们 anchor 版本的数据存储器很平凡, 却把 anchor 最常用的几块能力都连接在了一起: 账户约束, 动态重分配, pda 代签. 把它跑通之后, 我们可以继续加上一些更加复杂的逻辑. 代码总共只有不到 100 行, 但它是个很好的起点. 您应该能很快阅读懂它, 因此在这里不再过多赘述.
