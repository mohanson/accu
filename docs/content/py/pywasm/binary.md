# WebAssembly 二进制格式文件解析

WebAssembly 二进制文件(模块)编码按照 section 区分, 除了将函数分为定义和代码实现两部分, 大多数部分与模块中保存的一个 section 相对应.

每个 section 包括:

- section id, 大小一字节.
- section size, 格式为 u32, 记录 section 大小.
- data，section 中保存的实际内容, 格式取决于 section id.

每个 section 都是可选的, 如果某个 wasm 模块省略了某个 section, 则等同于存在一个内容为空的 section.

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

如果我此时直接将核心规范扔出来告诉你每个 section 的规则, 那可能会有点无聊, 因此我决定偷下懒, 我会使用一个真实的(且最小的) wasm 模块对其格式进行讲解, 并会要求你自学剩下的内容. 该模块文件由 C 编译而来, 其 C 源代码为:

```c
int add(int a, int b) {
    return a + b;
}
```

对应的 wasm 汇编代码为:

```no-highlight
(module
 (export "add" (func $add))
 (func $add (; 0 ;) (param $0 i32) (param $1 i32) (result i32)
  (i32.add
   (get_local $1)
   (get_local $0)
  )
 )
)
```

其二进制代码为(已经采用 16 进制表示):

```py
data = [
    0x00, 0x61, 0x73, 0x6d, 0x01, 0x00, 0x00, 0x00,
    0x01, 0x07, 0x01, 0x60, 0x02, 0x7f, 0x7f, 0x01,
    0x7f, 0x03, 0x02, 0x01, 0x00, 0x07, 0x07, 0x01,
    0x03, 0x61, 0x64, 0x64, 0x00, 0x00, 0x0a, 0x09,
    0x01, 0x07, 0x00, 0x20, 0x01, 0x20, 0x00, 0x6a,
    0x0b
]
```

**魔法数字与版本号**

首先来看前 8 个字节, 每个合法的 wasm 模块文件都包含一个 4 字节的魔法数字和一个 4 字节的版本号. 魔法数字的字符串表示为 `\0asm`, 对应的 ascii 码为 `[0x00, 0x61, 0x73, 0x6d]`. 版本号当前固定为 1, 对应的 ascii 码为 `[0x01, 0x00, 0x00, 0x00]`.

**类型分段**

```py
section_data = [0x01, 0x07, 0x01, 0x60, 0x02, 0x7f, 0x7f, 0x01, 0x7f]
```

在魔法数字与版本号之后, 跟着的便是众多的 section. 按照规定, 所有 section 按照 section id 顺序排列且最多只能出现一次. 唯一的例外是 custom section, 它可以任意次数出现在任意地方. wasm 解释器会忽略所有 custom section, 它存在的意义类似注释或标签, 作用在特殊场景.

我们取得的第一个字节是 `0x01`, 这意味着后面更着的是一个 type section. 下一步的目的获得 section size, 它是一个 u32, 并采用 leb128 编码. 您可以往回翻看 leb128 解码的过程, 但此处我便直接告诉你 section size 是 0x07. type section 内存储着模块内所有函数的签名, 在 section size 后跟着的内容是函数签名的数量, 字节为 `[0x01]`, 因此数量是 1. 每一个函数签名都以固定的 `0x60` 开头, 后面依次跟着函数的参数个数, 参数类型, 返回值个数和返回值类型, 它们是 `[0x02, 0x7f, 0x7f, 0x01, 0x7f]`, 翻译为便于阅读的函数签名格式, 则是

```no-highlight
func(i32, i32) -> i32
```

我们知道了 wasm 模块内至少有一个函数, 它接收两个 i32 类型的参数, 并返回一个 i32 类型的参数.

**函数分段**

```py
section_data = [0x03, 0x02, 0x01, 0x00]
```

只有函数签名是不够的, 因为多个函数可能拥有一个相同的签名, function section 会被解码为一个映射，告诉解析器某个函数的签名是什么. 它以 `0x03` 开头, `0x02` 告诉解析器 section size 为 2, 0x01 则说明该模块只有一个函数, 最后的 0x00 表明这唯一的函数签名索引为 0. 因此, 能得出如下的信息:

- 模块内只有一个函数
- 该函数的签名是 `func(i32, i32) -> i32`

**导出分段**

```py
section_data = [0x07, 0x07, 0x01, 0x03, 0x61, 0x64, 0x64, 0x00, 0x00]
```

正如大多数编程语言一样, wasm 内的函数也分为 private 和 public 两种访问权限. 只有 public 函数拥有函数名并且可被导出使用. 这部分信息被保存在 export section 中.  我们跳过 `[0x07, 0x07, 0x01]` 这三个字节, 相信读者一定已经知道它们分别代表了 section id, section size 和可导出函数的个数. 每个被导出的函数都包含三个部分, 分别是函数名, 对象类型和对象索引. 函数名是一个字符串, 在字符串的开头是字符串的长度, 因此代表函数名的字节是 `[0x61, 0x64, 0x64]`, ascii 表示为 `add`. 后面跟着的 0x00 是对象类型(函数), 最后的 0x00 为对象索引, 告诉解析器被导出的对象是在 function section 中索引为 0 的函数.

很好, 现在我们知道模块中大概保存了这样一个函数:

```no-highlight
pub func add(i32, i32) -> i32
```

**代码分段**

```py
section_data = [0x0a, 0x09, 0x01, 0x07, 0x00, 0x20, 0x01, 0x20, 0x00, 0x6a, 0x0b]
```

代码分段保存着函数的实现. 我不想再重复介绍, 让我们直接忽略前 4 个字节吧. `add` 函数的实现被保存为 `[0x00, 0x20, 0x01, 0x20, 0x00, 0x6a, 0x0b]`, 直接翻译为流水账式的汇编代码如下:

```no-highlight
local.get 1
local.get 0
i32.add
end
```

这正是 `add` 函数的代码实现.

# 使用 pywasm 进行解析

每个 section 具体的格式可参看 wasm 官方文档, 毕竟作为一名文档搬运工挺没意思的. 此处进行使用 pywasm 来解析 wasm module 的演示. 首先, 下载示例 wasm module 到本地电脑, 地址: [https://github.com/mohanson/pywasm/blob/master/examples/add.wasm](https://github.com/mohanson/pywasm/blob/master/examples/add.wasm).

```py
import pywasm

pywasm.on_debug()
pywasm.load('add.wasm')
```

由于开启了 debug 模式, 其 section 信息将被打印至标准输出, 如下所示.

```no-highlight
2020/05/08 23:58:12 type_section([function_type(result_type([i32, i32]), result_type([i32]))])
2020/05/08 23:58:12 function_section([type_index(0)])
2020/05/08 23:58:12 table_section([table(table_type(funcref, limits(0, 0)))])
2020/05/08 23:58:12 memory_section([memory(memory_type(limits(1, 0)))])
2020/05/08 23:58:12 global_section([])
2020/05/08 23:58:12 export_section([export(memory, memory_index(0)), export(add, function_index(0))])
2020/05/08 23:58:12 code_section([code(7, func([], expression([local.get [local_index(1)], local.get [local_index(0)], i32.add [], end []])))])
```

# 参考

- [1] WebAssembly Specification, Binary Format, Module [https://webassembly.github.io/spec/core/binary/modules.html](https://webassembly.github.io/spec/core/binary/modules.html)
