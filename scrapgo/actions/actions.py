import re
from collections import namedtuple

Link = namedtuple(
    'Link', 'pattern urlfilter parser name recursive'
)

Location = namedtuple('Location', 'url parser name')

Source = namedtuple('Source', 'pattern, urlfilter parser name')


def location(url, parser, name=None):
    return Location(url, parser, name or url)


def href(pattern, urlfilter=None, parser=None, name=None, recursive=False):
    regx = re.compile(pattern)
    return Link(
        regx,
        urlfilter,
        parser,
        name or pattern,
        recursive,
    )


def src(pattern, urlfilter=None, parser=None, name=None):
    regx = re.compile(pattern)
    return Source(
        regx,
        urlfilter,
        parser,
        name or pattern
    )
