# Python/霍夫曼编码

霍夫曼树又称最优二叉树，是一种带权路径长度最短的二叉树. 其广义定义: 给出一组符号(symbol)和其对应的权重值(weight), 其权重通常表示成概率(%), 求一组二元的前置码, 其二元码的长度为最短.

## 机理

一开始，所有的节点都是终端节点(Leaf), 节点内有三个字段:

1. 符号(symbol)
2. 权重(p)
3. 指向父节点的链接(parent)

而非终端节点(Node)内有四个字段:

1. 权重(p)
2. 指向两个子节点的链接(l & r)
3. 指向父节点的链接(parent)

实现霍夫曼树的方式有很多种, 可以使用优先队列简单达成这个过程, 给与权重较低的符号较高的优先级, 算法如下:

1. 把 n 个终端节点(Leaf)加入优先队列, 则 n 个节点都有一个优先权 P
2. 如果队列内的节点数 > 1, 则:
    1. 从队列中移除两个拥有最小 P 的节点
    2. 产生一个新节点, 此节点为被移除节点之父节点, 而此节点的权重值为两节点之权重和
    3. 把 2 产生之节点加入优先队列中
3. 最后在优先队列里的点为树的根节点(root)

## 代码实现

```py
import heapq


class Leaf:
    def __init__(self, p, symbol):
        self.p = p
        self.symbol = symbol
        self.parent = None

    def __lt__(self, other):
        return self.p < other.p


class Node:
    def __init__(self, l=None, r=None):
        self.l = l
        self.r = r
        self.parent = None
        if l:
            l.parent = self
        if r:
            r.parent = self

    def __lt__(self, other):
        return self.p < other.p

    @property
    def p(self):
        p = 0
        if self.l:
            p += self.l.p
        if self.r:
            p += self.r.p
        return p

    # 获取霍夫曼编码表
    def codebook(self):
        data = {}
        for i, entry in enumerate([self.l, self.r]):
            if entry is None:
                continue
            if isinstance(entry, Leaf):
                data[entry.symbol] = str(i)
            else:
                for s, code in entry.codebook().items():
                    data[s] = str(i) + code
        return data


class Tree:

    def __init__(self, items):
        page = []
        for item, p in items:
            heapq.heappush(page, Leaf(p, item))

        for _ in range(len(page) - 1):
            a = heapq.heappop(page)
            b = heapq.heappop(page)
            heapq.heappush(page, Node(a, b))

        self.root = page[0]
        self.codebook = self.root.codebook


if __name__ == '__main__':
    import collections
    tree = Tree(collections.Counter(open(__file__, 'rb').read()).items())
    print(tree.codebook())
    # {99: '000000', 44: '000001', ..., 32: '11'}
```
