# 杂项/云服务器环境下使用 QEMU 安装和使用虚拟机

QEMU 是一个通用和开源的机器模拟器和虚拟机. 这篇文章记录一下我在无 GUI 的云服务器上使用 QEMU 安装 Ubuntu 22.04.3 虚拟机的步骤.

```sh
# 安装 QEMU.
$ sudo apt-get install -y qemu

# 下载 Ubuntu 22.04.3 镜像.
$ wget https://mirrors.xjtu.edu.cn/ubuntu-releases/22.04.3/ubuntu-22.04.3-live-server-amd64.iso

# 将镜像挂载在 ubuntu-mount 目录.
$ sudo mount ubuntu-22.04.3-live-server-amd64.iso ubuntu-mount

# 为虚拟机系统创建硬盘文件.
$ qemu-img create -f qcow2 ubuntu.img 16G

# 安装 Ubuntu 22.04.3
$ qemu-system-x86_64 -m 2048 -hda ubuntu.img -cdrom ubuntu-22.04.3-live-server-amd64.iso -nographic -append console=ttyS0 -kernel ubuntu-mount/casper/vmlinuz -initrd ubuntu-mount/casper/initrd

# 取消镜像挂载
$ sudo umount ubuntu-mount

# 进入新安装好的虚拟机
$ qemu-system-x86_64 -m 2048 -hda ubuntu.img --nographic

# 退出虚拟机 Ctrl + A，然后按 X 键
```
