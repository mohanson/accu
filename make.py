import glob
import os
import subprocess
import sys

import PIL.Image


def call(command):
    print('$', command)
    r = subprocess.call(command, shell=True)
    if r != 0:
        sys.exit(r)


def make():
    call('mkdocs build')
    call('echo -n "9530b96b26004efa430cc08502bdb442" > site/baidu_verify_codeva-bkxO1ABXUL.html')
    call('echo -n "03890937a90586962ffe04ea5adaa43c" > site/03890937a90586962ffe04ea5adaa43c.txt')  # 360
    call('echo -n "google-site-verification: google9b75b4b4147e247b.html" > site/google9b75b4b4147e247b.html')
    call('echo -n "google.com, pub-5236818090688638, DIRECT, f08c47fec0942fa0" > site/ads.txt')


def mini():
    for html in glob.glob('site/**/*.html', recursive=1):
        with open(html, 'r+') as f:
            data = f.read()
            f.seek(0)
            f.truncate(0)
            f.write(data)


def exam_imgs_unused():
    imgs = glob.glob('docs/img/**/*.*', recursive=1)
    docs = glob.glob('docs/content/**/*.md', recursive=1)
    docs.append('docs/index.md')
    imgs_dict = dict.fromkeys(imgs, 0)

    for e in docs:
        with open(e) as f:
            for line in f:
                line = line.strip()
                if line.startswith('![img]'):
                    p = line[7:-1]
                    p = os.path.normpath(os.path.join(os.path.dirname(e), p))
                    assert p in imgs_dict, f'missed {e} {p}'
                    imgs_dict[p] += 1

    for k, v in imgs_dict.items():
        assert v != 0, f'unused {k}'


def exam_imgs_format():
    imgs = glob.glob('docs/img/**/*.*', recursive=1)
    for e in imgs:
        i = PIL.Image.open(e)
        assert i.format in ['JPEG', 'GIF'], f'format {e} {i.format}'


def exam_imgs_size():
    imgs = glob.glob('docs/img/**/*.*', recursive=1)
    for e in imgs:
        i = PIL.Image.open(e)
        assert i.size[0] == 480 and i.size[1] % 2 == 0, f'imsize {e} {i.size[0]}x{i.size[1]}'


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    exam_imgs_unused()
    exam_imgs_format()
    exam_imgs_size()
    make()
    mini()


if __name__ == '__main__':
    main()
