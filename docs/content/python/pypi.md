# Python/Pypi

我将在这篇文章中介绍如何将一个 Python package 发布到 Pypi. 尽量让步骤简洁, 以便任何人都可以在 3 分钟之内阅读完成.

官方教程: [https://packaging.python.org/tutorials/distributing-packages/](https://packaging.python.org/tutorials/distributing-packages/)

示例项目: [https://github.com/pypa/sampleproject](https://github.com/pypa/sampleproject)

## 配置账号

首先在 $HOME 下写入以下内容至 `.pypirc`:

```ini
[pypi]
username = __token__
password = pypi-xxxx
```

注意, 目前 pypi 已经不允许使用用户名和密码进行包的发布, 只允许使用 API Token. 要获得 API Token, 请访问: [https://pypi.org/manage/account/](https://pypi.org/manage/account/)

## 创建 pyproject.toml

在待发布的项目中创建 `pyproject.toml` 文件, 并写入以下模板内容:

```py
[build-system]
requires = ["setuptools"]
build-backend = "setuptools.build_meta"

[project]
name = "sample"
version = "1.2.0"
authors = [
  { name="The Python Packaging Authority", email="pypa-dev@googlegroups.com" },
]
description = "A sample Python project"
readme = "README.md"
license = { file = "LICENSE" }
dependencies = ["peppercorn"]

[project.urls]
homepage = "https://github.com/pypa/sampleproject"
```

## 打包并发布

```sh
# 安装 twine 依赖库
$ python -m pip install --upgrade twine

# 构建并使用 twine 发布代码
$ python -m build
$ python -m twine upload dist/*
```

## 本地开发

在本地开发的时候, 会希望源代码改变后, 会立即在其它项目中生效, 此时可以使用如下方式安装:

```sh
$ python -m pip install --editable .
```
