# Go/Cgo

使用 Cgo 可允许 Go 调用 C 代码. 编写某些具有特殊标志的 Go 代码, Cgo 将把 Go 代码与 C 代码合并编译并打包至单个 Go 包/可执行文件中.

让我们从下面这个例子开始, 这个例子使用 C 中的 puts 函数在标准输出中打印了 "Hello World!":

```go
package main

/*
#include <stdio.h>
#include <stdlib.h>
*/
import "C"
import "unsafe"

func main() {
	message := C.CString("Hello World!\n")
	defer C.free(unsafe.Pointer(message)) // free 函数定义在 stdlib.h 内
	C.puts(message) // puts 函数定义在 stdio.h 内
}
```

分析一下在上面的代码中我们做了什么: 我们首先 `import "C"`, 并且在这句话之前加了一段注释 `#include <stdio.h>...`, 之后在 `main` 函数内使用 `C.puts()` 等函数完成了我们的功能. Go 中并没有一个名字叫 `C` 的包, 是因为 `C` 是一个"伪包": 一个由 Cgo 解释的特殊命名空间. Cgo 会检测 `import "C"` 之前的注释, 并将它们作为 C 语法对待. 事实上, 注释内可以包含任意 C 代码, 比如在注释中定义一个 C 函数:

```go
package main

/*
#include <stdio.h>
#include <stdlib.h>

static void cprintf(const char* msg) {
    printf(msg);
}
*/
import "C"
import "unsafe"

func main() {
	message := C.CString("Hello World!\n")
	defer C.free(unsafe.Pointer(message))
	C.cprintf(message)
}
```

## 链接旧有的 C 代码

C 语言是一座巨大且古老的宝藏. 目前为止, 它仍然是世界上功能最强, 性能最好的语言. C 语言在机器学习, 音视频处理等领域具有不可置疑的领导地位, 许多名库均经过了全球无数开发者数年至数十年的持续开发和优化. 大致上来说, 相比使用别的语言比如 Go 或 Rust 重新实现一遍轮子, 复用这些 C 代码显得更有意义.

我们将使用一个简单的 C 包作为例子, 讲述如何在 Go 中复用 C 代码. 非常幸运, 我找到了一个及其简单的 C 库, 这个库只有两个文件: `foo.h` 与 `foo.c`:

```c
// foo.c
#include "foo.h"

void foo() {
    printf("I am foo!\n");
}
```

```c
// foo.h
#include <stdio.h>

void foo();
```

要在 Go 中使用这个 C 库, 我们需要新建一个 `foo.go` 文件, 并在文件中键入以下内容:

```go
// foo.go
package main

// #cgo LDFLAGS: -L ./ -lfoo
// #include "foo.h"
import "C"

func main() {
	C.foo()
}
```

万事俱备! 现在打开命令行, 键入以下内容:

```sh
$ gcc -c foo.c              # 生成 foo.o
$ ar rv libfoo.a foo.o      # 生成 libfoo.a
$ go build foo.go           # 生成 foo 可执行文件
$ ./foo                     # 执行可执行文件, 输出 I am foo!
```

## 代码下载

这篇文章中使用的代码均可于 [https://github.com/mohanson/cgo_example](https://github.com/mohanson/cgo_example) 下载. 该项目中还包括如何在 Go 中调用 C++ 代码的例子, 可作为本章的补充.

如果你对更加复杂 Cgo 项目感兴趣, 可以参考 [https://github.com/mohanson/FaceDetectionServer](https://github.com/mohanson/FaceDetectionServer),  该项目使用 Go 进行人脸识别, 而人脸识别源码是纯 C++ 编写的, 中间使用 Cgo 作为胶水.

## 参考

- [1] [Go. C? Go? Cgo!](https://blog.golang.org/c-go-cgo)
