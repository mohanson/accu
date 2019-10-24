该系列文章很早就准备写了, 但是一直拖着... 故事的起因是我在 windows 下 `rm -rf` 了自己的用户目录, 因此在该起事件后就研究起来如何 `rm` 的时候把文件放入回收站而不是直接删除, windows 提供了 C++ 版本的 api 来实现这一需求, 但作为一个懒人我并不想玩 C++, 所以, Python 大法好~

# Python windows 编程: 概览

在 windows 平台下, python 通过 `ctypes` 可以很容易的与 windows api 进行交互. 如下的代码将在桌面创建一个 `MessageBoxW`, 并在通知的内容中显示当前时间.

```py
import ctypes
import datetime

c = datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')
ctypes.windll.user32.MessageBoxW(0, c, '查询时间', 1)
```

![img](/img/py/ctypes/overview/messagebox.png)

`MessageBoxW` 的 C++ 接口文档位于 [https://msdn.microsoft.com/en-us/library/windows/desktop/ms645505(v=vs.85).aspx](https://msdn.microsoft.com/en-us/library/windows/desktop/ms645505(v=vs.85).aspx), 如文档所见, 我们可以很方便的修改包括标题, 正文, 按钮和 icon 等在内的几乎所有内容. 与上述 Python 代码等效的 C++ 代码如下所示:

```c++
#include <windows.h>
#pragma comment (lib, "User32.lib")

int WinMain(
    HINSTANCE hInstance,
    HINSTANCE hPrevInstance,
    LPSTR lpCmdLine,
    int nCmdShow
){
    MessageBoxW(NULL, (LPCWSTR)L"2018-05-20 10:22:38", (LPCWSTR)L"查询时间", MB_OKCANCEL);
    return 0;
}
```
