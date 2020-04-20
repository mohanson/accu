# Pywasm: Python 爱上 Wasm, 美味尝鲜!

pywasm 是一个使用纯 Python 实现的 WebAssembly 解释器. 您可以使用如下命令来安装它:

```sh
$ pip3 install pywasm
```

# WebAssembly

WebAssembly/wasm 是一个可移植, 体积小, 加载快并且兼容 Web 的全新格式. WebAssembly 是由主流浏览器厂商组成的 W3C 社区团体 制定的一个新的规范.

- 高效: WebAssembly 有一套完整的语义, 实际上 wasm 是体积小且加载快的二进制格式, 其目标就是充分发挥硬件能力以达到原生执行效率
- 安全: WebAssembly 运行在一个沙箱化的执行环境中, 甚至可以在现有的 JavaScript 虚拟机中实现. 在 web 环境中, WebAssembly 将会严格遵守同源策略以及浏览器安全策略.
- 开放: WebAssembly 设计了一个非常规整的文本格式用来, 调试, 测试, 实验, 优化, 学习, 教学或者编写程序. 可以以这种文本格式在web页面上查看wasm模块的源码.
- 标准: WebAssembly 在 web 中被设计成无版本, 特性可测试, 向后兼容的. WebAssembly 可以被 JavaScript 调用, 进入 JavaScript 上下文, 也可以像 Web API 一样调用浏览器的功能. 当然, WebAssembly 不仅可以运行在浏览器上, 也可以运行在非web环境下.

# AssemblyScript: 为 wasm 发明的编程语言

目前为止, 许多高级语言都能编译到 wasm. 其中最成熟的是 C 语言: 毕竟在设计开发过程中 C 就是 wasm 的第一目标. 但是 C 毕竟对大众不太友好, 因此在 C 之上一门新的语言出现了, 它就是 AssemblyScript, 一门对 TypeScript 做了减法的编程语言.

我们新建一个目录, 进入该目录

```sh
$ npm install --save-dev assemblyscript
$ npx asinit .
```

asinit 命令自动创建建议的目录结构和配置文件, 包括:

- 包含要编译为 WebAssembly 源代码的 ./assembly 目录(一个 index.ts 和 tsconfig.json)
- ./build 目录, 用于放置已编译的 WebAssembly 二进制文件

然后, 打开 ./assembly/index.ts, 其源代码是一个示例的加法函数, 如下

```ts
export function add(a: i32, b: i32): i32 {
  return a + b;
}
```

```sh
$ npm run asbuild
```

运行如上命令将程序编译为 WebAssembly.

使用根目录中的 index.js 实例化和导出 WebAssembly 模块, 您将可以像任何其它模块一样使用它, 其显着区别在于, 模块导出的唯一值是整数和浮点数. 到目前为止, 一切都很好...

# Run on pywasm

```sh
$ vim index.py
```

将以下代码拷贝到 index.py 中, 代码中做了两件事: 载入 wasm 二进制文件, 并调用函数 `add(10, 20)`.

```py
import pywasm


def env_abort(_: pywasm.Ctx):
    return


vm = pywasm.load('./build/optimized.wasm', {
    'env': {
        'abort': env_abort,
    }
})
r = vm.exec('add', [10, 20])
print(r)
```

```sh
$ python3 index.py
# 30
```

Bingo!

另外, 本文代码已发布至 github, 您可以直接克隆代码到本地, 如此, 就不用自己敲代码啦!

```sh
$ git clone https://github.com/mohanson/pywasm_assemblyscript
```
