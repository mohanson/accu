# JIT: 杂合的艺术

在生活中, 如果有两种合理但不同的方法时, 你应该总是研究两者的结合, 看看能否找到两全其美的方法. 我们称这种组合为杂合(hybrid). 例如, 为什么只吃巧克力或简单的坚果, 而不是将两者结合起来, 成为一块可爱的坚果巧克力呢?

在 1960 年约翰·麦卡锡偶然发现了此方法. 在他的重要论文《符号表达式的递归函数及其在机器上的计算》(Recursive functions of symbolic expressions and their computation by machine, Part I)第一部分中, 他提到了在运行时被转换的函数, 因此不需要编译并执行系统. JIT 编译是两种传统的机器代码翻译方法: 提前编译(AOT)和解释(Interpreter)的结合, 它结合了两者的优点和缺点.

让我们回忆一下第一篇文章的内容, 是关于编写 JIT 所需要的 4 个步骤:

0. 申请一段可写和可执行的内存
0. 将源码翻译为机器码(通常经过汇编)
0. 将机器码写入第一步申请的内存
0. 执行这部分内存

为了在 rust 中编写汇编代码, 一个名为 dynasm-rs 的扩展库将会被使用. dynasm-rs 是对著名 C/C++ 库 dynasm 的模仿, 后者则是 LuaJIT 项目的重要组成部分. dynasm-rs 是一个汇编语言编译器, 它将汇编代码编译为机器码(当然这不是必须的, 你也可以直接在解释器内手写机器码).

首先申请一段内存作为 Brainfuck 解释器的纸带, 并取得该段纸带在内存中的起始地址和终止地址:

```rs
let mut tape: Box<[u8]> = vec![0; 65536].into_boxed_slice();
let tape_addr_from = tape.as_mut_ptr();
let tape_addr_to = unsafe { tape_addr_from.add(tape.len()) };
```

我们将整个 Brainfuck 程序看作一个函数, 它接收两个参数: 纸带起始地址和终止地址. 根据 nasm 规范, 函数的第一个参数被存在 rdi 寄存器中, 第二个参数被存在 rsi 寄存器中. 我们将它们复制到 r12 和 r13 这两个寄存器内持久化存储. 同时 rcx 寄存器被用作为纸带的当前指针 SP, 赋予其初始值为纸带起始地址.

```rs
let mut ops = dynasmrt::x64::Assembler::new()?;
let entry_point = ops.offset();

dynasm!(ops
    ; .arch x64
    ; mov   r12, rdi // arg tape_addr_from
    ; mov   r13, rsi // arg tape_addr_to
    ; mov   rcx, rdi // stack pointer
);
```

编写 sysv64 格式的 getchar/putchar 函数, 使之后的汇编代码中可以调用这两个函数.

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

之后, 将每个 IR 翻译为语义等价的汇编代码如下. 首先 `SHL(x)`, `SHR(x)`, `ADD(x)` 和 `SUB(x)` 4 个操作符最为简单, 它们均只使用一行汇编代码即可完成翻译. 之后是 `PUTCHAR` 与 `GETCHAR`, 它们遵循汇编中函数调用的逻辑, 函数的参数与地址按照规则写入指定寄存器, 然后使用 call 指令调用该函数. 最后是 `JIZ(x)` 与 `JNZ(x)`, 它们负责流程控制, 其对应的汇编代码通过组合使用标签, 比较运算和 jump 指令完成.

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

同时不要忘记为该函数写上 return:

```rs
dynasm!(ops
    ; ret
);
```

最后, 通过**强制类型转换(cast)**将这段内存标记为一个合法的 rust 函数的函数体, 这可以通过 `std::mem::transmute` 函数实现.

```rs
let exec_buffer = ops.finalize().unwrap(); // compile the asm
let fun: extern "sysv64" fn(tape_addr_from: *mut u8, tape_addr_to: *mut u8) =
    unsafe { std::mem::transmute(exec_buffer.ptr(entry_point)) };
fun(tape_addr_from, tape_addr_to);
```

至此, 我们成功将一个 Brainfuck 程序动态编译为一个函数.

# 最后

本文的汇编代码中没有进行包括 I/O, 溢出等方面的错误处理, 这是一项复杂的工程, 并且特意不被加入到代码中以便读者只关心其核心逻辑. 您可以尝试自己去实现.

本文所有代码均放置在 [http://github.com/mohanson/brainfuck](https://github.com/mohanson/brainfuck) 仓库中. 实践是最好的老师, 当然如果你爸爸真的很有钱的话, 买一台更好的电脑也能让此前的解释器跑的很快.

# 参考

- [1] Brainfuck JIT 虚拟机教程, nugine, [https://nugine.github.io/bfjit/introduction.html](https://nugine.github.io/bfjit/introduction.html)
