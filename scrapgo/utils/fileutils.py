import os
import json


def mkdir_p(path):
    if not os.path.isdir(path):
        os.makedirs(path, exist_ok=True)


def cp(path, content):
    with open(path, 'wb') as fp:
        fp.write(content)


def read_json(path):
    with open(path, encoding='utf-8') as fp:
        return json.loads(fp.read())


def parse_jsonp(jsonp, **kwargs):
    js = jsonp[jsonp.index("(") + 1: jsonp.rindex(")")]
    return json.loads(js, **kwargs)


def get_file_extension(path):
	fn, ext = os.path.splitext(path)
	return ext