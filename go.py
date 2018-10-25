import glob
import re
import subprocess


def test():
    subprocess.call('mkdocs serve --dirtyreload -f mkdocs-dev.yml', shell=True)


def show():
    subprocess.call('mkdocs serve --dirtyreload', shell=True)


def main():
    subprocess.call('git pull origin master', shell=True)
    subprocess.call('mkdocs build', shell=True)
    with open('./site/baidu_verify_Pem1L7uAVI.html', 'w') as f:
        f.write('Pem1L7uAVI')
    with open('./site/google9b75b4b4147e247b.html', 'w') as f:
        f.write('google-site-verification: google9b75b4b4147e247b.html')


if __name__ == '__main__':
    main()
