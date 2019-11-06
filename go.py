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


def main():
    make()


if __name__ == '__main__':
    main()
