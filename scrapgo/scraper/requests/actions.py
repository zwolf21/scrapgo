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

    def _relay_patterns(self, seed, handle_location, handle_link, handle_source, context):
        results = defaultdict(list)
        responses = []

        for index, action in enumerate(self.LINK_PATTERNS):

            if isinstance(action, Location):
                responses += handle_location(action, context, results)
                continue

            if index == 0:
                responses.append(seed)

            next_responses = []
            for response in responses:
                if isinstance(action, Link):
                    next_responses += handle_link(
                        action, response, context, results
                    )
                else:
                    next_responses += handle_source(
                        action, response, context, results
                    )
            responses = next_responses
        return results

    def get_action(self, name):
        for action in self.LINK_PATTERNS:
            if action.name == name:
                return action
        raise ValueError('InValid name: {}'.format(name))
