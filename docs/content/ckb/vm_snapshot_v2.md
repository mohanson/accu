# CKB/CKB-VM Snapshot V2

## 背景

在 [CKB/CKB-VM Snapshot V1](./vm_snapshot_v1.md) 中, 我们介绍了 CKB-VM 最早的快照方案: 把所有写过的页面(dirty pages)整页复制下来, 连同寄存器, PC 一并序列化. 这套方案足够正确, 也足够简单, 但在真实场景下暴露出一个明显的弱点: 快照体积可能远远大于"脚本真正修改过的数据".

最典型的例子是 syscall `ckb_load_witness`. 脚本调用它时, CKB-VM 会把某条 witness 的内容整段拷贝到脚本指定的内存缓冲区里. 从内存子系统的角度看, 这段缓冲区的所有页面都被写入过, dirty 标志全部置位; 但从语义上看, 这些字节并不是脚本自己计算出来的, 而是逐字节地来自交易本身. 既然交易本身已经在链上公开存储, 让快照再复制一份就显得很浪费.

Snapshot V2 正是为这类场景设计的. 它的核心思想是: 引入一个"数据源"抽象, 把那些"内容完全来自外部, 可以稳定重新取得"的页面记为对数据源的引用(id + offset + length), 而不是整页字节. 真正由脚本计算并写入的页面, 仍按 V1 的方式整页保存.

