# Cryptography/椭圆曲线空间扩展之 Jacobian

椭圆曲线上的计算可以通过空间映射(Projective Space)进行一定程度的加速, 映射的本质上是将二维坐标系中的点加上无穷远点映射到三维坐标系的直线.

二维到三维:

```text
(x, y) -> (x, y, 1)
     O -> (0, 1, 0)
```

三维到二维:

```text
(x, y, z) -> (x / z, y / z)
(x, y, 0) -> O
```

可以注意到对于任意 a != 0, (ax, ay, az) 表示的是同一个点.

使用三元组进行椭圆曲线群运算的好处在于可以避免除法计算--通常进行除法的时间复杂度是进行乘法的 9 至 40 倍. 当我们用三元组 P = (x₁, y₁, z₁), Q = (x₂, y₂, z₂) 来计算 P + Q = (x₃, y₃, z₃) 时

- 如果 P != ±Q

```text
u = y₂z₁ - y₁z₂
v = x₂z₁ - x₁z₂
w = u²z₁z₂ - v³ - 2v²x₁z₂
x₃ = vw
y₃ = u(v²x₁z₂ - w) - v³y₁z₂
z₃ = v³z₁z₂
```

- 如果 P == +Q

```text
t = az₁² + 3x₁²
u = y₁z₁
v = ux₁y₁
w = t² - 8v
x₃ = 2uw
y₃ = t(4v - w) - 8y₁²u²
z₃ = 8u³
```

- 如果 P == -Q

```text
x₃ = 0
y₃ = 1
z₃ = 0
```

在 Jacobian 映射下不需要再特殊处理无穷远点, 并且计算过程不包含除法, 大大提高了计算速度.

## 代码实现

```
import secp256k1


class EcJacobian:
    def __init__(self, x, y, z):
        self.x = x
        self.y = y
        self.z = z

    @classmethod
    def encode(cls, ec):
        if ec == secp256k1.I:
            return EcJacobian(secp256k1.Fp(0), secp256k1.Fp(1), secp256k1.Fp(0))
        else:
            return EcJacobian(ec.x, ec.y, secp256k1.Fp(1))

    def decode(self):
        if self.z == secp256k1.Fp(0):
            return secp256k1.I
        else:
            return secp256k1.Ec(self.x / self.z, self.y / self.z)

    def double(self):
        x, y, z = self.x, self.y, self.z
        a = secp256k1.Fp(3) * x * x
        b = y * z
        c = x * y * b
        d = a * a - secp256k1.Fp(8) * c
        e = b * b
        f = secp256k1.Fp(2) * d * b
        g = a * (secp256k1.Fp(4) * c - d) - secp256k1.Fp(8) * y * y * e
        h = secp256k1.Fp(8) * b * e
        return EcJacobian(f, g, h)

    def __add__(self, other):
        x1, y1, z1 = self.x, self.y, self.z
        x2, y2, z2 = other.x, other.y, other.z
        if z1 == secp256k1.Fp(0):
            return other
        if z2 == secp256k1.Fp(0):
            return self
        u1 = y2 * z1
        u2 = y1 * z2
        v1 = x2 * z1
        v2 = x1 * z2
        if v1 == v2:
            if u1 != u2:
                return EcJacobian.encode(secp256k1.I)
            else:
                return self.double()
        u = u1 - u2
        v = v1 - v2
        w = z1 * z2
        a = v * v
        b = a * v2
        c = v * a
        d = u * u * w - c - b * secp256k1.Fp(2)
        x3 = v * d
        y3 = u * (b - d) - c * u2
        z3 = c * w
        return EcJacobian(x3, y3, z3)


p = secp256k1.G * 42
q = secp256k1.G * 24
assert p + q == secp256k1.G * 66
assert (EcJacobian.encode(p) + EcJacobian.encode(q)).decode() == secp256k1.G * 66

assert p + p == secp256k1.G * 84
assert (EcJacobian.encode(p) + EcJacobian.encode(p)).decode() == secp256k1.G * 84

q = secp256k1.Ec(p.x, -p.y)
assert p + q == secp256k1.I
assert (EcJacobian.encode(p) + EcJacobian.encode(q)).decode() == secp256k1.I
```

完整代码: <https://github.com/mohanson/cryptography-python>

## 参考

- [1] [熠智科技. 椭圆曲线科普, 3.4 Projective Space.](https://download.yeez.tech/doc/ECcurve.pdf)
- [2] [Anonymous. Wikibooks.](https://en.wikibooks.org/wiki/Cryptography/Prime_Curve/Jacobian_Coordinates)
