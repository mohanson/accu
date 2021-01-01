# 杂项/算法心得笔记

![img](/img/misc/hackers_delight/hackers_delight.jpg)

> 本书既不是普通的数学算式教程, 也不是单纯的电脑程序算法手册, 它讲的是"计算机算术" -- 卷首语.

这本书是 [xxuejie](https://github.com/xxuejie) 推荐给我的, 看了颇有惊为天人之感, 遂做了前面几章的一点简单笔记.

## 操作最右边的位元

| 描述 | 公式 |
| -----| ---- |
| 将字组中值为 1 且最靠右的位元置 0 | `x & (x - 1)` |
| 将字组中值为 0 且最靠右的位元置 1 | `x | (x + 1)` |
| 将字组尾部的 1 都置为 0 | `x & (x + 1)` |
| 将字组尾部的 0 都置为 1 | `x | (x - 1)` |
| 将字组中值为 0 且最靠右的位元置 1, 并将其余位置 0 | `!x & (x + 1)` |
| 将字组中值为 1 且最靠右的位元置 0, 并将其余位置 1 | `!x | (x - 1)` |
| 将字组尾部的 0 都置为 1, 并将其余位置 0 | `!x & (x - 1)` |
| 将字组尾部的 1 都置为 0, 并将其余位置 1 | `!x | (x + 1)` |
| 保留字组中值为 1 且最靠右的位元, 并将其余位置 0 | `x & (-x)` |
| 将字组中值为 1 且最靠右的位元及其右方所有值为 0 的位元置 1, 并将左方位元置 0 | `x ^ (x - 1)` |
| 将字组中值为 0 且最靠右的位元及其右方所有值为 1 的位元置 1, 并将左方位元置 0 | `x ^ (x + 1)` |

**例题 1**: 如何判断某个无符号整数是不是 2 的幂或 0?

判断 `x & (x - 1)` 运行结果是否为 0 即可. 在现实中有大量的需要判断给定数是否是 2 的幂的需求, 使用此公式为最优解.

**例题 2**: 如何判断某个无符号整数是不是 2^n - 1 或 0?

判断 `x & (x + 1)` 运行结果是否为 0 即可.

## 德摩根定律

在命题逻辑和逻辑代数中, 德摩根定律是关于命题逻辑规律的一对法则.

- 非 (p 且 q) 等价于 (非 p) 或 (非 q)
- 非 (p 或 q) 等价于 (非 p) 且 (非 q)

德摩根公式在计算机逻辑中的表示和其变形:

```text
!(x & y) = !x | !y
!(x | y) = !x & !y
!-x      = x - 1
!(x ^ y) = !x ^ y
!(x + y) = !x - y
!(x - y) = !x + y
```

## 从右至左的可计算性测试

一个从字组到字组的映射函数, 当且仅当当运算结果中的每一个位元只依赖于各操作数中对应位元及其右侧位元时, 才可以用一系列字并行加减法, 按位与, 按位或及按位取反操作实现出来.

## 绝对值函数

假设 x 为 32 位有符号整数, 首先执行 `y = x >> 31`, 然后套用下列式子之一即可:

|      abs       |      nabs      |
| -------------- | -------------- |
| `(x ^ y) - y`  | `y - (x ^ y)`  |
| `(x + y) ^ y`  | `(y - x) ^ y`  |
| `x - (2x & y)` | `(2x & y) - x` |

上面的这些公式通常用三或四条指令就能实现, 而且不带分支.

## 两数平均值

下列公式可以计算出两个无符号整数的平均值, 而且还不会溢出:

```text
(x & y) + ((x ^ y) >> 1)
```

对于有符号数, 有两种平均值, 一种是出现小数时向下取整, 另一种是向上取整, 分别使用公式

```text
(x & y) + ((x ^ y) >> 1)
(x | y) - ((x ^ y) >> 1)
```

## 符号扩展

这里所说的符号扩展, 指现在字组中确定某个位元为符号位, 然后再把它的值向左传播, 覆盖掉那些位元中原来的值. 通常实现符号扩展的方法是: 先进行逻辑左移, 然后进行带符号的右移. 然而若是没有这些指令, 可以考虑用下列算法之一来计算. 此处列出将 7 号位元向左传播的三种算式.

- `((x + 0x00000080) & 0x000000FF) - 0x00000080`
- `((x & 0x000000FF) ^ 0x00000080) - 0x00000080`
- `(x & 0x0000007F) - (x & 00000080)`

算式中的加法也可以用减法或异或代替. 第二个公式特别有用, 因为加入可以确定符号位左方全都是 0, 那么其中的按位和操作也可以省略了.

## 无符号右移模拟带符号右移

```text
(( x + 0x80000000) >> n) - (0x80000000 >> n)
```

## 三值比较函数

```text
cmp(x, y) = -1, x < y
          =  0, x = y
          =  1, x > y
```

下面的公式对无符号数和带符号数均适用

- `(x > y) - (x < y)`
- `(x >= y) - (x <= y)`

## 循环移位

- 无符号整数循环左移: `(x << n) | (x >> (32 - n))`
- 无符号整数循环右移: `(x >> n) | (x << (32 - n))`

## 互换寄存器中的值

```text
x = x ^ y
y = x ^ y
x = x ^ y
```

## 在两个值之间切换

假设 x 的取值只可能是 a 或 b, 而现在需要将 x 设置为与当前值不同的另一个值. 有下面两种做法(无需理会可能的溢出):

- `x = a + b - x`
- `x = a ^ b ^ x`

## 将数值上调/下调为 2 的已知次幂的倍数

如果想将无符号整数 x 下调为一个值最接近它同时还是 8 的倍数的数, 那么只需要执行 `x & -8` 就可以了. 如果我们规定"下调"指的是向负无穷方向, 那么这个算法同样适合带符号整数. 上调和下调一样容易, 只需要执行 `(x + 7) & -8`. 上调还有另一个公式 `x + (-x & 7)`, 因此如果你想知道最少给 x 加上几才能把它变成 8 的倍数, 那么用 `-x & 7` 就能算出来.

如果想把一个带符号数朝 0 方向调整为值最接近它且能被 8 整除的数, 那么可以应用下面的算法:

```text
t = (x >> 31) & 7
r = (x + t) & -8
```

一个典型的应用是在 x86 调用约定中, 在发起 call 之前 sp 必须是 16 的倍数(16 byte aligned), 此时可以使用汇编代码:

```text
and rsp, -15
```

## 调整到上一个/下一个 2 的幂

将无符号数 x 下调为不大于 x 且与之最近的 2 的幂

```c
uint32_t flp2(uint32_t x) {
    x = x | (x >> 1);
    x = x | (x >> 2);
    x = x | (x >> 4);
    x = x | (x >> 8);
    x = x | (x >> 16);
    return x - (x >> 1);
}
```

上调整为下一个 2 的幂

```c
uint32_t clp2(uint32_t x) {
    x = x - 1;
    x = x | (x >> 1);
    x = x | (x >> 2);
    x = x | (x >> 4);
    x = x | (x >> 8);
    x = x | (x >> 16);
    return x + 1;
}
```

## 判断取值范围是否跨越了 2 的幂边界

假定从地址 0 开始将内存划分为大小为 2 的幂的若干块(一个常见的值是 4 KB). 然后, 给定起始地址 a 和长度 l, 我们希望确定地址范围从 a 到 a + l - 1(l >= 2)，是否跨过一个块边界. a 和 l 是无符号整数, 并且可能是任何值. 注意, 当 l 为 0 或 1 时, 永远不会跨越块边界.

这种判断在内存管理方面有很大的作用, 例如按照块来延迟内存的初始化. 假设块的大小是 8, 可以使用如下公式判断:

```text
8 - (a & 7) < l;
```

## 统计值为 1 的位元数

种群计数(population count)函数, 也常常被简写为 pop, popcnt 或 pcnt.

有一种"分治法"可以巧妙的计算这个值: 首先, 把邻近的两个位元值编组为 1 个位段, 将这两个位元的值相加, 把结果放到宽度为 2 的位段中, 然后把邻近的两个二元位段相加, 将结果放到宽度为 4 的位段中, 以此类推. 这种算法利用了"分而治之"的想法, 将一个大问题(统计 32 个位元中值为 1 的个数)化为两个小问题(统计 16 个位元中值为 1 的个数), 分别将其解决, 然后合并结果.

```text
| 1 0   1 1   1 1   0 0   0 1   1 0   0 0   1 1   0 1   1 1   1 1   1 0   1 1   1 1   1 1   1 1 |
| 0 1 | 1 0 | 1 0 | 0 0 | 0 1 | 0 1 | 0 0 | 1 0 | 0 1 | 1 0 | 1 0 | 0 1 | 1 0 | 1 0 | 1 0 | 1 0 |
| 0 0   1 1 | 0 0   1 0 | 0 0   1 0 | 0 0   1 0 | 0 0   1 1 | 0 0   1 1 | 0 1   0 0 | 0 1   0 0 |
| 0 0   0 0   0 1   0 1 | 0 0   0 0   0 1   0 0 | 0 0   0 0   0 1   1 0 | 0 0   0 0   1 0   0 0 |
| 0 0   0 0   0 0   0 0   0 0   0 0   1 0   0 1 | 0 0   0 0   0 0   0 0   0 0   0 0   1 1   1 0 |
| 0 0   0 0   0 0   0 0   0 0   0 0   0 0   0 0   0 0   0 0   0 0   0 0   0 0   0 1   0 1   1 1 |
```

使用 C 语言实现, 即:

```c
uint32_t pcnt(uint32_t x) {
    x = (x & 0x55555555) + ((x >> 1) & 0x55555555);
    x = (x & 0x33333333) + ((x >> 2) & 0x33333333);
    x = (x & 0x0F0F0F0F) + ((x >> 4) & 0x0F0F0F0F);
    x = (x & 0x00FF00FF) + ((x >> 8) & 0x00FF00FF);
    x = (x & 0x0000FFFF) + ((x >> 16) & 0x0000FFFF);
    return x;
}
```

除此之外有很多其它优化方式和其它算法, 这里不表.

## 前导 0 计数

前导 0 计数也可以利用二分搜索计数实现.

```c
uint32_t clz(uint32_t x) {
    if (x == 0) return(32);
    uint32_t n = 0;
    if (x <= 0x0000FFFF) { n = n + 16; x = x << 16; }
    if (x <= 0x00FFFFFF) { n = n + 8; x = x << 8; }
    if (x <= 0x0FFFFFFF) { n = n + 4; x = x << 4; }
    if (x <= 0x3FFFFFFF) { n = n + 2; x = x << 2; }
    if (x <= 0x7FFFFFFF) { n = n + 1; }
    return n;
}
```

## 后缀 0 计数

计算后缀 0 个数的一种方法是将其转换为求前导 0 计数问题:

```text
32 - clz(!x & (x - 1))
```