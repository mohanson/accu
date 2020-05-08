# WebAssembly 二进制格式文件解析

WebAssembly 二进制文件(模块)编码按照 section 区分, 除了将函数分为定义和代码实现两部分, 大多数部分与模块中保存的一个 section 相对应.

每个 section 包括:

- section id, 大小一字节.
- section size, 格式为 u32, 记录 section 大小.
- data，section 中保存的实际内容, 格式取决于 section id.

每个 section 都是可选的, 省略的部分等同于存在空白内容的 section.

总共存在 11 种不同类型的 section, 它们分别是:

Id  |     Section
--- | ----------------
0   | custom section
1   | type section
2   | import section
3   | function section
4   | table section
5   | memory section
6   | global section
7   | export section
8   | start section
9   | element section
10  | code section
11  | data section

每个 section 具体的格式可参看 wasm 官方文档, 此处进行使用 pywasm 来解析 wasm module 的演示. 首先, 下载 wasm module 到本地电脑, 地址: [https://github.com/mohanson/pywasm/blob/master/examples/add.wasm](https://github.com/mohanson/pywasm/blob/master/examples/add.wasm). 该模块实现了一个 i32 整数加法运算, 编译自 C 代码, 位于同目录中.

编写如下 python 代码:

```py
import pywasm

pywasm.on_debug()

pywasm.load('add.wasm')
```

由于开启了 debug 模式, 其 section 信息将被打印至标准输出, 如下:

```no-highlight
2020/05/08 23:58:12 type_section([function_type(result_type([i32, i32]), result_type([i32]))])
2020/05/08 23:58:12 function_section([type_index(0)])
2020/05/08 23:58:12 table_section([table(table_type(funcref, limits(0, 0)))])
2020/05/08 23:58:12 memory_section([memory(memory_type(limits(1, 0)))])
2020/05/08 23:58:12 global_section([])
2020/05/08 23:58:12 export_section([export(memory, memory_index(0)), export(add, function_index(0))])
2020/05/08 23:58:12 code_section([code(7, func([], expression([local.get [local_index(1)], local.get [local_index(0)], i32.add [], end []])))])
```

可看到该模块包含的所有 section 信息.

# 参考

- [1] WebAssembly Specification, Binary Format, Module [https://webassembly.github.io/spec/core/binary/modules.html](https://webassembly.github.io/spec/core/binary/modules.html)
