import os
import subprocess
import sys


def call(command):
    print('$', command)
    r = subprocess.call(command, shell=True)
    if r != 0:
        sys.exit(r)


def make():
    os.chdir(os.path.dirname(os.path.realpath(__file__)))
    call('mkdocs build -d site_build')
    call('rm -rf site')
    call('mv site_build site')
    call('echo -n "Pem1L7uAVI" > site/baidu_verify_Pem1L7uAVI.html')
    call('echo -n "google-site-verification: google9b75b4b4147e247b.html" > site/google9b75b4b4147e247b.html')
    call('echo -n "google.com, pub-5236818090688638, DIRECT, f08c47fec0942fa0" > site/ads.txt')
    call('rm site/img/favicon.ico')
    call('cp docs/img/favicon.ico site/img/favicon.ico')


def main():
    make()


if __name__ == '__main__':
    main()
