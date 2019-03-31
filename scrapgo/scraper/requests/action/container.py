import re
from collections import defaultdict

from scrapgo.utils.shortcuts import parse_path
from .actions import *


class LinkPatternContainerMixin(object):
    LINK_PATTERNS = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

    def _relay_patterns(self, seed, handle_location, handle_link, handle_source, context, until):
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
            if until is not None and action.name == until:
                break
        return results

    def get_action(self, name, many=False):
        actions = []
        for action in self.LINK_PATTERNS:
            if action.name == name:
                if many == False:
                    return action
                else:
                    actions.append(action)
        if actions:
            return actions
        raise ValueError('InValid name: {}'.format(name))

    def find_referer(self, action, response):
        if not action.referer or not hasattr(response, 'trace'):
            return
        action_name = action.referer
        tracer = response.trace
        actions = self.get_action(action_name, many=True)
        for action in actions:
            for url in tracer:
                link = parse_path(url)
                if isinstance(action, Location):
                    if action.url in [url, link]:
                        return url
                else:
                    p = action.pattern
                    if p.match(url) or p.match(link):
                        return url
