import glob
import os
import subprocess
import sys


def call(command):
    print('$', command)
    r = subprocess.call(command, shell=True)
    if r != 0:
        sys.exit(r)


def make():
    call('mkdocs build -d site_build')
    call('rm -rf site')
    call('mv site_build site')
    call('echo -n "Pem1L7uAVI" > site/baidu_verify_Pem1L7uAVI.html')
    call('echo -n "google-site-verification: google9b75b4b4147e247b.html" > site/google9b75b4b4147e247b.html')
    call('echo -n "google.com, pub-5236818090688638, DIRECT, f08c47fec0942fa0" > site/ads.txt')
    call('rm site/img/favicon.ico')
    call('cp docs/img/favicon.ico site/img/favicon.ico')


def exam_imgs():
    imgs = [i[4:] for i in glob.glob('docs/img/**/*.*', recursive=1)]
    docs = glob.glob('docs/content/**/*.md', recursive=1)

    imgs_dict = dict.fromkeys(imgs, 0)
    imgs_dict.pop('/img/favicon.ico')
    imgs_dict.pop('/img/wx_qrcode.jpg')
    imgs_dict.pop('/img/cover.gif')

    for e in docs:
        with open(e) as f:
            for line in f:
                line = line.strip()
                if line.startswith('![img]'):
                    p = line[7:-1]
                    assert p in imgs_dict, f'missed {e} {p}'
                    imgs_dict[p] += 1

    for k, v in imgs_dict.items():
        assert v != 0, f'unused {k}'


def main():
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    exam_imgs()
    make()


if __name__ == '__main__':
    main()
