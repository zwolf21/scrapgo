import re
from collections import namedtuple

Link = namedtuple(
    'Link', 'pattern urlfilter parser name recursive caching'
)

Location = namedtuple('Location', 'url parser name caching')

Source = namedtuple('Source', 'pattern, urlfilter parser name caching')


def location(url, parser, name=None, caching=True):
    return Location(url, parser, name or url, caching)


def href(pattern, urlfilter=None, parser=None, name=None, recursive=False, caching=True):
    regx = re.compile(pattern)
    return Link(
        regx,
        urlfilter,
        parser,
        name or pattern,
        recursive,
        caching
    )


def src(pattern, urlfilter=None, parser=None, name=None, caching=True):
    regx = re.compile(pattern)
    return Source(
        regx,
        urlfilter,
        parser,
        name or pattern,
        caching
    )
