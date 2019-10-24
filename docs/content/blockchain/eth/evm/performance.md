# EVM 性能测试

简短来说, 重构版 EVM 的综合性能大概是 parity 的 5 倍. 下面是性能测试结果. 其中横坐标表示性能测试用例, 纵坐标表示用例执行时间, 单位是微秒.

测试用例: [https://github.com/ethereum/tests/tree/develop/VMTests/vmPerformance](https://github.com/ethereum/tests/tree/develop/VMTests/vmPerformance)

![img](/img/blockchain/eth/evm/performance/sep1.png)

![img](/img/blockchain/eth/evm/performance/sep2.png)

# 测试步骤

**cita-vm**

```
$ git checkout evmbin
$ cd evmbin && cargo build --release && cd ..
$ ./target/release/evmbin /VMTests/vmPerformance/
```

```no-highlight
vmPerformance/ackermann31.json::ackermann31 97
vmPerformance/ackermann32.json::ackermann32 389
vmPerformance/ackermann33.json::ackermann33 621
vmPerformance/fibonacci10.json::fibonacci10 267
vmPerformance/fibonacci16.json::fibonacci16 2186
vmPerformance/loop-add-10M.json::loop-add-10M 2881404
vmPerformance/loop-divadd-10M.json::loop-divadd-10M 5721593
vmPerformance/loop-divadd-unr100-10M.json::loop-divadd-unr100-10M 4175267
vmPerformance/loop-exp-1b-1M.json::loop-exp-1b-1M 616223
vmPerformance/loop-exp-2b-100k.json::loop-exp-2b-100k 89863
vmPerformance/loop-exp-4b-100k.json::loop-exp-4b-100k 144989
vmPerformance/loop-exp-8b-100k.json::loop-exp-8b-100k 261641
vmPerformance/loop-exp-16b-100k.json::loop-exp-16b-100k 489881
vmPerformance/loop-exp-32b-100k.json::loop-exp-32b-100k 916001
vmPerformance/loop-exp-nop-1M.json::loop-exp-nop-1M 217362
vmPerformance/loop-mul.json::loop-mul 731762
vmPerformance/loop-mulmod-2M.json::loop-mulmod-2M 25718798
vmPerformance/manyFunctions100.json::manyFunctions100 487
```

**parity-ethereum**

```
$ cargo build --release -p evmbin
$ ./target/release/parity-evm stats-jsontests-vm /VMTests/vmPerformance/${filename}
```

```no-highlight
vmPerformance/ackermann31.json::ackermann31 1111
vmPerformance/ackermann32.json::ackermann32 2350
vmPerformance/ackermann33.json::ackermann33 3477
vmPerformance/fibonacci10.json::fibonacci10 1179
vmPerformance/fibonacci16.json::fibonacci16 10644
vmPerformance/loop-add-10M.json::loop-add-10M 16731293
vmPerformance/loop-divadd-10M.json::loop-divadd-10M 25010486
vmPerformance/loop-divadd-unr100-10M.json::loop-divadd-unr100-10M 16092226
vmPerformance/loop-exp-1b-1M.json::loop-exp-1b-1M 1915096
vmPerformance/loop-exp-2b-100k.json::loop-exp-2b-100k 226432
vmPerformance/loop-exp-4b-100k.json::loop-exp-4b-100k 283573
vmPerformance/loop-exp-8b-100k.json::loop-exp-8b-100k 391474
vmPerformance/loop-exp-16b-100k.json::loop-exp-16b-100k 610770
vmPerformance/loop-exp-32b-100k.json::loop-exp-32b-100k 1049655
vmPerformance/loop-exp-nop-1M.json::loop-exp-nop-1M 1174623
vmPerformance/loop-mul.json::loop-mul 3705582
vmPerformance/loop-mulmod-2M.json::loop-mulmod-2M 21589432
vmPerformance/manyFunctions100.json::manyFunctions100 1667
```

**go-ethereum**

需要修改 `tests/vm_test.go` 部分代码, 打印出每个用例的时间, 并关闭调用追踪功能. 修改完成后的代码如下:

```go
package tests

import (
        "testing"
        "time"

        "github.com/ethereum/go-ethereum/core/vm"
)

func TestVM(t *testing.T) {
        t.Parallel()
        vmt := new(testMatcher)
        vmt.slow("^vmPerformance")
        vmt.fails("^vmSystemOperationsTest.json/createNameRegistrator$", "fails without parallel execution")

        vmt.walk(t, vmTestDir, func(t *testing.T, name string, test *VMTest) {
                tic := time.Now()
                vmt.checkFailure(t, name, test.Run(vm.Config{}))
                println(name, time.Since(tic).Nanoseconds() / 1000)
        })
}
```

```
$ cd tests && go test --test.run=TestVM
```

```no-highlight
vmPerformance/ackermann31.json 286
vmPerformance/ackermann32.json 993
vmPerformance/ackermann33.json 1596
vmPerformance/fibonacci10.json 406
vmPerformance/fibonacci16.json 5530
vmPerformance/loop-add-10M.json 8332217
vmPerformance/loop-divadd-10M.json 19945905
vmPerformance/loop-divadd-unr100-10M.json 14968603
vmPerformance/loop-exp-16b-100k.json 6054910
vmPerformance/loop-exp-1b-1M.json 18456493
vmPerformance/loop-exp-2b-100k.json 2026035
vmPerformance/loop-exp-32b-100k.json 11538413
vmPerformance/loop-exp-4b-100k.json 2419685
vmPerformance/loop-exp-8b-100k.json 3096883
vmPerformance/loop-exp-nop-1M.json 640488
vmPerformance/loop-mul.json 2694618
vmPerformance/loop-mulmod-2M.json 4484331
vmPerformance/manyFunctions100.json 1081
```
