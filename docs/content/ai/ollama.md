# 人工智能/OLLAMA

Ollama 是一个开源的人工智能对话模型框架, 可以在一个工具内方便自由的切换使用不同的对话模型. 我们可以利用它进行各种异想天开的对话任务.

项目地址: <https://github.com/ollama/ollama>

## 安装

这里只记录在 Linux amd64 操作系统环境下的安装步骤:

```sh
$ curl -L https://ollama.com/download/ollama-linux-amd64.tgz -o ollama-linux-amd64.tgz
$ mkdir ollama
$ sudo tar -C ollama -xzf ollama-linux-amd64.tgz
```

## 启动

ollama 的架构分为服务端和客户端, 服务端需要一直保持在后台运行, 客户端则可以随时启动或退出.

```sh
# 启动服务端
$ ollama serve

# 启动客户端, 开始语言对话
$ ollama run llama3.2
```
