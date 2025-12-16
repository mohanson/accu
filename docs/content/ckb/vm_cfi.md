# CKB/CKB-VM 扩展指令集 CFI

在 RISC-V 架构中, 函数调用机制依赖于 ra(return address) 寄存器来保存返回地址. 当执行函数跳转时, 处理器会将返回地址写入 ra 寄存器. 对于嵌套函数调用的场景, 由于 ra 寄存器只有一个, 因此当前 ra 中的返回地址必须被保存到栈上, 以便后续恢复.

这种设计引入了一个关键的安全风险: 如果攻击者能够通过某种手段(如缓冲区溢出漏洞)破坏栈里的内容, 就可以篡改保存在栈上的返回地址. 这正是 [ROP(Return-Oriented Programming)](https://en.wikipedia.org/wiki/Return-oriented_programming) 或 JOP 攻击的核心原理. 攻击者通过精心构造的 gadgets(代码片段) 链, 劫持程序的控制流, 从而实现任意代码执行.

在 CKB 智能合约的场景下, 这种攻击的威胁尤为显著. 攻击者甚至不需要构造复杂的 ROP 链, 只需将返回地址指向 `syscall exit` 并设置退出码为 0, 即可绕过合约的安全检查, 使验证逻辑失效. 这种攻击方式简单却极具破坏性.

因此, 对栈的保护机制, 尤其是返回地址的完整性验证, 对于保障 CKB-VM 的安全性至关重要. 这也是引入 CFI(Control Flow Integrity) 扩展指令的根本动机.

## 典型的 ROP 攻击链路

下面是一个典型的 ROP 攻击链路示例:

```c
#include <stdint.h>

#include "ckb_syscalls.h"

// 我们想要劫持控制流, 通过 ROP 直接跳转到这里. 这个函数会直接调用 ckb_exit(0), 在 CKB-VM 环境中表示脚本验证通过.
void fun_rop_gadget_return_zero() {
    ckb_exit(0);
}

// 这是包含漏洞的函数. 我们在该函数里直接修改栈上保存的返回地址. 在实际场景中, 这个漏洞可能是由于缓冲区溢出, 野指针,
// use-after-free 等原因引起的.
void fun_vulner() {
    // 获取 fun_rop_gadget_return_zero 的地址.
    uint64_t gadget_addr = (uint64_t)&fun_rop_gadget_return_zero;
    // 获取当前栈指针
    register uint64_t sp_val;
    asm volatile("mv %0, sp" : "=r"(sp_val));
    // 在 -O0 编译下, 通过反汇编可以看到:
    //   12bd8:  addi sp,sp,-48
    //   12bda:  sd   ra,40(sp)
    // 所以我们需要修改 sp+40 位置的值.
    uint64_t *return_addr_ptr = (uint64_t*)(sp_val + 40);
    *return_addr_ptr = gadget_addr;
    // 当这个函数执行 ret 指令时, 它会从栈上加载返回地址.
    // 由于我们已经修改了栈上的返回地址, 因此它会跳转到 fun_rop_gadget_return_zero 函数.
    return;
}

int main() {
    fun_vulner();
    return 1;
}
```

```sh
$ riscv64-unknown-elf-gcc -O0 -nostdinc -nostdlib -nostartfiles -I ckb-c-stdlib -I ckb-c-stdlib/libc -g -o main main.c
$ ckb-debugger --bin main

# Run result: 0
# All cycles: 3460(3.4K)
# Exit code: 0
```

## 真实的 ROP 攻击示例

接上面的演示例子, 我们改进下 fun_vulner 函数, 使其更贴近真实的 ROP 攻击场景. 具体来说, 我们让 fun_vulner 接收一个用户输入的缓冲区, 并将其复制到栈上的本地缓冲区中. 由于没有边界检查, 攻击者可以构造恶意输入来覆盖栈上的返回地址. 这是一个典型的缓冲区溢出漏洞利用场景.

```c
#include <stdint.h>

#include "ckb_syscalls.h"

// 我们想要劫持控制流, 通过 ROP 直接跳转到这里. 这个函数会直接调用 ckb_exit(0), 在 CKB-VM 环境中表示脚本验证通过.
void fun_rop_gadget_return_zero() {
    ckb_exit(0);
}

// 这是包含漏洞的函数. 它接收用户输入并复制到栈上的缓冲区中, 但没有进行边界检查.
// 这会导致缓冲区溢出, 攻击者可以覆盖栈上保存的返回地址.
void fun_vulner(const uint64_t *input) {
    // 在栈上分配一个 64 字节的缓冲区
    uint64_t buffer[8];
    // 危险: 没有边界检查的复制操作
    // 这里复制了 10 个 uint64_t, 超出了 buffer 的大小, 造成缓冲区溢出.
    buffer[0] = input[0];
    buffer[1] = input[1];
    buffer[2] = input[2];
    buffer[3] = input[3];
    buffer[4] = input[4];
    buffer[5] = input[5];
    buffer[6] = input[6];
    buffer[7] = input[7];
    buffer[8] = input[8]; // 溢出! 覆盖栈上的 saved s0
    buffer[9] = input[9]; // 溢出! 覆盖栈上的 saved ra (返回地址)
}

int main() {
    // 构造恶意输入来进行 ROP 攻击. 输入数据可能来自用户定义的 witness args 或者 lock args.
    uint64_t malicious_input[10];

    // 通过反汇编可以看到 fun_vulner 的栈布局:
    // - 栈帧大小       : 112 字节 (sp-112)
    // - buffer[64] 位置: s0-72 到 s0-8, 其中 s0 = sp + 112
    // - buffer         : 实际在 sp + 40 到 sp + 104
    // - saved s0 在 sp + 96
    // - saved ra 在 sp + 104
    // 填充前 64 字节的缓冲区 (8 个 uint64_t)
    malicious_input[0] = 0x4141414141414141ULL;
    malicious_input[1] = 0x4242424242424242ULL;
    malicious_input[2] = 0x4343434343434343ULL;
    malicious_input[3] = 0x4444444444444444ULL;
    malicious_input[4] = 0x4545454545454545ULL;
    malicious_input[5] = 0x4646464646464646ULL;
    malicious_input[6] = 0x4747474747474747ULL;
    malicious_input[7] = 0x4848484848484848ULL;

    // 第 64-72 字节: 覆盖 saved s0 (填充数据)
    malicious_input[8] = 0x5050505050505050ULL;
    // 第 72-80 字节: 覆盖 saved ra (这是 ROP 攻击的关键) !
    malicious_input[9] = (uint64_t)&fun_rop_gadget_return_zero;

    fun_vulner(malicious_input);
    return 1;
}
```

```sh
$ riscv64-unknown-elf-gcc -O0 -nostdinc -nostdlib -nostartfiles -I ckb-c-stdlib -I ckb-c-stdlib/libc -g -o main main.c
$ ckb-debugger --bin main

# Run result: 0
# All cycles: 3460(3.4K)
# Exit code: 0
```

## 尝试对 ROP 攻击进行防护

看了上面的 ROP 攻击示例, 我们可以总结出攻击的关键点在于: 攻击者能够覆盖栈上保存的返回地址. 因此, 保护栈上返回地址的完整性是防御该攻击的核心.

我们可以尝试通过在函数入口和出口添加栈保护代码来防护该攻击. 具体来说, 在函数入口保存栈指针, 在函数返回前验证栈指针是否被篡改. 如果发现栈指针异常, 则强行终止程序.

**这就是 CFI 扩展指令集的核心思想.** 两点:

- 前向保护: 程序不能随意跳转到别的位置, 必须跳转到合法的目标.
- 后向保护: 函数返回时, 必须确保返回地址没有被篡改.

> 在上面的例子里, 程序从 fun_vulner 函数跳转到 fun_rop_gadget_return_zero 就是不合法的跳转. 我们希望通过一些机制来阻止这种非法跳转. 同时在执行 fun_vulner 函数开始和返回之前, 我们需要有机制确保其函数返回地址未被修改.

## CFI 扩展简介

[RISC-V CFI specification](https://github.com/riscv/riscv-cfi) 已经正式合并至 [RISC-V Instruction Set Manual](https://github.com/riscv/riscv-isa-manual), 规范内容分为以下两个部分:
- [Privileged ISA](https://github.com/riscv/riscv-isa-manual/blob/main/src/priv-cfi.adoc): 特权级指令集架构, 定义了操作系统和虚拟机监控器层面的 CFI 支持
- [Unprivileged ISA](https://github.com/riscv/riscv-isa-manual/blob/main/src/unpriv-cfi.adoc): 非特权级指令集架构, 定义了应用程序层面的 CFI 指令.

从 Specification 的成熟度来看, CFI 扩展规范已经进入稳定阶段. 对于 CKB-VM 而言, 核心关注点在 Unprivileged ISA 部分, 该部分引入了以下5条新指令:

- `LPAD`(Landing Pad): 标记合法的间接跳转目标位置, 用于 forward-edge 保护
- `SSPUSH`(Shadow Stack Push): 将返回地址压入 shadow stack
- `SSPOPCHK`(Shadow Stack Pop and Check): 从 shadow stack 弹出返回地址并验证其完整性
- `SSRDP`(Shadow Stack Read Pointer): 读取 shadow stack 指针
- `SSAMOSWAP`(Shadow Stack Atomic Swap): 原子地交换 shadow stack 上的值

这些指令的核心机制是 Shadow Stack(影子栈): 除了常规的程序栈外, 硬件维护一个独立的影子栈专门用于存储返回地址. 当函数调用发生时, 返回地址会同时保存在常规栈和影子栈上; 函数返回时, 硬件会验证两个栈上的返回地址是否一致. 由于影子栈对普通内存访问指令不可见, 攻击者即使能够破坏常规栈, 也无法同步篡改影子栈, 从而实现了返回地址的完整性保护.

## CFI 扩展: 前向保护

`LPAD`(Landing Pad) 指令用于标记合法的间接跳转目标位置, 实现控制流的前向保护.

1. 当编译器生成间接跳转指令(如 `jr`, `jalr`) 时, 目标地址必须指向一个 `LPAD` 指令.
2. CKB-VM 会检查间接跳转的目标地址是否对应一个 `LPAD` 指令.
3. 如果目标地址不是 `LPAD`, 则触发控制流异常, 终止程序执行.

通常在调用虚函数, 或者通过函数指针调用函数时, 会使用间接跳转指令. 通过在合法的函数入口处插入 `LPAD` 指令, 可以确保程序只能跳转到预定义的合法位置, 防止攻击者通过篡改函数指针或返回地址来跳转到非法代码位置.

**示例**

```c
// 通过函数指针调用函数.
typedef int (*func_ptr)(int);

int add(int a, int b) {
    // 编译器会在 add 函数入口处插入 lpad 指令.
    return a + b;
}

int main() {
    func_ptr fp = &add;
    // 当执行 jalr 跳转到 fp 时, CKB-VM 验证目标地址是否为 lpad.
    int result = fp(5, 3);
    return result;
}
```

前向保护只在间接跳转时生效, 对于直接跳转(如普通的函数调用和返回)不进行限制. 这是因为直接跳转的目标地址在编译时已经确定, 不易被攻击者篡改.

## CFI 扩展: 后向保护

后向保护通过影子栈(Shadow Stack)机制实现, 主要依赖 `SSPUSH` 和 `SSPOPCHK` 指令来保护函数返回地址的完整性. Shadow Stack 是由硬件维护的独立栈结构, 专门用于存储返回地址. 与普通程序栈不同, Shadow Stack 对常规内存访问指令(如 `lw`, `sw`)不可见, 只能通过专用的 CFI 指令访问. 这种设计确保了即使攻击者能够破坏常规栈, 也无法篡改 Shadow Stack 上的返回地址.

**函数调用时**

1. 在函数调用时(执行 `call` 或 `jalr` 指令后), 编译器会插入 `SSPUSH` 指令.
2. 该指令将返回地址写入 Shadow Stack 的栈顶, 并自动递增 Shadow Stack 指针.
3. 返回地址同时存储在常规栈和 Shadow Stack 中.

**函数返回时**

1. 在函数返回时(执行 `ret` 或 `jr ra` 指令前), 编译器会插入 `SSPOPCHK` 指令.
2. 该指令从 Shadow Stack 栈顶弹出预期的返回地址, 并自动递减 Shadow Stack 指针.
3. 硬件比较 Shadow Stack 中的返回地址与常规栈中的返回地址.
4. 如果两者不匹配, 则触发控制流异常, 终止程序执行.
5. 若一致, 允许函数正常返回.

**示例**

```c
#include <stdint.h>

int add(int a, int b) {
    // 编译器插入 sspush ra.
    int result = a + b;
    // 编译器插入 sspopchk ra, 验证返回地址完整性
    return result;
}

int main() {
    int result = add(5, 3);
    return result;
}
```

## 工具链的现状

截至 2025/12/15 日, LLVM 对 RISC-V CFI 扩展指令的支持, 目前正处于开发阶段. 考虑到 CFI 规范已正式纳入 RISC-V 指令集手册, 预计工具链的支持将在不久的将来完善.

在 LLVM 21 中，通过以下命令行可以开启试验性质的开关：

```sh
--target=riscv64
-march=rv64imc_zba_zbb_zbc_zbs_zicfiss1p0_zicfilp1p0
-menable-experimental-extensions
-fcf-protection=full
-mcf-branch-label-scheme=func-sig
```

在 Rust 最新的 nightly 版本中, 由于 rustc 基于 LLVM 21 构建, 因此也可以通过类似的方式启用 CFI 支持. 具体来说, 可以使用如下的环境变量配置:

```sh
RUSTFLAGS=-C target-feature=+experimental-zicfiss,+experimental-zicfilp
```

但是需要注意, 目前 Rust 对 CFI 的支持还不完善, 编译结果会生成 LPAD 指令, 但尚未在函数调用和返回处插入 SSPUSH 和 SSPOPCHK 指令.
