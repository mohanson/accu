# Python/使用 requests 下载显示进度

```py
import contextlib
import requests

resp = requests.get('http://httpbin.org/get', stream=True)
with contextlib.closing(resp) as r:
    accepts = 0
    for data in r.iter_content(chunk_size=32):
        accepts += len(data)
        progress = accepts / int(r.headers['Content-Length'])
        print(f'{progress:4.2f}')
```

```text
0.10
0.21
0.31
0.42
0.52
0.63
0.73
0.84
0.94
1.00
```
