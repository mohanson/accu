# 以太坊: 智能合约

现在你已经掌握了如何使用以及如何交易以太的基础知识, 现在是时候弄清楚真正让以太坊脱颖而出的地方: 智能合约. 智能合约是生活在区块链上的代码片段, 它们完全代码执行命令. 它们可以阅读其他智能合约, 做出决定, 交易以太并执行其他合约. 只要整个网络存在, 智能合约就会存在并运行, 只有当它们耗尽 Gas 或者它们被编程为自毁时才会停止.

你可以用合约做什么? 你几乎可以做任何事情, 但是对于本指南, 让我们做一些简单的事情: 你将在合约中存储一段数据, 并且可供所有人访问.

那么现在就开始吧.

# Truffle

Truffle 是以太坊智能合约开发框架. 使用 truffle 之前确保已经安装 nodejs, 并使用如下命令安装 truffle:

```sh
$ npm install -g truffle
```

为了创建一个项目, 请在一个空目录中运行(本章中我们的目录名为 storage)

```sh
$ truffle init
```

一切顺利的话, 你将看到 truffle 为你生成了以下目录结构:

```no-highlight
drwxr-xr-x 1 mohan 197609   0 Jul  4 10:27 contracts
drwxr-xr-x 1 mohan 197609   0 Jul  4 10:27 migrations
drwxr-xr-x 1 mohan 197609   0 Jul  4 10:27 test
-rw-r--r-- 1 mohan 197609 545 Jul  4 10:27 truffle-config.js
-rw-r--r-- 1 mohan 197609 545 Jul  4 10:27 truffle.js
```

# Solidity

Solidity 是一门面向合约的, 为实现智能合约而创建的高级编程语言. 这门语言受到了 C++, Python 和 Javascript 语言的影响, 设计的目的是能在 EVM(以太坊虚拟机) 上运行.

文档: [http://solidity.readthedocs.io/en/v0.4.24/](http://solidity.readthedocs.io/en/v0.4.24/)

我们将使用 Solidity 编写我们的第一份智能合约.

# 编写代码

首先在 contracts/ 目录下新建一个 Storage.sol 文件, 并键入以下内容

```no-highlight
pragma solidity ^0.4.0;

contract Storage {
    uint storedData;

    function set(uint x) public {
        storedData = x;
    }

    function get() public constant returns (uint) {
        return storedData;
    }
}
```

注意到在代码首行我们使用 `pragma solidity ^0.4.0;` 声明编译该份代码需要的 solidity 编译器版本必须 >= 0.4.0. 随后定义了一个 Storage 合约, 合约内部有一个 storedData 属性和两个方法.

在 /migrations 目录下新建 2_deploy_contracts.js, 并键入以下内容

```js
var Storage = artifacts.require("./Storage.sol");

module.exports = function(deployer) {
      deployer.deploy(Storage);
};
```

编辑 /truffle.js 文件, 键入:

```js
var HDWalletProvider = require('truffle-privatekey-provider')

module.exports = {
  networks: {
    ropsten: {
      provider: new HDWalletProvider(
        '------------------------private key-----------------------------', 'https://ropsten.infura.io'),
      network_id: '*',
      gas: 4000000,
      from: '0xeb1379888f6117386043b1e50aafa983006958d8'
    }
  }
};
```

注意到这里我们使用了 truffle-privatekey-provider 依赖, 并且你需要在 HDWalletProvider 中填入自己的私钥, 在 from 中填入自己的地址. 确保该地址下有足够的以太完成合约发布.

# 发布合约

使用如下命令发布合约. 在合约发布过程中, 视网络情况需耗费几分钟左右.

```sh
$ truffle migrate --network ropsten
```

发布日志

```no-highlight
Using network 'ropsten'.

Running migration: 1_initial_migration.js
  Deploying Migrations...
  ... 0x57292ffb1af07429e39d6097c746d87333297fc2e20afa6a73af7ea099c5cc20
  Migrations: 0xdda1c2d592b83df75d70f370a919017a07201065
Saving successful migration to network...
  ... 0x25f24012e240d8c3a8897c944a4177b72869618550051970494fd2430f065185
Saving artifacts...
Running migration: 2_deploy_contracts.js
  Deploying Storage...
  ... 0x10c7307e8a932455743c1c5543a3672c3e0b2af672e38f396fde468f5a2171bb
  Storage: 0xb31163a22f1a51f2a9c5ebe80b7fe529744cb20e
Saving successful migration to network...
  ... 0xfdb77c967faa312b38f489b480e200bba7fbb0e2bf35f4322ad411e498424667
Saving artifacts...
```

# 测试合约

使用 truffle console 进入交互式命令行:

```sh
$ truffle console --network ropsten
```

调用 `set` 方法赋值数据.

```js
Storage.deployed().then(
  instance => instance.set.sendTransaction(42)
).then(
  result => newStorageData = result
)
```

调用 `get` 方法获取数据.

```js
Storage.deployed().then(
  instance => instance.get.call()
).then(
  result => storeData = result
)
```

> 你可能注意到调用 set 方法时使用了 sendTransaction, 而调用 get 方法时使用了 call. 当方法修改了区块链数据时, 需明确的发送一个交易, 因而使用 sendTransaction.
