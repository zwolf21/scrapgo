from .urlparser import *
import json


def mkdir_p(path):
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def cp(path, content):
    with open(path, 'wb') as fp:
        fp.write(content)


def parse_jsonp(jsonp, **kwargs):
    js = jsonp[jsonp.index("(") + 1: jsonp.rindex(")")]
    return json.loads(js, **kwargs)
