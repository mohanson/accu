import subprocess
import sys


def call(command):
    print(command)
    r = subprocess.call(command, shell=True)
    if r != 0:
        sys.exit(r)


def test():
    call('mkdocs serve --dirtyreload -f mkdocs-dev.yml')


def show():
    call('mkdocs serve --dirtyreload')


def make():
    call('mkdocs build')
    with open('./site/baidu_verify_Pem1L7uAVI.html', 'w') as f:
        f.write('Pem1L7uAVI')
    with open('./site/google9b75b4b4147e247b.html', 'w') as f:
        f.write('google-site-verification: google9b75b4b4147e247b.html')
    with open('./site/ads.txt', 'w') as f:
        f.write('google.com, pub-5236818090688638, DIRECT, f08c47fec0942fa0')


def main():
    make()


if __name__ == '__main__':
    main()
