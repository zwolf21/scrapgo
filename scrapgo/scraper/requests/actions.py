import re
from collections import namedtuple

Location = namedtuple(
    'Location', 'url filter parser name recursive refresh set_header'
)

Link = namedtuple(
    'Link', 'pattern filter parser name recursive refresh set_header'
)


Source = namedtuple(
    'Source', 'pattern, filter parser name recursive refresh set_header')


def _set_header(location, previous, headers):
    return headers


def location(url, filter=None, parser=None, name=None, recursive=False, refresh=False, set_header=None):
    return Location(
        url,
        filter,
        parser,
        name or url,
        recursive,
        refresh,
        set_header or _set_header
    )


def href(pattern, filter=None, parser=None, name=None, recursive=False, refresh=False, set_header=None):
    regx = re.compile(pattern)
    return Link(
        regx,
        filter,
        parser,
        name or pattern,
        recursive,
        refresh,
        set_header=set_header or _set_header
    )


def src(pattern, filter=None, parser=None, name=None, refresh=False, set_header=None):
    regx = re.compile(pattern)
    return Source(
        regx,
        filter,
        parser,
        name or pattern,
        False,
        refresh,
        set_header or _set_header
    )
