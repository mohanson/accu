# JIT: 折中的艺术

JIT 编译是两种传统的机器代码翻译方法: 提前编译(AOT)和解释(Interpreter)的结合, 它结合了两者的优点和缺点(实际上更多它是解释执行的语言最后为了性能妥协的产物, 除了在一些特定用途的场景下, 比如模拟器的动态重编译技术, JIT 大部分情况下不如直接的编译器来的高效和快乐).

让我们回忆一下第一篇文章的内容, 是关于编写 JIT 所需要的 4 个步骤:

0. 申请一段可写和可执行的内存
0. 将源码翻译为汇编
0. 将汇编写入第一步申请的内存
0. 执行这部分内存

为了在 rust 中编写汇编代码, 一个名为 dynasm-rs 的扩展库会被我使用. dynasm-rs 是对 C/C++ 库 dynasm 的模仿, 后者则是 LuaJIT 项目的重要组成部分. dynasm 是一个汇编语言编译器, 它将汇编代码编译为机器码. 当然这不是必须的, 你也可以直接手写机器码.

首先申请一段内存作为 Brainfuck 解释器的栈(注: 它不是被用来保存机器码的可执行内存), 并取得该段内存的起始地址和终止地址:

```rs
let mut memory: Box<[u8]> = vec![0; 65536].into_boxed_slice();
let memory_addr_from = memory.as_mut_ptr();
let memory_addr_to = unsafe { memory_addr_from.add(memory.len()) };
```

我们将整个 Brainfuck 程序看作一个函数, 它接收两个参数: 内存起始地址和终止地址. 根据 nasm 规范, 函数的第一个参数被存在 rdi 寄存器中, 第二个参数被存在 rsi 寄存器中. 将它们复制到 r12 和 r13 这两个寄存器内持旧化存储. 同时 rcx 寄存器被作为栈指针对待, 它的初始值是内存起始地址.

```rs
let mut ops = dynasmrt::x64::Assembler::new()?;
let entry_point = ops.offset();

dynasm!(ops
    ; .arch x64
    ; mov   r12, rdi // arg memory_addr_from
    ; mov   r13, rsi // arg memory_addr_to
    ; mov   rcx, rdi // stack pointer
);
```

编写 sysv64 格式的 getchar/putchar 函数, 为了之后的汇编代码中可以直接调用这两个函数而不报错:

```rs
unsafe extern "sysv64" fn putchar(char: *mut u8) {
    std::io::stdout()
        .write_all(std::slice::from_raw_parts(char, 1))
        .unwrap();
}

unsafe extern "sysv64" fn getchar(char: *mut u8) {
    std::io::stdout().flush().unwrap();
    std::io::stdin()
        .read_exact(std::slice::from_raw_parts_mut(char, 1))
        .unwrap();
}
```

将每个 IR 翻译为语义等价的汇编代码如下. 首先 `SHL(x)`, `SHR(x)`, `ADD(x)` 和 `SUB(x)` 4 个操作符最为简单, 它们均只使用一行汇编代码即可完成翻译. 之后是 `PUTCHAR` 与 `GETCHAR`, 它们遵循汇编中函数调用的逻辑, 函数的参数与地址按照规则写入指定寄存器, 然后使用 call 指令调用该函数. 最后是 `JIZ(x)` 与 `JNZ(x)`, 它们负责流程控制, 其对应的汇编代码通过组合使用标签, 比较运算和 jump 指令完成.

```rs
for ir in code.instrs {
    match ir {
        ir::IR::SHL(x) => dynasm!(ops
            ; sub rcx, x as i32 // sp -= x
        ),
        ir::IR::SHR(x) => dynasm!(ops
            ; add rcx, x as i32 // sp += x
        ),
        ir::IR::ADD(x) => dynasm!(ops
            ; add BYTE [rcx], x as i8 // *sp += x
        ),
        ir::IR::SUB(x) => dynasm!(ops
            ; sub BYTE [rcx], x as i8 // *sp -= x
        ),
        ir::IR::PUTCHAR => dynasm!(ops
            ; mov  r15, rcx
            ; mov  rdi, rcx
            ; mov  rax, QWORD putchar as _
            ; sub  rsp, BYTE 0x28
            ; call rax
            ; add  rsp, BYTE 0x28
            ; mov  rcx, r15
        ),
        ir::IR::GETCHAR => dynasm!(ops
            ; mov  r15, rcx
            ; mov  rdi, rcx
            ; mov  rax, QWORD getchar as _
            ; sub  rsp, BYTE 0x28
            ; call rax
            ; add  rsp, BYTE 0x28
            ; mov  rcx, r15
        ),
        ir::IR::JIZ(_) => {
            let l = ops.new_dynamic_label();
            let r = ops.new_dynamic_label();
            loops.push((l, r));
            dynasm!(ops
                ; cmp BYTE [rcx], 0
                ; jz => r
                ; => l
            )
        }
        ir::IR::JNZ(_) => {
            let (l, r) = loops.pop().unwrap();
            dynasm!(ops
                ; cmp BYTE [rcx], 0
                ; jnz => l
                ; => r
            )
        }
    }
}
```

别忘记为这个函数写上 return:

```rs
dynasm!(ops
    ; ret
);
```

最后, 将这段内存标记为一个合法的 rust 函数, 通过 `std::mem::transmute` 实现. 该函数可以被直接调用, 其作用等价于解释执行的 brainfuck 源代码.

```rs
let exec_buffer = ops.finalize().unwrap(); // compile the asm
let fun: extern "sysv64" fn(memory_addr_from: *mut u8, memory_addr_to: *mut u8) =
    unsafe { std::mem::transmute(exec_buffer.ptr(entry_point)) };
fun(memory_addr_from, memory_addr_to);
```

# 结语

麻雀虽小五脏俱全. 这是一个相当初级的项目, 但也包含了解释器, IR 优化与 JIT 编译三大部分. 对 JIT 汇编代码的细节本文完全没有介绍, 这需要您自己去学习, RTFD.

同时本文的汇编代码中没有进行包括 I/O, 溢出等方面的错误处理, 这是一项复杂的工程, 并且特意不被加入到代码中以便读者只关心其核心逻辑.

本文所有代码均放置在 [http://github.com/mohanson/brainfuck](https://github.com/mohanson/brainfuck) 仓库中.

# 参考

- [1] Brainfuck JIT 虚拟机教程, nugine, [https://nugine.github.io/bfjit/introduction.html](https://nugine.github.io/bfjit/introduction.html)
