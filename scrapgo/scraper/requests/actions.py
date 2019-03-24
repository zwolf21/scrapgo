import re
from collections import namedtuple, defaultdict

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


def location(url, filter=None, parser=None, name=None, recursive=False, refresh=True, set_header=None):
    if isinstance(url, (str, bytes)):
        url = [url]
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


class LinkPatternContainerMixin(object):
    LINK_PATTERNS = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _set_root(self, root=None):
        error_message = \
            'Define ROOT_URL or at least one location in SCRP_RELAY'
        if root is None:
            locations = [
                act for act in self.LINK_PATTERNS if isinstance(act, Location)
            ]
            if not locations:
                raise ValueError(error_message)
            self.ROOT_URL = locations[0].url[0]
        elif self.LINK_PATTERNS is None:
            if self.ROOT_URL is None:
                raise ValueError(error_message)
            loc = location(self.ROOT_URL, refresh=True)

    def _relay_patterns(self, seed, handle_location, handle_link, handle_source, context):
        results = defaultdict(list)
        urls = [seed]
        for action in self.LINK_PATTERNS:
            next_urls = []
            for root in urls:
                if isinstance(action, Location):
                    next_urls += handle_location(action, context, results)
                elif isinstance(action, Link):
                    next_urls += handle_link(action, root, context, results)
                elif isinstance(action, Source):
                    next_urls += handle_source(action, root, context, results)
            urls = next_urls
            # print('next_urls:', next_urls)
        return results

    def get_action(self, name):
        for action in self.LINK_PATTERNS:
            if action.name == name:
                return action
        raise ValueError('InValid name: {}'.format(name))
