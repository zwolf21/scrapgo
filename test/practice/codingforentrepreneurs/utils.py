from urllib.parse import urlparse, quote, urlunparse


def urlencode(url):
    map_encode_char = {
        '+': '%2B',
        '&': '%26'
    }
    for sep, repl in map_encode_char.items():
        url = url.replace(sep, repl)
    return url


def encodepath(url):
    map_encode_char = {
        '+': '%2B',
        '&': '%26'
    }
    p = urlparse(url)
    path = p.path
    u = p._replace(path=quote(path))
    return urlunparse(u)


def transpath(path):
    trantab = {
        '|': '[]'
    }
    for sep, repl in trantab.items():
        path = path.replace(sep, repl)
    return path
