# Solana/更多开发者工具/Anchor 测试框架

当你写下第一行合约代码, 测试就是它开口说的第一句话. 我们希望它既能在框架下顺畅表达, 也能在底层协议里自证严谨. 本节把测试当成一段小旅程: 先用 anchor 自带的 ts 测试框架走一条铺好的大道, 再用 python 下的 pxsol 客户端走一条原野小路(直接按二进制协议构造交易数据).

目标很朴素: 在本地链上, 初始化一个数据存储器, 多次更新内容, 然后把它读回来确认数据无误. 路径与代码都在仓库的 `tests/` 目录里.

## TypeScript

这条路最省心. 你只需要告诉 anchor: 我要哪个程序, 要调用这个程序的哪个指令, 带上哪些账户与参数. 其余的编解码与账户核验, 由 anchor 和 idl 替你完成.

> Anchor 的 idl 会在你第一次构建程序时自动生成. 它记录了程序 id, 每个指令的账户与参数, 以及每个账户的数据结构. 你可以把它想象成一个桥梁, 连接链上程序与链下客户端.

我们的测试很比较简单, 先调用一次 init, 然后调用两次 update, 每次都传入不同长度的内容. 每次调用后, 我们都 fetch 一次账户数据, 确认内容正确.

```ts
import * as anchor from "@coral-xyz/anchor";
import { Program } from "@coral-xyz/anchor";
import { PxsolSsAnchor } from "../target/types/pxsol_ss_anchor";

describe("pxsol-ss-anchor", () => {
  // Configure the client to use the local cluster.
  anchor.setProvider(anchor.AnchorProvider.env());
  const program = anchor.workspace.pxsolSsAnchor as Program<PxsolSsAnchor>;
  const provider = anchor.getProvider() as anchor.AnchorProvider;
  const wallet = provider.wallet as anchor.Wallet;
  const walletPda = anchor.web3.PublicKey.findProgramAddressSync(
    [Buffer.from("data"), wallet.publicKey.toBuffer()],
    program.programId
  )[0];

  it("Init with content and then update (grow and shrink)", async () => {
    // Airdrop SOL to fresh authority to fund rent and tx fees
    await provider.connection.confirmTransaction(await provider.connection.requestAirdrop(
      wallet.publicKey,
      2 * anchor.web3.LAMPORTS_PER_SOL
    ), "confirmed");

    const poemInitial = Buffer.from("");
    const poemEnglish = Buffer.from("The quick brown fox jumps over the lazy dog");
    const poemChinese = Buffer.from("片云天共远, 永夜月同孤.");
    const walletPdaData = async (): Promise<Buffer<ArrayBuffer>> => {
      let walletPdaData = await program.account.data.fetch(walletPda);
      return Buffer.from(walletPdaData.data);
    }

    await program.methods
      .init()
      .accounts({
        user: wallet.publicKey,
        userPda: walletPda,
        systemProgram: anchor.web3.SystemProgram.programId,
      })
      .signers([wallet.payer])
      .rpc();
    if (!(await walletPdaData()).equals(poemInitial)) throw new Error("mismatch");

    await program.methods
      .update(poemEnglish)
      .accounts({
        user: wallet.publicKey,
        userPda: walletPda,
        systemProgram: anchor.web3.SystemProgram.programId,
      })
      .signers([wallet.payer])
      .rpc();
    if (!(await walletPdaData()).equals(poemEnglish)) throw new Error("mismatch");

    await program.methods
      .update(poemChinese)
      .accounts({
        user: wallet.publicKey,
        userPda: walletPda,
        systemProgram: anchor.web3.SystemProgram.programId,
      })
      .signers([wallet.payer])
      .rpc();
    if (!(await walletPdaData()).equals(poemChinese)) throw new Error("mismatch");
  });
});
```

运行:

```bash
# 自动构建, 部署到本地链并运行 ts 测试
$ anchor test
```

## Python Pxsol

这条路更贴近协议本身. 我们会亲手排列账户列表, 拼接 8 字节方法 discriminator, 再把 4 字节小端长度与原始字节流接在后头. 它适合跨语言集成, 或在没有 anchor 客户端的环境里验算每一步.

代码如下:

```py
import argparse
import base64
import pxsol


parser = argparse.ArgumentParser()
parser.add_argument('--net', type=str, choices=['develop', 'mainnet', 'testnet'], default='develop')
parser.add_argument('--prikey', type=str, default='11111111111111111111111111111112')
parser.add_argument('args', nargs='+')
args = parser.parse_args()

user = pxsol.wallet.Wallet(pxsol.core.PriKey.base58_decode(args.prikey))
prog_pubkey = pxsol.core.PubKey.base58_decode('GS5XPyzsXRec4sQzxJSpeDYHaTnZyYt5BtpeNXYuH1SM')
data_pubkey = prog_pubkey.derive_pda(b'data' + user.pubkey.p)[0]


def init():
    rq = pxsol.core.Requisition(prog_pubkey, [], bytearray())
    rq.account.append(pxsol.core.AccountMeta(user.pubkey, 3))
    rq.account.append(pxsol.core.AccountMeta(data_pubkey, 1))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
    rq.data = bytearray().join([
        bytearray([220, 59, 207, 236, 108, 250, 47, 100]),
    ])
    tx = pxsol.core.Transaction.requisition_decode(user.pubkey, [rq])
    tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
    tx.sign([user.prikey])
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    pxsol.rpc.wait([txid])
    r = pxsol.rpc.get_transaction(txid, {})
    for e in r['meta']['logMessages']:
        print(e)


def update():
    rq = pxsol.core.Requisition(prog_pubkey, [], bytearray())
    rq.account.append(pxsol.core.AccountMeta(user.pubkey, 3))
    rq.account.append(pxsol.core.AccountMeta(data_pubkey, 1))
    rq.account.append(pxsol.core.AccountMeta(pxsol.program.System.pubkey, 0))
    rq.data = bytearray().join([
        bytearray([219, 200, 88, 176, 158, 63, 253, 127]),
        len(args.args[1].encode()).to_bytes(4, 'little'),
        args.args[1].encode(),
    ])
    tx = pxsol.core.Transaction.requisition_decode(user.pubkey, [rq])
    tx.message.recent_blockhash = pxsol.base58.decode(pxsol.rpc.get_latest_blockhash({})['blockhash'])
    tx.sign([user.prikey])
    txid = pxsol.rpc.send_transaction(base64.b64encode(tx.serialize()).decode(), {})
    pxsol.rpc.wait([txid])
    r = pxsol.rpc.get_transaction(txid, {})
    for e in r['meta']['logMessages']:
        print(e)


def load():
    info = pxsol.rpc.get_account_info(data_pubkey.base58(), {})
    print(base64.b64decode(info['data'][0])[8 + 32 + 1 + 4:].decode())


if __name__ == '__main__':
    eval(f'{args.args[0]}()')
```

运行:

```bash
$ solana-test-validator -l /tmp/solana-ledger
$ anchor deploy
# Program Id: GS5XPyzsXRec4sQzxJSpeDYHaTnZyYt5BtpeNXYuH1SM

$ python tests/pxsol-ss-anchor.py update "The quick brown fox jumps over the lazy dog"
$ python tests/pxsol-ss-anchor.py load
# The quick brown fox jumps over the lazy dog

$ python tests/pxsol-ss-anchor.py update "片云天共远, 永夜月同孤."
$ python tests/pxsol-ss-anchor.py load
# 片云天共远, 永夜月同孤.
```