本文介绍 Snapshot V2 的实现, 源代码位于 [src/snapshot2.rs](https://github.com/nervosnetwork/ckb-vm/blob/develop/src/snapshot2.rs).

## DataSource 抽象

V2 用一个 trait 描述"可寻址且生命周期内稳定不变"的数据源:

```rs
pub trait DataSource<I: Clone + PartialEq> {
    fn load_data(&self, id: &I, offset: u64, length: u64) -> Option<(Bytes, u64)>;
}
```

- `I` 是数据条目的标识类型, 由使用方自行定义. 在 CKB 的场景下, 它通常是一个枚举, 用来区分 cell data, witness 等不同来源, 同时携带 index.
- `load_data` 接受 id, 偏移和期望长度, 返回实际读到的字节以及"从 offset 开始的完整剩余长度". 后者的设计与 CKB syscall 一致, 调用方可以借此告诉脚本"实际有多少字节可读", 即便本次只取了其中一段.

DataSource 必须满足一个隐含的契约: 在虚拟机的整个生命周期内, 同样的 `(id, offset, length)` 必须能稳定地取回同样的字节. 否则恢复出来的虚拟机就不再与挂起时等价. 把交易作为数据源是天然合规的, 因为它已经定型, 不会再变.

## Snapshot2Context

V2 不再是一个无状态的函数集合, 而是一个有状态的上下文对象 `Snapshot2Context`, 与虚拟机的整个执行过程并行存在:

```rs
pub struct Snapshot2Context<I: Clone + PartialEq, D: DataSource<I>> {
    // page index -> (id, offset, flag)
    pages: HashMap<u64, (I, u64, u8)>,
    data_source: D,
}
```

`pages` 这张表是 V2 的核心数据结构: 它记录了每一个"内容完全来自数据源"的页面, 以及该页对应的数据源 id, 在数据源中的偏移, 以及页 flag. 表中的页和内存中真实页面是一一对应的, 但它并不存放页内容, 内容在需要时随时可以通过 `data_source.load_data` 重新取得.

只要这张表维护得足够准确, 制作快照时就能把这部分页面替换成对数据源的引用, 快照体积自然就降下来了.

## 跟踪与撤销跟踪

`Snapshot2Context` 通过两个互为反操作的方法维护 `pages` 表:

```rs
pub fn track_pages<M>(&mut self, machine: &mut M,
    start: u64, mut length: u64, id: &I, mut offset: u64) -> Result<(), Error>;

pub fn untrack_pages<M>(&mut self, machine: &mut M,
    start: u64, length: u64) -> Result<(), Error>;
```

`track_pages` 把 `[start, start+length)` 内**完整覆盖**的页面登记成"来自数据源 id, 起始偏移 offset". 实现上有几处细节值得注意:

- 它会先把 start 向上对齐到页边界, 头尾不满一整页的部分被直接丢弃. 原因是部分页同时包含数据源字节和其它内容, 无法整体用一条数据源引用来描述, 只能退回为普通脏页.
- 登记前会显式 `clear_flag(page, FLAG_DIRTY)`. 因为这些字节虽然刚刚通过 `store_bytes` 写入了内存, 但语义上它们等同于"原样从数据源加载", 不应当被视为脏页, 否则后续制作快照时会被当成 V1 风格的整页 dirty 数据再保存一次.
- 表中保存的 flag 是清掉 DIRTY 之后从内存系统读回的当前 flag, 这样恢复时其它属性位(可读, 可写, 可执行等)也能一并还原.

`untrack_pages` 则负责相反的事: 当一段内存即将被脚本自行写入时, 先把这段范围内的所有页从 `pages` 中删除, 并把 DIRTY 标记重新置位. 这是为了防止"先从数据源加载, 后又被脚本部分覆盖"的页被误判为干净的数据源页. 一旦发生覆盖, 这一页就不再等于数据源里的内容了.

## 接入虚拟机的两个入口

仅有 track / untrack 还不够, 还需要把它们插入到所有"会把数据源字节搬进内存"的操作里. V2 提供了两个高层入口.

第一个是 `store_bytes`, 取代普通的 `Memory::store_bytes`, 专门用于 syscall 把外部数据写入脚本内存的场景:

```rs
pub fn store_bytes<M>(&mut self, machine: &mut M,
    addr: u64, id: &I, offset: u64, length: u64, size_addr: u64
) -> Result<(u64, u64), Error> {
    let (data, full_length) = self.load_data(id, offset, length)?;
    machine.memory_mut().store64(
        &M::REG::from_u64(size_addr), &M::REG::from_u64(full_length))?;
    self.untrack_pages(machine, addr, data.len() as u64)?;
    machine.memory_mut().store_bytes(addr, &data)?;
    self.track_pages(machine, addr, data.len() as u64, id, offset)?;
    Ok((data.len() as u64, full_length))
}
```

它的执行顺序是: 取数据 -> 把"完整长度"写回 `size_addr`(对应 CKB syscall 的返回约定) -> 先 untrack 一次目标区间(清理掉之前可能登记过的任何引用) -> 真正写入字节 -> 再 track 一次, 完成新的登记. 一切 syscall 风格的数据加载(load witness, load cell data 等)都应当通过这个方法进入内存, 才能享受到 V2 的体积优化.

第二个入口是 `mark_program`, 用来登记 ELF 程序自身. CKB-VM 当前的 `load_program` 还不在 `SupportMachine` trait 上, 不便于直接拦截, 所以 V2 采用一个分两步的工作流:

```rs
pub fn mark_program<M>(&mut self, machine: &mut M,
    metadata: &ProgramMetadata, id: &I, offset: u64) -> Result<(), Error> {
    for action in &metadata.actions {
        self.init_pages(machine, action, id, offset)?;
    }
    Ok(())
}
```

调用方先 `elf::parse_elf` 得到 `ProgramMetadata`, 再 `load_program_with_metadata` 真正把程序装进内存, 最后把 metadata 交给 `mark_program`. metadata 中的每个 `LoadingAction` 描述了 ELF 一个段(segment)的装载方式: 装到哪个地址, 长度多少, 在文件中的源区间是什么. `init_pages` 就根据这些信息计算出 "(内存地址, 在数据源中的偏移, 长度)" 三元组, 调 `track_pages` 完成登记. 这样脚本的代码段和只读数据段也成了对数据源的引用, 不再占用快照体积.

## 制作快照

`make_snapshot` 的工作是把当前虚拟机的状态序列化为 `Snapshot2`:

```rs
#[derive(Clone, Debug, Deserialize, Serialize)]
pub struct Snapshot2<I: Clone + PartialEq> {
    // (address, flag, id, source offset, source length)
    pub pages_from_source: Vec<(u64, u8, I, u64, u64)>,
    // (address, flag, content)
    pub dirty_pages: Vec<(u64, u8, Vec<u8>)>,
    pub version: u32,
    pub registers: [u64; RISCV_GENERAL_REGISTER_NUMBER],
    pub pc: u64,
    pub cycles: u64,
    pub max_cycles: u64,
    pub load_reservation_address: u64,
}
```

相比 V1, 这里多了三类字段: `pages_from_source` 用来描述对数据源的引用, `cycles` 和 `max_cycles` 用来恢复虚拟机的计费状态(V1 完全没有保存这两项, 调用方必须自行管理), 其余字段含义不变.

制作过程分两遍扫描:

```rs
pub fn make_snapshot<M>(&self, machine: &mut M) -> Result<Snapshot2<I>, Error> {
    let mut dirty_pages: Vec<(u64, u8, Vec<u8>)> = vec![];
    for i in 0..machine.memory().memory_pages() as u64 {
        let flag = machine.memory_mut().fetch_flag(i)?;
        if flag & FLAG_DIRTY == 0 { continue; }
        let address = i * PAGE_SIZE;
        let mut data: Vec<u8> = machine.memory_mut().load_bytes(address, PAGE_SIZE)?.into();
        if let Some(last) = dirty_pages.last_mut() {
            if last.0 + last.2.len() as u64 == address && last.1 == flag {
                last.2.append(&mut data);
            }
        }
        if !data.is_empty() {
            dirty_pages.push((address, flag, data));
        }
    }
    // ... 第二遍: 扫 self.pages 生成 pages_from_source
}
```

第一遍按 V1 的思路收集所有 dirty 页, 但在追加时会与上一条比较: 若两条记录的地址恰好连续, 且 flag 相同, 就合并成一条. 这种"地址连续则合并"的优化在 `pages_from_source` 的生成中体现得更充分. 第二遍扫描 `self.pages` 时, 不仅要求地址相邻和 flag 相同, 还要求 `id` 相同, 并且在数据源中的偏移也连续, 满足这四个条件的页才能合并成一条更长的引用. 这能把对同一段 witness 的多页引用压缩为一条记录, 进一步减小快照体积.

`make_snapshot` 还做了一个小但重要的去重: 如果某页同时出现在 `self.pages` 中和 dirty 列表中, 以 dirty 优先, 跳过 `pages_from_source` 中的对应条目. 这种情况发生在"先用 `store_bytes` 加载, 后又被脚本部分覆盖但没走 `untrack_pages`"的边界场景, 让 dirty 优先保证了恢复后的内容仍然正确.

## 恢复快照

`resume` 是 `make_snapshot` 的反过程:

```rs
pub fn resume<M>(&mut self, machine: &mut M, snapshot: &Snapshot2<I>) -> Result<(), Error> {
    if machine.version() != snapshot.version { return Err(Error::InvalidVersion); }
    self.pages.clear();
    // 恢复寄存器, PC, cycles, max_cycles ...
    for (address, flag, id, offset, length) in &snapshot.pages_from_source {
        let (data, _) = self.load_data(id, *offset, *length)?;
        machine.memory_mut().store_bytes(*address, &data)?;
        for i in 0..(data.len() as u64 / PAGE_SIZE) {
            machine.memory_mut().set_flag(address / PAGE_SIZE + i, *flag)?;
        }
        self.track_pages(machine, *address, data.len() as u64, id, *offset)?;
    }
    for (address, flag, content) in &snapshot.dirty_pages {
        machine.memory_mut().store_bytes(*address, content)?;
        for i in 0..(content.len() as u64 / PAGE_SIZE) {
            machine.memory_mut().set_flag(address / PAGE_SIZE + i, *flag)?;
        }
    }
    machine.memory_mut()
        .set_lr(&M::REG::from_u64(snapshot.load_reservation_address));
    Ok(())
}
```

第一步仍然是版本校验; 第二步会把 `self.pages` 整张表清空, 因为 resume 意味着我们进入了一个全新的上下文, 旧的跟踪信息已经无意义. 接着依次回写寄存器, PC, cycles 和 max_cycles.

接下来处理 `pages_from_source`: 对每条引用, 通过 `load_data` 从数据源重新取回字节, 直接写进内存, 再 `set_flag` 复原页 flag, 最后 `track_pages` 把这段范围重新登记到 `self.pages` 中. 这一步很关键, 恢复出来的虚拟机不仅要状态等价, 还要让后续的 `make_snapshot` 仍然能正确识别出哪些页是数据源页. 期间还会对每条引用做对齐校验, 若地址或长度不是页大小的整数倍, 立即返回 `MemPageUnalignedAccess` 错误.

最后处理 `dirty_pages`, 把整页字节按 V1 的方式写回内存, 设置 flag, 这些页天然带着 DIRTY 标志, 不需要登记到 `self.pages`.

## 与 V1 的比较

V2 在 V1 的基础上做了三处实质性扩展:

- 引入 DataSource 抽象, 把"内容来自外部"的页面以引用形式存入快照, 替代整页字节. 对 syscall 大量加载外部数据的脚本, 快照体积可以缩小一个数量级以上.
- 跟踪 ELF 程序自身. 通过 `mark_program` 把代码段, 只读数据段也变成对数据源的引用, 进一步压缩体积.
- 把 cycles 和 max_cycles 纳入快照. V1 只关心"计算状态"本身, 计费信息由调用方负责; V2 直接把它们当作虚拟机状态的一部分, 让"恢复后的虚拟机"完全等价于"挂起前的虚拟机", 调用方更容易使用.

代价是 V2 把"跟踪页面"这件事侵入到了所有数据加载路径上. 任何把外部字节搬进虚拟机内存的 syscall, 都必须改走 `Snapshot2Context::store_bytes` 而不是 `Memory::store_bytes`, 否则就享受不到优化, 甚至可能让快照漏掉一些信息. 对脚本开发者而言这层差异是透明的, 但对实现 syscall 的人来说, 需要时时记得绕道 `Snapshot2Context`.
