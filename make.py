import glob
import os
import shutil
import subprocess
import tempfile

import PIL.Image
import lib.gool


def make():
    with tempfile.TemporaryDirectory() as output:
        subprocess.run(f'mkdocs build -d {output}', shell=True)
        shutil.copytree(f'{output}', 'site', dirs_exist_ok=True)
    with open('site/baidu_verify_codeva-bkxO1ABXUL.html', 'w') as f:
        f.write('9530b96b26004efa430cc08502bdb442')
    with open('site/03890937a90586962ffe04ea5adaa43c.txt', 'w') as f:  # 360
        f.write('03890937a90586962ffe04ea5adaa43c')
    with open('site/google9b75b4b4147e247b.html', 'w') as f:
        f.write('google-site-verification: google9b75b4b4147e247b.html')
    with open('site/ads.txt', 'w') as f:
        f.write('google.com, pub-5236818090688638, DIRECT, f08c47fec0942fa0')


def mini():
    if shutil.which('js-beautify') is None:
        print('main: mini skipped, js-beautify not found')
        return
    grun = lib.gool.cpu()
    for html in glob.glob('site/**/*.html', recursive=True):
        grun.call(subprocess.run, f'js-beautify -r --no-preserve-newlines {html}', shell=True)
    grun.wait()


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
    make()
    exam_link('site')
    mini()


if __name__ == '__main__':
    main()
