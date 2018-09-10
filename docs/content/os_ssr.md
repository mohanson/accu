# Esay install

```sh
git clone https://github.com/shadowsocksr-backup/shadowsocksr.git
git checkout manyuser
cd shadowsocksr
bash initcfg.sh

# 于 config.json 配置端口, 密码等
# 通常配置 port 与 password 即可

# 启动服务, 可以使用 supervisor 托管
cd shadowsocks
python server.py -c ../config.json
# 启动客户端
python local.py -s host -c ../config.json
```

# Supervisor 配置

```ini
[program:ssr]
directory = /src/shadowsocksr/shadowsocks
command = python server.py -c ../config.json
redirect_stderr = true
stdout_logfile = /data/logs/ssr.log
stdout_logfile_backups = 1
```

# Windows 下的 bat 客户端

```bat
@echo off
if "%1" == "h" goto begin
mshta vbscript:createobject("wscript.shell").run("%~nx0 h",0)(window.close)&&exit
:begin

cd /src/shadowsocksr/shadowsocks && python local.py -s HOST -c ../config.json
```

# Firefox
安装插件 foxyproxy standard

新建代理服务器 127.0.0.1:1080, 选择 socks5, 模式, 模式订阅使用 [https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt](https://raw.githubusercontent.com/gfwlist/gfwlist/master/gfwlist.txt)
