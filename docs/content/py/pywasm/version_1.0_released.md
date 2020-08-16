# pywasm 1.0 版本发布

在过去的一段时间里, pywasm 加足马力, 一口气将自身版本号从 0.4.6 版本升到 1.0.0 版本, 这意味着它已经做好了 Ready for product 的准备!

pywasm 是什么? pywasm 是使用纯 Python 编写的 WebAssembly 解释器. 项目地址: [https://github.com/mohanson/pywasm](https://github.com/mohanson/pywasm)

# pywasm 在这段时间干了什么?

**重写 LEB128 不定长整数编码算法**. 它是 python 环境下第一个关于 LEB128 算法的轮子, 你可以直接 `pip install leb128` 来下载和使用它. 相比起 0.4.6 版本, 它带来了大约 120% 左右的性能提升.

**重写 WebAssembly Parser**. 要运行一段代码首先得解析它, 不是吗? 更快, 代码更清晰!

**重写浮点数指令**. 在 0.4.6, 浮点数使用 python 内置 float 来完成, 但这存在问题, 因为 Python 的 float 几乎完全不符合 IEEE 754 标准. 现在, numpy 承担了这部分工具. Python, 为甚么你就不愿意好好的设计整数和浮点数这两种基本类型呢? 不定长的整数和浮点数看上去很吸引人, 但对于底层开发来说真的是大灾难.

**重写 Runtime 结构**. 目前的代码结构更加符合 WebAssembly 核心规范所描述的虚拟机结构. 这存粹是为了方便阅读而作的优化.

**采用多栈结构替换单栈结构**. 每一个函数调用都有一个全新的栈, 虽然和规范有所出入, 但真的很 awesome! 另外多栈的好处是调用栈的快速销毁: 当退出一个函数时, 直接抛弃该函数的栈即可, 而无需过多与父函数交互.

**完整的兼容性**. 为了不破坏早期使用者的体验, 此次升级保持向上兼容.

**完整的测试**. pywasm 项目的启动是在 3 年前, 那时候 WebAssembly 还处在早期阶段, 官方并未发布组织结构良好的测试用例. 在发现官方将四处散落的测试用例集合并以一个 Mirror repo 公布时, pywasm 立即更新了自身的测试. 对于解析和验证无误的 wasm module, pywasm 已经做到 100% 测试通过.

# pywasm 有哪些有趣的应用?

- [https://github.com/dholth/zstdpy/](https://github.com/dholth/zstdpy/). 使用 pywasm 作为运行时执行 zstd 压缩算法, 作者 Daniel Holth 是 pypa(Python 官方包管理工具) 成员之一.
- [https://github.com/mohanson/pywasm_assemblyscript](https://github.com/mohanson/pywasm_assemblyscript). AssemblyScript 现在不但可以运行在浏览器上, 还能跑在 Python 中! 只需要一个 npm 命令, 不尝试一下吗?

# pywasm 的未来

- 思考 JIT 或 AOT 方案. 虽然已经有初步尝试, 但它需要外援!
- WASI(WebAssembly System Interface), 不过这得等该规范 stable 后开始动手.
- 多线程和多返回值支持, 同样得等该规范 merge 入 wasm core spec 后开始动手.

# 对 WebAssembly 的思考和吐槽

这家伙不是一个指令集标准, 而是一门语言标准! 它在运行过程中上下文环境太强, 这与我认知的 ISA 有着天壤之别, 更像是一门二进制编程语言...
