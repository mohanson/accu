# Solana/账户模型/程序派生地址算法解析

在 solana 上开发程序, 您早晚会需要使用程序派生地址(pda 地址). 简单说, 这是一种专属于您程序的数据账户地址, 可以用来保存数据, 但它跟普通钱包地址不一样, 它**没有私钥**, 别人也没法控制它, 只有您的程序能指挥它做事.

## 如何生成

程序派生地址是程序根据一组种子(可以是字符串, 钱包地址等)加上自己的公钥算出来的一个地址. 它不是随机生成的, 而是可以预先计算, 可预测的. 这个地址不会对应任何私钥, 所以没人能签名控制它, 包括程序作者本人.

这对去中心化程序(比如链上钱包, 订单簿, 投票系统)来说特别重要, 因为开发者经常要给每个用户分配一个账户, 但不想让他们自己管理这个账户的密钥, 否则用户可以直接手动修改数据账户内的数据为任意数据.

上个小节中有个例子:

```py
import pxsol

ada = pxsol.wallet.Wallet(pxsol.core.PriKey.int_decode(0x01))
thb = pxsol.core.PubKey.base58_decode('F782pXBcfvHvb8eJfrDtyD7MBtQDfsrihSRjvzwuVoJU')
pda = thb.derive_pda(ada.pubkey.p)[0]
print(pda) # HCPe787nPq7TfjeFivP9ZvZwejTAq1PGGzch93qUYeC3
```

这样几行代码就能生成一个程序派生地址, 通常我们会把它当作用户在该程序下的数据存储账户.

## 算法解释

Solana 的密钥对是 ed25519 曲线上的点, 包含一个公钥和对应的私钥. 公钥用作链上账户的地址.

程序派生地址是一个通过预定义输入集有意生成的点, 必须位于 ed25519 曲线之外. 位于 ed25519 曲线之外的点没有有效的对应私钥, 无法执行普通意义上的签名操作. 相应的, solana 网络为程序派生地址开了个特殊的后门, 程序可以为自己的派生地址进行模拟签名操作.

生成程序派生地址算法过程如下:

1. 把种子和程序公钥拼在一起.
2. 给它加一个叫 bump 的值(从 255 开始向下尝试).
3. 每次拼完后算哈希, 看看算出来的地址在不在椭圆曲线上.
4. 若地址不在曲线上, 说明这个地址不可能被签名控制, 可以用作程序派生地址.

详细代码实现如下:

```py
class PubKey:
    # Solana's public key is a 32-byte array. The base58 representation of the public key is also referred to as the
    # address.

    def __init__(self, p: bytearray) -> None:
        assert len(p) == 32
        self.p = p

    def derive_pda(self, seed: bytearray) -> typing.Tuple[PubKey, int]:
        # Program Derived Address (PDA). PDAs are addresses derived deterministically using a combination of
        # user-defined seeds, a bump seed, and a program's ID.
        # See: https://solana.com/docs/core/pda
        data = bytearray()
        data.extend(seed)
        data.append(0xff)
        data.extend(self.p)
        data.extend(bytearray('ProgramDerivedAddress'.encode()))
        for i in range(255, -1, -1):
            data[len(seed)] = i
            hash = bytearray(hashlib.sha256(data).digest())
            # The pda should fall off the ed25519 curve.
            if not pxsol.eddsa.pt_exists(hash):
                return PubKey(hash), i
        raise Exception
```

## 习题

例: Bump 是干嘛的?

答: 它是用来避免地址冲突的调节器. 如果某个种子组合生成的地址不合法, 程序就试着调 bump, 直到找到一个合法地址.

例: 程序派生地址能自己发交易吗?

答: 不行. 程序派生地址没有私钥, 因此它不能直接发交易, 只能被程序调用和控制.
