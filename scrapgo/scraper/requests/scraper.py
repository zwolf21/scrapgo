from collections import abc

from scrapgo.utils.shortcuts import parse_query, parse_path
from scrapgo.modules import CachedRequests, SoupParserMixin
from .crawler import RequestsSoupCrawler
from .action import *


class LinkRelayScraper(ActionContainer, RequestsSoupCrawler):

    def __init__(self, **kwargs):
        super().__init__(**kwargs)

    def reducer(self, parsed, name, results):
        if parsed is None:
            return
        if isinstance(parsed, (str, bytes)):
            results[name].append(parsed)
        elif isinstance(parsed, abc.Mapping):
            results[name].append(parsed)
        elif isinstance(parsed, abc.Iterable):
            results[name].extend(list(parsed))

    def scrap(self, root_params=None, context=None, until=None):
        self.context = context or {}
        self.root_params = root_params
        return self._relay_actions(
            self._handle_actions,
            context,
            until
        )

    def _handle_actions(self, action, response, context, results):
        if response is None:
            response = self.get(self.ROOT_URL)

        kwargs = {
            'response': response,
            'context': context,
            'filter': action.filter,
            'parser': action.parser,
            'refresh': action.refresh,
            'referer': self.find_referer(action, response),
            'fields': action.fields
        }
        if isinstance(action, (Root, Url)):
            if action.url == '/':
                action.url = self.ROOT_URL
            url = action.set_params(
                response, action.url, self.root_params, context)
            if isinstance(url, str):
                patterns = [url]
            else:
                patterns = list(url)
        elif isinstance(action, RegexUrl):
            patterns = [action.regex]
            kwargs['recursive'] = action.recursive
        elif isinstance(action, FormatUrl):
            patterns = action.formater(action.template, context=context)
            if isinstance(patterns, str):
                patterns = [patterns]
        else:
            patterns = [action.url]

        next_responses = []
        for pattern in patterns:
            kwargs['pattern'] = pattern
            for rsp, parsed in self._crawl(**kwargs):
                if not self._is_parsable(rsp):
                    action.static = True
                next_responses.append(rsp)
                self.reducer(parsed, action.name, results)

        if action.static == True:
            return [response]
        return next_responses

    def find_referer(self, action, response):
        if response is None:
            return self.ROOT_URL
        if not action.referer or not hasattr(response, 'trace'):
            return
        action_name = action.referer
        tracer = response.trace
        actions = self.get_action(action_name, many=True)
        for action in actions:
            for url in tracer:
                link = parse_path(url)
                if isinstance(action, (Url, Root)):
                    if action.url in [url, link]:
                        return url
                else:
                    p = action.regex
                    if p.match(url) or p.match(link):
                        return url
