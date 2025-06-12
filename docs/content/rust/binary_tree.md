# Rust 零基础入门/二叉树

在之前的课程中, 我们了解了所有权, 借用检查, 生命周期等概念是如何使 Rust 变得安全和高效的, 但正如一句俗语所说: "Every coin has two sides", 每个硬币都有两面, Rust 的这些设计也会给开发者带来一些困扰. 我先讲一个小故事: Max Howell 是一个著名的 macOS/IOS 开发工程师, 在 2015 年 6 月 10 日的时候, 他发布了一条推特, 他去面试了谷歌, 但谷歌的人让他滚动, 因为他不会在白板上翻转二叉树, 虽然谷歌内部 90% 的工程师都在用他写的软件.

这在当时引发了巨大的讨论, 我们先暂时不管这个事情的结果. 如果你曾今刷过题的话, 比如 leetcode, 那应该很容易回忆起来一些关于链表或二叉树的题目. 翻转二叉树一定是所有题目中经典中的经典. 很多人都和我抱怨过在 Rust 中实现数据结构有多么不容易, 我认为这是相当合理的吐槽, 一切都是那该死的安全性检查. 但是为了让你出去面试的时候不至于被拒绝, 所以, 我们今天来实现如何在 Rust 中翻转二叉树吧(提示: 这很不容易).

## 什么是二叉树

在计算机科学中, 二叉树是每个节点最多只有两个分支(即不存在分支度大于 2 的节点)的树结构. 通常分支被称作"左子树"或"右子树". 二叉树的分支具有左右次序, 不能随意颠倒. 你可以直接看下面这张图片, 这很容易理解. 二叉树的常见用处是作为高效搜索和高效排序.

> 有张图

## 在 Rust 中实现

如果按照过去语言的思路我们似乎应该可以这么写:

```rs
struct Node<T> {
    value: T,
    left: Node<T>,
    right: Node<T>,
}
```

这样的写法在大多数语言中都是行的通的, 包括 Golang 和 Python, 这是老师另外常用的两门语言. 我们去尝试编译这段代码, 得到了编译报错, 但事实上我一点也不意外. 我们阅读报错信息, 发现它说我们递归使用了类型导致类型拥有无限的大小.

```text
 --> src/main.rs:1:1
  |
1 | struct Node {
  | ^^^^^^^^^^^ recursive type has infinite size
2 |     Left: Node,
  |     ---------- recursive without indirection
3 |     Right: Node,
  |     ----------- recursive without indirection
  |
  = help: insert indirection (e.g., a `Box`, `Rc`, or `&`) at some point to make `Node` representable
```

编译器拒绝我们的理由很合理, 如果你仔细思考上述的 Node 结构体在内存中如何表示, 确实会发现它是一个无限递归的结构.

我认为问题的根源在于 Node 节点拥有左子树和右子树的所有权. 换句话说, 如果左子树和右子树只是一个引用类型, 就不会存在无限大小的结构体了. 那么, 谁拥有左子树和右子树?

# Rc

我们引入一个新的工具, 叫做引用计数的智能指针, Rc. 我将把子树的所有权交给 Rc. Rc 是一个很有用的工具, 它通常用来处理单个值拥有多个所有者的情况. 每当这个值拥有一个所有者, 那它的引用计数加 1. 当它的引用计数变为 0 时, 则内存被回收.

你可以想象一下, 将 Rc 作为房间中的电视. 当一个人进入房间看电视时, 他会打开电视. 其他人随后也可以进入房间看电视, 当最后一个人离开房间时, 由于不再使用电视, 他将选择关闭电视.

在此时, 我们不会使用 Rc 的多所有者功能, 仅仅是让 Rc 拥有子树. 所以, 修改代码如下:

```rs
use std::rc::Rc;

struct Node<T> {
    value: T,
    left: Rc<Node<T>>,
    right: Rc<Node<T>>,
}
```

太棒了, 编译通过了!

# Option

我迫不及待的开始想初始化一个 Node 了, 但是, 等等, 我为了初始化 Node, 必须先有左子树和右子树, 而子树也是 Node 类型, 我们似乎卡住了.

有办法在初始化 Node 的时候先不写入左子树和右子树, 让它们保持为空, 等初始化完成后再去修改相关字段吗? 而且, 如果我们考虑到二叉树最后的叶子节点, 它不拥有左子树和右子树, 所以对于叶子节点来说这两个字段都是空的.

为此我们引入一个新的工具, 叫做 Option. Option 是 Rust 中最常用最重要的类型, 它的语义是这个类型的变量可能为 None. None 不是空指针, 是一个类型, 语义为空. 很多语言都有类似的概念, 但在 Rust 中有一些细微的区别. 我不想太过详细的解释这件事情, 让我们保持专注.

改下我们的代码, 让它成为:

```rs
use std::rc::Rc;

struct Node<T> {
    value: T,
    left: Option<Rc<Node<T>>>,
    right: Option<Rc<Node<T>>>,
}

fn main() {
    let mut root = Node::<u32>{value: 0, left: None, right: None};
    let left = Node::<u32>{value: 1, left: None, right: None};
    let right = Node::<u32>{value: 2, left: None, right: None};
    root.left = Some(Rc::new(left));
    root.right = Some(Rc::new(right));

    println!("{:?}", root.value);
    println!("{:?}", root.left.unwrap().value);
    println!("{:?}", root.right.unwrap().value);
}
```

## RefCell

还差最后一步! 为了翻转二叉树, 我们需要修改树中的值. 你可能已经注意到, Rust 默认情况下所有变量都是不可变的, 即使这个变量在 Rc 内部也是一样.

不过我们还是会实际测试一下, 确保你对此印象深刻:

```rs
root.left.unwrap().value = 4;
```

你会得到一个编译报错.

我很确信这是我最后一次说这句话: 为了解决这个问题, 我们要引入一个新的工具, 叫做 RefCell. 它表示内部可变性. 内部可变性是 Rust 中的一种设计模式, 即使对数据有不可变的引用, 它也允许您对数据进行改变. RefCell 经常被用在 Rc 内部, 就像这样:

```rs
use std::rc::Rc;
use std::cell::RefCell;

struct Node<T> {
    value: T,
    left: Option<Rc<RefCell<Node<T>>>>,
    right: Option<Rc<RefCell<Node<T>>>>,
}

fn main() {
    let mut root = Node::<u32>{value: 0, left: None, right: None};
    let left = Node::<u32>{value: 1, left: None, right: None};
    let right = Node::<u32>{value: 2, left: None, right: None};
    root.left = Some(Rc::new(RefCell::new(left)));
    root.right = Some(Rc::new(RefCell::new(right)));

    println!("{:?}", root.value);
    if let Some(ref x) = root.left {
        println!("{:?}", x.borrow().value);
    }
    if let Some(ref x) = root.right {
        println!("{:?}", x.borrow().value);
    }

    if let Some(ref mut x) = root.left {
        x.borrow_mut().value = 4;
    }
    if let Some(ref x) = root.left {
        println!("{:?}", x.borrow().value);
    }
}
```

最后我布置一个作业, 请继续我的代码, 完成翻转二叉树的功能. 我认为这是对于 Rust 初学者很好的一个毕业测试. 要理解 Rc, RefCell, Option 等概念会花上你不少时间, 因为这真的很难.
