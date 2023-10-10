# 人工智能/Stable Diffusion API

Stable Diffusion 除了默认的 WebUI 之外, 还有一套 API 接口, 借助 API 接口可以帮助我们实现一些自动化的事情, 例如循环不停出图--如果我们只使用 WebUI 的话, 唯一的办法就是不停的用手点击, 我们可是程序员耶, 这种事情必须自动化!

## 启动参数

首先, 在运行 web ui 的时候添加 `--api` 参数. 例如

```sh
$ bash webui.sh --api
```

这会启用 API 接口, 你可以在 `http://127.0.0.1:7860/docs` 上访问 API 文档. 目前让我们只专注于文生图接口 `/sdapi/v1/txt2img`. 我们的目的是让 Stable Diffusion 按照要求不停的出图.

## 代码实现

```py
import requests

host = "http://127.0.0.1:7860"

# 首先设置要使用的模型. 模型的名称可以通过 /sdapi/v1/sd-models 获得.
requests.post(url=f'{host}/sdapi/v1/options', json={
    'sd_model_checkpoint': 'chilloutmix_NiPrunedFp32Fix.safetensors [fc2511737a]',
})

# 设置文生图的参数
body = {
    "prompt": "beautiful, masterpiece, best quality, extremely detailed face",
    "negative_prompt": "paintings, sketches",
    "width": 480,
    "height": 270,
    "batch_size": 4,
    "save_images": True,   # 要保存图像. 默认情况下图像不会保存到 outputs/txt2img-images 内.
    "send_images": False,  # 不返回图像. 默认情况下会将图像使用 base64 返回.
    "restore_faces": True, # 修复人脸哟.
    "steps": 20,
}

# 设置一个循环让其不停出图, 耶!
for _ in range(1 << 1024):
    requests.post(url=f'{host}/sdapi/v1/txt2img', json=body)
```

图像生成位置在 `outputs/txt2img-images`, 短短一会就生成这么多图像, 真是太棒了.

```sh
$ tree outputs/txt2img-images/2023-10-01/

outputs/txt2img-images/2023-10-01/
├── 00000-3005953957.png
├── 00001-3005953958.png
├── 00002-3005953959.png
├── 00003-3005953960.png
├── 00004-1143834554.png
├── 00005-1143834555.png
├── 00006-1143834556.png
├── 00007-1143834557.png
├── 00008-1722353361.png
├── 00009-1722353362.png
├── 00010-1722353363.png
├── 00011-1722353364.png
├── 00012-3997631580.png
├── 00013-3997631581.png
├── 00014-3997631582.png
├── 00015-3997631583.png
├── 00016-457252506.png
├── 00017-457252507.png
├── 00018-457252508.png
├── 00019-457252509.png
├── 00020-421652671.png
├── 00021-421652672.png
├── 00022-421652673.png
├── 00023-421652674.png
├── 00024-2769114944.png
├── 00025-2769114945.png
├── 00026-2769114946.png
├── 00027-2769114947.png
├── 00028-1296436480.png
├── 00029-1296436481.png
├── 00030-1296436482.png
└── 00031-1296436483.png
```

## 参考

- [0] [Kilvoctu, API](https://github.com/AUTOMATIC1111/stable-diffusion-webui/wiki/API)
