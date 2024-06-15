# 杂项/2018 年刑侦科推理试题

2018 年江苏网警在微博上公布了一套 2018 年刑侦科目推理试题, 试题如下:

```
1. 这道题的答案是:
A.A    B.B    C.C    D.D

2. 第 5 题的答案是:
A.C    B.D    C.A    D.B

3. 以下选项中哪一题的答案与其他三项不同:
A.第 3 题    B.第 6 题    C.第 2 题    D.第 4 题

4. 以下选项中哪两项的答案相同:
A.第 1,5 题    B. 第 2,7 题    C. 第 1,9 题    D. 第 6,10 题

5. 以下选项中哪一题的答案与本题相同:
A.第 8 题    B. 第 4 题    C. 第 9 题    D. 第 7 题

6. 以下选项中哪两题的答案与第 8 题相同:
A.第 2,4 题    B. 第 1,6 题    C. 第 3,10 题    D. 第 5,9 题

7. 在此十道题中, 被选中次数最少的选项字母为:
A.C    B.B    C.A    D.D

8. 以下选项中哪一题的答案与第一题的答案在字母中不相邻:
A.第 7 题    B. 第 5 题    C. 第 2 题    D. 第 10 题

9. 已知"第 1 题与第 6 题的答案相同"与"第 X 题与第 5 题的答案相同"的真假性相反, 那么 X 为:
A.第 6 题    B. 第 10 题    C. 第 2 题    D. 第 9 题

10. 在此 10 道题中, ABCD 四个字母出现最多与最少者的差为:
A.3    B.2    C.4    D.1
```

在看到这道题的时候我大概想好了要怎么使用计算机去解决. 可惜的是当时人在户外, 卫生纸太小写不下. 第二天回到家, 用时 33 分钟编写了如下程序并搜索到了唯一解. 在计算机的角度来看, 这道题的求解空间是 `4^10` 即 1 兆, 是相当小的一个数字. 约束条件是 10 个, 即 10 道题目. 因此, 只需要遍历 0 到 4^10 并查找满足 10 个约束条件的数字即可. 代码如下:

```go
package main

import (
	"log"
	"slices"
)

func constraint_1(_ [10]uint8) bool {
	return true
}

func constraint_2(v [10]uint8) bool {
	switch v[1] {
	case 0:
		return v[4] == 2
	case 1:
		return v[4] == 3
	case 2:
		return v[4] == 0
	case 3:
		return v[4] == 1
	}
	panic("unreachable")
}

func constraint_3(v [10]uint8) bool {
	switch v[2] {
	case 0:
		return v[2] != v[5] && v[5] == v[1] && v[1] == v[3]
	case 1:
		return v[5] != v[2] && v[2] == v[1] && v[1] == v[3]
	case 2:
		return v[1] != v[2] && v[2] == v[5] && v[5] == v[3]
	case 3:
		return v[3] != v[2] && v[2] == v[5] && v[5] == v[1]
	}
	panic("unreachable")
}

func constraint_4(v [10]uint8) bool {
	switch v[3] {
	case 0:
		return v[0] == v[4]
	case 1:
		return v[1] == v[6]
	case 2:
		return v[0] == v[8]
	case 3:
		return v[5] == v[9]
	}
	panic("unreachable")
}

func constraint_5(v [10]uint8) bool {
	switch v[4] {
	case 0:
		return v[4] == v[7]
	case 1:
		return v[4] == v[3]
	case 2:
		return v[4] == v[8]
	case 3:
		return v[4] == v[6]
	}
	panic("unreachable")
}

func constraint_6(v [10]uint8) bool {
	switch v[5] {
	case 0:
		return v[1] == v[3] && v[3] == v[7]
	case 1:
		return v[0] == v[5] && v[5] == v[7]
	case 2:
		return v[2] == v[9] && v[9] == v[7]
	case 3:
		return v[4] == v[8] && v[8] == v[7]
	}
	panic("unreachable")
}

func constraint_7(v [10]uint8) bool {
	c := [4]uint8{}
	for _, e := range v {
		c[e] += 1
	}
	switch v[6] {
	case 0:
		return c[2] < c[0] && c[2] < c[1] && c[2] < c[3]
	case 1:
		return c[1] < c[0] && c[1] < c[2] && c[1] < c[3]
	case 2:
		return c[0] < c[1] && c[0] < c[2] && c[0] < c[3]
	case 3:
		return c[3] < c[0] && c[3] < c[1] && c[3] < c[2]
	}
	panic("unreachable")
}

func constraint_8(v [10]uint8) bool {
	switch v[7] {
	case 0:
		return v[6]-v[0] != 1 && v[6]-v[0] != 255
	case 1:
		return v[4]-v[0] != 1 && v[4]-v[0] != 255
	case 2:
		return v[1]-v[0] != 1 && v[1]-v[0] != 255
	case 3:
		return v[9]-v[0] != 1 && v[9]-v[0] != 255
	}
	panic("unreachable")
}

func constraint_9(v [10]uint8) bool {
	switch v[8] {
	case 0:
		a := v[0] == v[5]
		b := v[5] == v[4]
		return a == !b
	case 1:
		a := v[0] == v[5]
		b := v[9] == v[4]
		return a == !b
	case 2:
		a := v[0] == v[5]
		b := v[1] == v[4]
		return a == !b
	case 3:
		a := v[0] == v[5]
		b := v[8] == v[4]
		return a == !b
	}
	panic("unreachable")
}

func constraint_a(v [10]uint8) bool {
	c := [4]uint8{}
	for _, e := range v {
		c[e] += 1
	}
	switch v[9] {
	case 0:
		return slices.Max(c[:])-slices.Min(c[:]) == 3
	case 1:
		return slices.Max(c[:])-slices.Min(c[:]) == 2
	case 2:
		return slices.Max(c[:])-slices.Min(c[:]) == 4
	case 3:
		return slices.Max(c[:])-slices.Min(c[:]) == 1
	}
	panic("unreachable")
}

func main() {
	v := [10]uint8{}
	for i := 0; i < 1048576; i++ {
		for j := 0; j < 10; j++ {
			v[j] = uint8((i >> (j * 2)) & 3)
		}
		if !constraint_1(v) {
			continue
		}
		if !constraint_2(v) {
			continue
		}
		if !constraint_3(v) {
			continue
		}
		if !constraint_4(v) {
			continue
		}
		if !constraint_5(v) {
			continue
		}
		if !constraint_6(v) {
			continue
		}
		if !constraint_7(v) {
			continue
		}
		if !constraint_8(v) {
			continue
		}
		if !constraint_9(v) {
			continue
		}
		if !constraint_a(v) {
			continue
		}
		log.Println(v)
	}
}
```

计算得到答案是 `BCACA CDABA`.
