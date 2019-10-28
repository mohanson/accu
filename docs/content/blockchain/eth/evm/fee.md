# Gas/燃气/费用

相信许多人都对 "以太坊虚拟机每一步执行都要扣除 Gas 费用" 有所耳闻, 但鲜少有人能确切的说出具体扣费规则是如何的. EVM 按照不同的操作码预估消耗的计算机资源成本进行对应的 Gas 扣费, 并且其是先扣费, 后执行的预付费机制.

| Name                    | Value | Description                           |
|-------------------------|-------|---------------------------------------|
| $G_{\text zero}$          | 0     | 位于 $W_{\text zero}$ 集合内的操作码费用           |
| $G_{\text base}$          | 2     | 位于 $W_{\text base}$ 集合内的操作码费用           |
| $G_{\text verylow}$       | 3     | 位于 $W_{\text verylow}$ 集合内的操作码费用        |
| $G_{\text low}$           | 5     | 位于 $W_{\text low}$ 集合内的操作码费用            |
| $G_{\text mid}$           | 8     | 位于 $W_{\text mid}$ 集合内的操作码费用            |
| $G_{\text high}$          | 10    | 位于 $W_{\text high}$ 集合内的操作码费用           |
| $G_{\text extcode}$       | 700   | 位于 $W_{\text extcode}$ 集合内的操作码费用        |
| $G_{\text balance}$       | 400   | BALANCE 操作码的费用                        |
| $G_{\text sload}$         | 200   | SLOAD 操作码的费用                          |
| $G_{\text jumpdest}$      | 1     | JUMPDEST 操作码的费用                       |
| $G_{\text sset}$          | 20000 | SSTORE 操作码的费用, 当存储从零值设置为非零值的时候        |
| $G_{\text sreset}$        | 5000  | SSTORE 操作码的费用, 当存储从任意值设置为零值的时候        |
| $R_{\text sclear}$        | 15000 | 退费, 当存储从非零值设置为零值的时候                   |
| $R_{\text selfdestruct}$  | 24000 | 退费, SELFDESTRUCT 操作码                  |
| $G_{\text selfdestruct}$  | 5000  | SELFDESTRUCT 操作码的费用                   |
| $G_{\text create}$        | 32000 | CREATE 操作码的费用                         |
| $G_{\text codedeposit}$   | 200   | CREATE 操作码将代码存入世界状态需要为每字节支付的费用        |
| $G_{\text call}$          | 700   | CALL 操作码的费用                           |
| $G_{\text callvalue}$     | 9000  | 作为 CALL 操作的一部分, 支付非零值传输               |
| $G_{\text callstipend}$   | 2300  | 对于非零值转移，从 $G_{\text call}$ 值中减去被调用合约的津贴 |
| $G_{\text newaccount}$    | 25000 | CALL 或 SELFDESTRUCT 操作码创建新账号的费用       |
| $G_{\text exp}$           | 10    | EXP 操作码的费用                            |
| $G_{\text expbyte}$       | 50    | EXP 操作码指数部分每有效 bit 的费用                |
| $G_{\text memory}$        | 3     | 扩容内存的费用, 按 word 计算                    |
| $G_{\text txcreate}$      | 32000 | 创建合约的花费, 在 Homestead 阶段之后             |
| $G_{\text txdatazero}$    | 4     | 交易中每一个零字节的费用                          |
| $G_{\text txdatanonzero}$ | 68    | 交易中每一个非零字节的费用                         |
| $G_{\text transaction}$   | 21000 | 每个交易的费用.                              |
| $G_{\text log}$           | 375   | LOG 操作码的费用                            |
| $G_{\text logdata}$       | 8     | LOG 操作码为每一个字节数据的费用                    |
| $G_{\text logtopic}$      | 375   | LOG 操作码为每一个 Topic 的费用                 |
| $G_{\text sha3}$          | 30    | SHA3 操作码的费用                           |
| $G_{\text sha3word}$      | 6     | SHA3 操作码的费用, 按 word 的计算               |
| $G_{\text copy}$          | 3     | COPY 操作码的费用, 按 word 计算                |
| $G_{\text blockhash}$     | 20    | BLOCKHASH 操作码的费用                      |
| $G_{\text quaddivisor}$   | 100   | 指数模数预编译契约的输入大小的二次系数                   |

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


