# 人工智能/Stable Diffusion 面容修复

## 前言

这篇文章距离上一篇文章已经隔了半年之久了, 由于最近有一些想法想借助 AI 实现, 所以又把 Stable Diffusion 拿起来了. Stable Diffusion 在生成人脸图像的时候, 多数时候生成的五官图像均惨不忍睹, 偶尔爆了幸运才能生成一张精致的人脸. 在一番搜索后得知其有一个面容修复模型可以修复人像的五官, 修复效果惊人!

同时这次我会在 Windows 操作系统和一张 Nvidia GTX 1066 显卡上运行 Stable Diffusion WebUI, 相比起第一次在云服务器上动辄一个小时的出图时间, 现在平均出图时间只用一分钟左右.

## Windows + Nvidia 环境

阅读官方这篇 [Install-and-Run-on-NVidia-GPUs](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/Install-and-Run-on-NVidia-GPUs) 文章基本能不踩坑的安装好, 但是我在下载模型和从 Github 克隆仓库的时候遇到了问题: 无法访问互联网... 自从开始用国外云服务器写代码以来, 已经 8 年时间没用墙内电脑做开发了...

## 代理

Stable Diffusion WebUI 依赖 Python 3.10.6 和 Git 工具. 安装好它们, 然后为其设置代理可以解决克隆仓库失败和 Pip 下载失败的问题:

```sh
$ pip config set global.proxy 127.0.0.1:1080

$ git config --global https.proxy 127.0.0.1:1080
$ git config --global http.proxy 127.0.0.1:1080
```

同时在运行 `webui.bat` 之前, 设置 `HTTPS_PROXY` 和 `HTTP_PROXY` 环境变量, 接着添加 `--no-half` 参数运行即可.

```sh
$ $Env:HTTPS_PROXY="127.0.0.1:1080"
$ $Env:HTTP_PROXY="127.0.0.1:1080"

$ ./webui.bat --no-half
```

等待一段时间, 浏览器窗口会自动打开.

## 面容修复

勾选 Settings / Face restoration / Restore faces 即可.

## 修复效果

**开启前**

![img](../../img/ai/stable_diffusion_face_restoration/grid-0000.jpg)

**开启后**

开启面容修复选项后, Stable Diffusion WebUI 会自动下载相关模型文件, 约 10 个 G 大小, 代理速度慢的话得有的等的.

![img](../../img/ai/stable_diffusion_face_restoration/grid-0001.jpg)

修复效果还是非常好的, 修复前目测平均四张图只能出一张正常图, 开启后概率至少提高三倍.
