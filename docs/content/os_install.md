# 系统更新

```sh
yum -y update
yum -y install epel-release
yum -y install gcc readline-devel sqlite-devel openssl-devel zlib-devel libffi-devel

# 中文乱码
# 修改 /etc/locale.conf
LANG="en_US.UTF-8"

# 修改 ~/.bash_profile
stty erase ^h
```

# 安装 python

```sh
# 3.6.3 版本
version=3.6.3

wget https://www.python.org/ftp/python/${version}/Python-${version}.tgz
tar -zxvf Python-${version}.tgz
cd Python-${version}
mkdir -p /usr/local/python
mkdir -p /usr/local/python/lib
./configure --enable-shared --prefix /usr/local/python LDFLAGS="-Wl,-rpath /usr/local/python/lib"
make
make install
```

```sh
# 修改 ~/.bash_profile
export PATH=$PATH:/usr/local/python/bin

# 墙内的话可以更改并使用豆瓣的源
# 修改或新建 ~/.pip/pip.conf, windows 下为 ~/pip/pip.ini
[global]
index-url = https://pypi.douban.com/simple
```

# 安装 golang

```sh
version=1.9

wget https://storage.googleapis.com/golang/go${version}.linux-amd64.tar.gz
tar -zxvf go${version}.linux-amd64.tar.gz
mv go /usr/local/go
mkdir /usr/local/gopath
```

```sh
# 修改 ~/.bash_profire
export GOROOT=/usr/local/go
export GOPATH=/usr/local/gopath
export PATH=$PATH:$GOROOT/bin
export PATH=$PATH:$GOPATH/bin
```

# 安装 screen

```sh
yum -y install screen

# 创建 ~/.screenrc
shell -$SHELL

# 修改 ~/.bashrc
alias sr='screen -r'

# 修改 ~/.bash_profile
case $TERM in
  screen*)
    export PS1='[\u:screen \w]\$ '
    ;;
  *)
    export PS1='[\u \w]\$ '
    ;;
esac
```

# 安装 tmpwatch

```sh
yum -y install tmpwatch

# 修改 /etc/crontab
24 7 * * * root /usr/sbin/tmpwatch -u -f 108 /tmp
24 7 * * * root /usr/sbin/tmpwatch -u -f 108 /var/tmp

#重启 crond
systemctl restart  crond.service
```

# 安装 supervisor

```shell
yum -y install supervisor
supervisord -c /etc/supervisord.conf
systemctl enable supervisord.service
```

supervisor 配置文件位于 /etc/supervisord.conf 与 /etc/supervisord.d, 应用配置文件应位于 /etc/supervisord.d, 并以 .ini 结尾. 如下是一个简单的 http server 服务配置.

```ini
[program:httpserver]
directory = /tmp
environment=
    env1=env1,
    env2=env2
command = python3 -m http.server
redirect_stderr = true
stdout_logfile_maxbytes = 20MB
stdout_logfile_backups = 5
stdout_logfile = /data/logs/httpserver.log
```

新增或修改配置文件后, 使用 `supervisor update` 更新.

# 密钥登录

将本机的 id\_rsa.pub 内容复制到 ~/.ssh/authorized\_keys 内.

```sh
# 修改 /etc/ssh/sshd_config
PubkeyAuthentication yes
PasswordAuthentication no

# 重启 sshd
systemctl restart sshd
```
