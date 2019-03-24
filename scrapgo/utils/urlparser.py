import os
from urllib.parse import urlparse, urlunparse, parse_qsl, parse_qs, urljoin

from requests import Request, Session


def abs_path(root, url):
    # print('abs_path:root', root)
    # print('abs_path:url', url)
    return urljoin(root, url)


def parse_path(url):
    p = urlparse(url)
    args = '', '', p.path, p.params, p.query, p.fragment
    return urlunparse(args)


def parse_root(url):
    p = urlparse(url)
    args = p.scheme, p.netloc, '', '', '', ''


def parse_query(url, qsl=True):
    parse = urlparse(url)
    queryset = parse_qsl(parse.query) if qsl == True else parse_qs(parse.query)
    return dict(queryset)


def parse_src(url):
    p = urlparse(url)
    return os.path.basename(p.path)


def queryjoin(url, params=None):
    r = Request('GET', url, params=params)
    s = Session()
    return s.prepare_request(r).url
