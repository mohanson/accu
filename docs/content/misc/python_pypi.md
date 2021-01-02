# 杂项/Python Pypi

官方教程: [https://packaging.python.org/tutorials/distributing-packages/](https://packaging.python.org/tutorials/distributing-packages/)

示例项目: [https://github.com/pypa/sampleproject](https://github.com/pypa/sampleproject)

## 配置账号

在 $HOME 下写入以下内容至 .pypirc

```ini
[distutils]
index-servers =
    pypi

[pypi]
username = username
password = password
```

## 创建 setup.py

```py
import setuptools

setuptools.setup(
    name='sample',
    version='1.2.0',
    url='https://github.com/pypa/sampleproject',
    license='MIT',
    author='The Python Packaging Authority',
    author_email='pypa-dev@googlegroups.com',
    description='A sample Python project',
    packages=['sample'],
    install_requires=[
        'peppercorn',
    ]
)
```

## 打包并发布

```sh
$ python -m pip install --upgrade twine

$ python setup.py sdist
$ python -m twine upload dist/*
```

## 提示

**发布模块与文件**

在 setup.py 中, 使用 `packages=['sample']` 会发布 sample 目录(包), 而使用 `py_modules=['sample']` 会发布 sample.py 文件. 大多数情况下, 你可以使用 `packages=setuptools.find_packages()` 自动发现代替手动填写.


**生成命令行程序**

```py
entry_points={
    'console_scripts': [
        'sample=sample:main',
    ],
}
```
在 setup.py 中配置以上代码, 一个名为 sample 的命令行程序将在安装此模块后生成.
