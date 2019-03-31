from collections import defaultdict
from .actions import *


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
