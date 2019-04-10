import re
from collections import defaultdict
from itertools import takewhile

from scrapgo.utils.shortcuts import parse_path, queryjoin
from .actions import *


class ActionContainer(object):
    LINK_RELAY = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)

        if not isinstance(self.LINK_RELAY[0], Root):
            self.LINK_RELAY.insert(
                0, url(self.ROOT_URL, as_root=True, refresh=True))

        for index, action in enumerate(self.LINK_RELAY):
            if isinstance(action, (Root, Url)):
                if hasattr(self, 'ROOT_URL') and self.ROOT_URL is None:
                    self.ROOT_URL = action.url
                action.set_params = self._get_method(
                    action.set_params, 'set_params'
                )
            if isinstance(action, FormatUrl):
                action.formater = self._get_method(action.formater, 'formater')

            action.parser = self._get_method(action.parser, 'parser')
            action.filter = self._get_method(action.filter, 'filter')

    def _relay_actions(self, handle_actions, context, until=None):
        results = defaultdict(list)
        responses = []

        for action in self.LINK_RELAY:
            if isinstance(action, Root):
                responses += handle_actions(action, None, context, results)
                continue
            next_responses = []
            for response in responses:
                next_responses += handle_actions(
                    action, response, context, results
                )
            responses = next_responses
            if until is not None and action.name == until:
                break
        return results

    def _get_method(self, func, kind):
        if callable(func):
            return func
        if isinstance(func, str):
            if hasattr(self, func):
                return getattr(self, func)

        return {
            'filter': self.main_filter,
            'parser': self.default_parser,
            'formater': self.url_formater,
            'set_params': self.set_params
        }[kind]

    def default_parser(self, response, match, soup, context=None):
        return

    def main_filter(self, link, match, query, context=None):
        return True

    def url_formater(self, template, context=None):
        return []

    def set_params(self, response, url, params, context=None):
        return queryjoin(url, params)

    def get_action(self, name, many=False):
        actions = []
        for action in self.LINK_RELAY:
            if action.name == name:
                if many == False:
                    return action
                else:
                    actions.append(action)
        if actions:
            return actions
        raise ValueError('Invalid name: {}'.format(name))
