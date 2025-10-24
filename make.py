import glob
import os
import subprocess

import PIL.Image


def make():
    r = subprocess.run('git status mkdocs.yml', capture_output=True, shell=True)
    if 'nothing to commit, working tree clean' in r.stdout.decode():
        r = subprocess.run('mkdocs build --dirty', shell=True)
        assert r.returncode == 0
    else:
        r = subprocess.run('mkdocs build --clean', shell=True)
        assert r.returncode == 0
    with open('site/baidu_verify_codeva-bkxO1ABXUL.html', 'w') as f:
        f.write('9530b96b26004efa430cc08502bdb442')
    with open('site/03890937a90586962ffe04ea5adaa43c.txt', 'w') as f:  # 360
        f.write('03890937a90586962ffe04ea5adaa43c')
    with open('site/google9b75b4b4147e247b.html', 'w') as f:
        f.write('google-site-verification: google9b75b4b4147e247b.html')
    with open('site/ads.txt', 'w') as f:
        f.write('google.com, pub-5236818090688638, DIRECT, f08c47fec0942fa0')


def mini():
    for html in glob.glob('site/**/*.html', recursive=True):
        with open(html, 'r+') as f:
            data = f.read()
            f.seek(0)
            f.truncate(0)
            f.write(data)


def exam_imgs_unused():
    imgs = glob.glob('docs/img/**/*.*', recursive=True)
    docs = glob.glob('docs/content/**/*.md', recursive=True)
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
    imgs = glob.glob('docs/img/**/*.*', recursive=True)
    for e in imgs:
        i = PIL.Image.open(e)
        assert i.format in ['JPEG', 'GIF'], f'format {e} {i.format}'


def exam_imgs_size():
    imgs = glob.glob('docs/img/**/*.*', recursive=True)
    for e in imgs:
        i = PIL.Image.open(e)
        assert i.size[0] == 480 and i.size[1] % 2 == 0, f'imsize {e} {i.size[0]}x{i.size[1]}'


def exam_link(name: str):
    for e in os.scandir(name):
        p = os.path.join(name, e.name)
        assert not e.is_symlink()
        if e.is_dir():
            exam_link(p)


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    exam_imgs_unused()
    exam_imgs_format()
    exam_imgs_size()
    exam_link('site')
    make()
    mini()


if __name__ == '__main__':
    main()
