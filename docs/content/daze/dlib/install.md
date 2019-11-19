[dlib](http://dlib.net/) 是一个包含机器学习算法和工具的 c++ 库.

# 安装

```sh
$ git clone --depth=1 https://github.com/davisking/dlib.git
$ cd dlib
$ mkdir build; cd build; cmake .. ; cmake --build .
# 安装 python API
$ python setup.py install
```

详细请至 [https://github.com/davisking/dlib](https://github.com/davisking/dlib) 阅读官方文档.

**记录一: dlib Python API 需要 boost.python 支持**

简而言之, 前往 [http://www.boost.org/](http://www.boost.org/) 下载 boost 后, 使用如下命令安装即可, 注意使用 --with-python 配置 python 可执行文件, 安装脚本会自动寻找 python 的安装目录.

```sh
$ ./bootstrap.sh --prefix=/usr/local/boost --with-python=python3 --with-libraries=python
# CPLUS_INCLUDE_PATH 值为 pyconfig.h 所在路径
$ CPLUS_INCLUDE_PATH=/usr/local/python/include/python3.6m ./b2
$ ./b2 install
```

安装完毕后在 ~/.bash_profile 中设置环境变量

```sh
export PATH=$PATH:/usr/local/boost/include
export LD_LIBRARY_PATH=$LD_LIBRARY_PATH:/usr/local/boost/lib
```

**记录二: 内存过小导致编译失败**

```no-highlight
c++: internal compiler error: Killed (program cc1plus)
Please submit a full bug report,
with preprocessed source if appropriate.
See <http://bugzilla.redhat.com/bugzilla> for instructions.
gmake[2]: *** [CMakeFiles/dlib_.dir/src/vector.cpp.o] Error 4
gmake[1]: *** [CMakeFiles/dlib_.dir/all] Error 2
gmake: *** [all] Error 2
error: cmake build failed!
```

测试时 1G 内存导致编译失败, 使用额外的 1G swap 后重新编译解决问题:

```sh
$ dd if=/dev/zero of=/data/swap bs=64M count=16
$ chmod 0600 /data/swap
$ mkswap /data/swap
$ swapon /data/swap
```
