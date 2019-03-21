from .urlparser import *


def mkdir_p(path):
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def cp(path, content):
    with open(path, 'wb') as fp:
        fp.write(content)
