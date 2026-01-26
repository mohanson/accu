import os
import pathlib

src = '/home/ubuntu/src/pxsol/doc/zh/markdown/content'

for e in os.scandir(src):
    new = pathlib.Path(e.path).read_text()
    new = new.replace('![img](../img/', '![img](../../img/solana/')
    old = pathlib.Path(e.name).read_text()
    if old == new:
        continue
    print(f'update {e.name}')
    pathlib.Path(e.name).write_text(new)
