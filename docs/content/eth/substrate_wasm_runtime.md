# Substrate wasm runtime

先对 substrate 做一个一句话介绍: **使用 wasm 编写状态转换函数(STF)的 layer2 框架**.

## 接口定义

substrate 内部定义了一些函数接口, 开发者使用 wasm 模块实现这些函数, 即能接入 substrate 起一条链. 具体而言, 必要的函数定义在:

> ./substrate/core/client/src/[runtime_api.rs](http://runtime_api.rs/)

```rs
decl_runtime_apis! {
    /// The `Core` api trait that is mandantory for each runtime.
    #[core_trait]
    pub trait Core {
        /// Returns the version of the runtime.
        /// 返回 wasm 模块的版本号
        fn version() -> RuntimeVersion;

        /// Returns the authorities.
        /// 返回验证人列表(因为 substrate 使用的类 BFT 共识
        fn authorities() -> Vec<AuthorityIdFor<Block>>;

        /// Execute the given block.
        /// 执行区块, 包括区块中的所有交易
        fn execute_block(block: Block);

        /// Initialise a block with the given header.
        /// 初始化新区块的环境, 包括 block_number, 上个区块的哈希等
        fn initialise_block(header: &<Block as BlockT>::Header);
    }
}
```


其本质就是将 **execute_block()** 函数实现在 wasm 中!

Note: 与 tendermint 项目有点类似, tendermint 也可以由用户自定义 execute_block() 的逻辑, 区别在于 tendermint 通过 rpc 与用户写的进程交互而非 wasm.

在 ./substrate/core/client/src/block_builder/api.rs, ./substrate/core/consensus/aura/primitives/src/lib.rs 等源码中还有其他可选的接口定义, 不展开讲.

## wasm 模块分析

wasm 的能力比较有限, 最主要的问题是**它无法与链上信息交互**. 此时需要由宿主环境为其提供原生函数, wasm 可以在内部通过 import 的方式导入宿主环境函数.

这里分析一下 substrate 默认提供的 wasm 运行时是如何编写的.

首先生成创始配置文件:

```
$ substrate —chain=staging build-spec > /tmp/chainspec.json
```

使用如下代码分析配置文件内部的相关的 wasm 运行时代码:

```py
import json
import pywasm
pywasm.on_debug()

with open('/tmp/chainspec.json') as f:
    data = json.load(f)
    h = data['genesis']['runtime']['consensus']['code'][2:]
    b = bytes.fromhex(h)

    with open('/tmp/chainspec.wasm', 'wb') as f:
        f.write(b)

pywasm.structure.Module.load('/tmp/chainspec.wasm')
```

精简部分输出后结果如下, Import 行是 wasm 需要从宿主环境导入的函数, Export 行是 wasm 导出给宿主环境以供宿主环境调用的函数. 可以发现, wasm 从宿主机导入了 `env.ext_get_storage_into` 等 storage 相关函数以及 `env.ext_blake2_256`, `env.ext_ed25519_verify` 等哈希/签名函数.
同时导出了 Core_version, Core_execute_block 等 Core 函数.

```
Import[0] env.ext_get_storage_into -> Function[7]
Import[1] env.ext_twox_128 -> Function[4]
Import[2] env.ext_set_storage -> Function[5]
Import[3] env.ext_clear_storage -> Function[6]
Import[4] env.ext_clear_prefix -> Function[6]
Import[5] env.ext_storage_root -> Function[2]
Import[6] env.ext_storage_changes_root -> Function[8]
Import[7] env.ext_exists_storage -> Function[1]
Import[8] env.ext_blake2_256 -> Function[4]
Import[9] env.ext_print_utf8 -> Function[6]
Import[10] env.ext_sandbox_memory_new -> Function[1]
Import[11] env.ext_sandbox_memory_teardown -> Function[2]
Import[12] env.ext_print_hex -> Function[6]
Import[13] env.ext_sandbox_memory_get -> Function[9]
Import[14] env.ext_sandbox_memory_set -> Function[9]
Import[15] env.ext_ed25519_verify -> Function[9]
Import[16] env.ext_sandbox_instantiate -> Function[10]
Import[17] env.ext_sandbox_invoke -> Function[11]
Import[18] env.ext_sandbox_instance_teardown -> Function[2]
Import[19] env.ext_blake2_256_enumerated_trie_root -> Function[5]
Import[20] env.ext_print_num -> Function[12]
Import[21] env.ext_malloc -> Function[13]
Import[22] env.ext_free -> Function[2]

Export[4] Core_version -> Function[235]
Export[5] Core_authorities -> Function[236]
Export[6] Core_execute_block -> Function[237]
Export[7] Core_initialise_block -> Function[244]
Export[8] Metadata_metadata -> Function[245]
Export[9] BlockBuilder_apply_extrinsic -> Function[249]
Export[10] BlockBuilder_finalise_block -> Function[250]
Export[11] BlockBuilder_inherent_extrinsics -> Function[252]
Export[12] BlockBuilder_check_inherents -> Function[253]
Export[13] BlockBuilder_random_seed -> Function[254]
Export[14] TaggedTransactionQueue_validate_transaction -> Function[255]
Export[15] GrandpaApi_grandpa_pending_change -> Function[257]
Export[16] GrandpaApi_grandpa_authorities -> Function[258]
Export[17] AuraApi_slot_duration -> Function[259]
```

## 关于 evm

substrate medium 文章谈到了 evm, 总结一下: substrate 可以集成 evm, 但不推荐.

## 参考资料

- [1] [substrate.readme.io](https://substrate.readme.io/docs/glossary)
- [2] [如何搭建 substrate 链?](https://gitlab.com/chrisdcosta/basictest/blob/master/Howto.md)
