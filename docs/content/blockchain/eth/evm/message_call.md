EVM 中有四个关于跨合约调用的指令:

- `0xf1` CALL
- `0xf2` CALLCODE
- `0xf4` DELEGATECALL
- `0xfa` STATICCALL

Note: 注意这四个指令的编码不是连续的.

# CALL

**Message-call into an account.**

当 A 合约使用 CALL 调用 B 合约时, B 合约的代码读取/修改的是 B 合约内的 storage. 相当于传统编程领域内的启子进程.

# CALLCODE

**Message-call into this account with an alternative account’s code.**

当 A 合约使用 CALLCODE 调用 B 合约时, 相当于将 B 合约的代码载入到 A 合约的运行时环境, B 合约代码读取/修改的是 A 合约内的 storage. 相当传统编程领域内的导入一个依赖包.

# DELEGATECALL

**Message-call into this account with an alternative account’s code, but persisting the current values for sender and value.**

DELEGATECALL 与 CALLCODE 类似, 区别在于 msg.sender 不同.

假设有如下调用栈:

```text
User ---> Contract A ---> Contract B
```

假设 Contract A 使用 CALLCODE 调用 Contract B, Contract B 内执行了获取 msg.sender 的操作, 则 msg.sender = A.address; 如果是使用的 DELEGATECALL, 则 msg.sender = User.address.

# STATICCALL

**Static message-call into an account.**

STATICCALL 与 CALL 类似, 区别在于被调用的合约不允许修改自己的 storage.

# 后记

在重写 EVM 的过程中, 在这块地方卡了很久, 它包含一些历史包袱(众所周知 EVM 中即使修改一个 Gas 值都会导致硬分叉)而不得不做妥协. 好消息是 EVM 的历史使命即将结束, eWASM 将接替 EVM 继续前进.

我目前在做 WASM 虚拟机方面的工作, <重写 EVM> 系列文章大部分是在我写 WASM 虚拟机期间完成的. 年前已经实现了完整的 WASM MVP 版本, 项目地址是在 [https://github.com/mohanson/pywasm](https://github.com/mohanson/pywasm), 前端小伙伴要是准备学习 WASM 的话且凑巧懂点 python 的话, 可以尝试一下!

完.
