# 介绍

supervisor 是一个进程管理工具, 使用它, 可以:

1. 方便的用来启动, 重启以及关闭单个或多个进程
2. 开机自启动配置的进程
3. 配置的进程异常退出时, 自动重启

# 安装

```sh
# 安装
$ yum -y install supervisor
# 启动 supervisord
$ supervisord -c /etc/supervisord.conf
# 配置 supervisord 开机自启动
$ systemctl enable supervisord.service
```

# 入门

以一个静态文件服务器为例, 启动该服务的命令是 `python3 -m http.server`. 我需要后台运行该进程, 并且期望该进程能随操作系统的启动而自动启动. 要做到这一点, 在 /etc/supervisord.d/ 目录下新建一个文件 httpserver.ini 并写入:

```ini
[program:httpserver]
directory=/tmp
command=python3 -m http.server
stdout_logfile=/data/logs/httpserver.log
redirect_stderr=true
stdout_logfile_backups=2
```

接着使用 `supervisorctl update` 更新. 你应该可以看到以下输出:

```sh
$ supervisorctl update
httpserver: added process group
```

这表明该进程已经被 supervisor 托管了, `supervisorctl` 提供了许多子命令以用来管理进程, 查看 [http://supervisord.org/running.html#supervisorctl-actions](http://supervisord.org/running.html#supervisorctl-actions) 以了解更多.

# 配置文件说明

进程的配置文件均位于 /etc/supervisord.d, 并以 .ini 结尾. 关于配置的详细说明如下:

```ini
[program:theprogramname]
command=/bin/cat              ; the program (relative uses PATH, can take args)
process_name=%(program_name)s ; process_name expr (default %(program_name)s)
numprocs=1                    ; number of processes copies to start (def 1)
directory=/tmp                ; directory to cwd to before exec (def no cwd)
umask=022                     ; umask for process (default None)
priority=999                  ; the relative start priority (default 999)
autostart=true                ; start at supervisord start (default: true)
autorestart=true              ; retstart at unexpected quit (default: true)
startsecs=10                  ; number of secs prog must stay running (def. 1)
startretries=3                ; max # of serial start failures (default 3)
exitcodes=0,2                 ; 'expected' exit codes for process (default 0,2)
stopsignal=QUIT               ; signal used to kill process (default TERM)
stopwaitsecs=10               ; max num secs to wait b4 SIGKILL (default 10)
user=chrism                   ; setuid to this UNIX account to run the program
redirect_stderr=true          ; redirect proc stderr to stdout (default false)
stdout_logfile=/a/path        ; stdout log path, NONE for none; default AUTO
stdout_logfile_maxbytes=1MB   ; max # logfile bytes b4 rotation (default 50MB)
stdout_logfile_backups=10     ; # of stdout logfile backups (default 10)
stdout_capture_maxbytes=1MB   ; number of bytes in 'capturemode' (default 0)
stdout_events_enabled=false   ; emit events on stdout writes (default false)
stderr_logfile=/a/path        ; stderr log path, NONE for none; default AUTO
stderr_logfile_maxbytes=1MB   ; max # logfile bytes b4 rotation (default 50MB)
stderr_logfile_backups=10     ; # of stderr logfile backups (default 10)
stderr_capture_maxbytes=1MB   ; number of bytes in 'capturemode' (default 0)
stderr_events_enabled=false   ; emit events on stderr writes (default false)
environment=A=1,B=2           ; process environment additions (def no adds)
serverurl=AUTO                ; override serverurl computation (childutils)
```

# 参考
- [1] Supervisor: A Process Control System [http://supervisord.org/](http://supervisord.org/)
