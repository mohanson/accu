# Cryptography/多项式运算

多项式(英语: Polynomial)是代数学中的基础概念, 是由称为未知数的变量和称为系数的常数通过有限次加减法, 乘法以及自然数幂次的乘方运算得到的代数表达式.

给定一个环 R(R 通常是交换环, 可以是有理数, 实数或者复数等等)以及一个未知数 x, 则任何形同:

```text
a₀ + a₁⋅x + a₂⋅x² ... + aₙ⋅xⁿ
```

的代数表达式叫做 R 上的一元多项式. N 称作该多项式的 degree.

## 多项式加法和减法

接下来的代码我们使用一个数组来表示一个多项式. 在数组中, 系数从低到高排列, 例如, [1, 2, 3] 表示 1 + 2x + 3x². 考虑如下两个多项式:

```py
px = [4, -2, 5] # p(x) = 5x² - 2x + 4
qx = [2, -5, 2] # q(x) = 2x² - 5x + 2
```

```py
def polyadd(c1, c2):
    return [c1[i] + c2[i] for i in range(len(c1))]


def polysub(c1, c2):
    return [c1[i] - c2[i] for i in range(len(c1))]

assert polyadd(px, qx) == [6, -7, 7] # 7x² - 7x + 6
assert polysub(px, qx) == [2, 3, 3]  # 3x² + 3x + 2
```

## 多项式乘法

```py
def polymul(c1, c2):
    p = [0 for _ in range(len(c1) + len(c2) - 1)]
    for i in range(len(c1)):
        for j in range(len(c2)):
            p[i+j] += c1[i] * c2[j]
    return p

assert polymul(px, qx) == [8, -24, 28, -29, 10] # 10x⁴ - 29x³ + 28x² - 24x + 8
```

## 多项式除法

需要使用 Polynomial long division 算法.

```py
def polydivmod(c1, c2):
    # Algorithm: https://en.wikipedia.org/wiki/Polynomial_long_division
    # The code implementation is inspired by numpy.polynomial.polynomial.polydiv
    lc1 = len(c1)
    lc2 = len(c2)
    if lc1 < lc2:
        return [], c1
    if lc2 == 1:
        return [e / c2[0] for e in c1], []
    dif = lc1 - lc2
    scl = c2[-1]
    nc1 = c1.copy()
    nc2 = [e/scl for e in c2[:-1]]
    i = dif
    j = lc1 - 1
    while i >= 0:
        for k in range(lc2 - 1):
            nc1[i+k] -= nc2[k]*nc1[j]
        i -= 1
        j -= 1
    return [i/scl for i in nc1[j+1:]], nc1[:j+1]

def polydiv(c1, c2):
    return polydivmod(c1, c2)[0]


def polymod(c1, c2):
    return polydivmod(c1, c2)[1]

assert polydiv(px, qx) == [2.5]      # 2.5
assert polymod(px, qx) == [-1, 10.5] # 10.5x - 1
```

## 多项式求模逆

多项式的模逆要用到扩展欧几里得算法(Extended euclidean algorithm). 所谓的模逆就是 i1 * c1 % c2 == 1, 其中 i1 为 c1 关于 c2 的模逆.

```py
def polydeg(c1):
    d = len(c1) - 1
    while c1[d] == 0 and d:
        d -= 1
    return d

def polyinv(c1, c2):
    # Algorithm: https://en.wikipedia.org/wiki/Extended_Euclidean_algorithm
    newt, t = [1], [0]
    newr, r = c1, c2
    while polydeg(newr):
        quotient = polydiv(r, newr)
        r, newr = newr, polysub(r, polymul(newr, quotient))
        t, newt = newt, polysub(t, polymul(newt, quotient))
    return [e/newr[0] for e in newt[:polydeg(c2)]]

assert polymod(polymul(polyinv(px, qx), px), qx)[0] == 1
```

完整代码: <https://github.com/mohanson/cryptography-python/blob/master/polynomial.py>

## 使用 Numpy 计算多项式

```py
import numpy

# p(x) = 5x² - 2x + 4
px = [4, -2, 5]

# q(x) = 2x² - 5x + 2
qx = [2, -5, 2]

r = numpy.polynomial.polynomial.polyadd(px, qx)
print('polyadd', r)  # 7x² - 7x + 6
r = numpy.polynomial.polynomial.polysub(px, qx)
print('polysub', r)  # 3x² + 3x + 2
r = numpy.polynomial.polynomial.polymul(px, qx)
print('polymul', r)  # 10x⁴ - 29x³ + 28x² - 24x + 8
quo, rem = numpy.polynomial.polynomial.polydiv(px, qx)
print('polydiv quo', quo)  # 2.5
print('polydiv rem', rem)  # 10.5x - 1
```

## 参考

- [1] [Wikipedia, 多项式.](https://zh.wikipedia.org/wiki/%E5%A4%9A%E9%A0%85%E5%BC%8F)
