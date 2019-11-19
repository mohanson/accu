# Gas/燃气/费用

相信许多人都对"以太坊虚拟机每一步执行都要扣除 Gas 费用"有所耳闻, 但鲜少有人能确切的说出具体扣费规则是如何的. EVM 按照不同的操作码预估消耗的计算机资源成本进行对应的 Gas 扣费, 并且其是先扣费, 后执行的预付费机制.

![img](/img/blockchain/eth/evm/fee/fee_schedule.png)

其中:

- $W_{\text zero}$ = {STOP, RETURN, REVERT}
- $W_{\text base}$ = {ADDRESS, ORIGIN, CALLER, CALLVALUE, CALLDATASIZE, CODESIZE, GASPRICE, COINBASE, TIMESTAMP, NUMBER, DIFFICULTY, GASLIMIT, RETURNDATASIZE, POP, PC, MSIZE, GAS}
- $W_{\text verylow}$ = {ADD, SUB, NOT, LT, GT, SLT, SGT, EQ, ISZERO, AND, OR, XOR, BYTE, CALLDATALOAD, MLOAD, MSTORE, MSTORE8, PUSH*, DUP*, SWAP*}
- $W_{\text low}$ = {MUL, DIV, SDIV, MOD, SMOD, SIGNEXTEND}
- $W_{\text mid}$ = {ADDMOD, MULMOD, JUMP}
- $W_{\text high}$ = {JUMPI}
- $W_{\text extcode}$ = {EXTCODESIZE}

内存的花费比较有意思, EVM 中内存花费是指数上升的, 也就是说你使用 1024 字节的内存和 1024 * 1024 字节的内存花费并不是 1024 倍, 而是一个指数倍关系.

$$
C_{\text mem}(a) = G_{\text memory} * a + \frac{a^2}{512}
$$

其中 a 是以 word 计算的内存大小. 假设一个操作码的执行过程中对内存进行了扩容, 则它实际需要花费的 Gas 是:

$$
G_{\text mem} = C_{\text mem}^\prime - C_{\text mem}
$$

# 举个栗子

**例(1)**: 假设当前内存消耗为 16 word, 使用 MSTORE 操作码对内存扩容为 32 word, 求该步需要消耗的 Gas.

$$
G = G_{\text verylow} + C_{\text mem}(32) - C_{\text mem}(16) = 3 + 98 - 48 = 53
$$

**例(2)**: 求执行 EVM 字节码 "0x601060005260206000f3" 所消耗的 Gas.

假设初始 Gas 为 100000, 则按操作码解析后的执行过程如下:

```
PUSH1           pc=00000000 cost=3
PUSH1           pc=00000002 cost=3
MSTORE          pc=00000004 cost=6
PUSH1           pc=00000005 cost=3
PUSH1           pc=00000007 cost=3
RETURN          pc=00000009 cost=0
```

因此消耗的 Gas 为 18.
