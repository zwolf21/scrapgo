from collections import abc

from scrapgo.utils.shortcuts import parse_query
from scrapgo.modules import CachedRequests, SoupParserMixin
from .crawler import RequestsSoupCrawler
from .action import *


class LinkPatternScraper(LinkPatternContainerMixin, RequestsSoupCrawler):

    def __init__(self, context=None, **kwargs):
        super().__init__(**kwargs)
        self.context = context or {}

    def _get_method(self, func, kind):
        if callable(func):
            return func
        if isinstance(func, str):
            if hasattr(self, func):
                return getattr(self, func)

        return {
            'filter': self.main_filter,
            'parser': self.default_parser,
            'set_header': self.set_headers,
        }[kind]

    def default_parser(self, response, match, soup, context=None):
        return

    def main_filter(self, link, query, match, context=None):
        return True

    def set_headers(self, location, previous, headers):
        return headers

    def _handle_location(self, action, context, results):
        parser = self._get_method(action.parser, 'parser')
        filter = self._get_method(action.filter, 'filter')
        set_header = self._get_method(action.set_header, 'set_header')
        url = self.ROOT_URL if action.url == '/' else action.url
        headers = set_header(url, url, self.get_header())
        query = parse_query(url)
        match = None
        if not self.main_filter(url, query, match, context=context):
            return []

        if not filter(url, query, match, context=context):
            return []
        response = self.get(url, headers=headers, refresh=action.refresh)
        soup = self._get_soup(response.content)
        parsed = parser(response, query, soup, context=context)
        self.reducer(parsed, action.name, results)
        return [response]

    def _handle_link(self, action, response, context, results):
        kwargs = {
            'response': response,
            'pattern': action.pattern,
            'filter': self._get_method(action.filter, 'filter'),
            'set_header': self._get_method(action.set_header, 'set_header'),
            'parser': self._get_method(action.parser, 'parser'),
            'context': context,
            'recursive': action.recursive,
            'refresh': action.refresh,
            'referer': self.find_referer(action, response)
        }
        next_responses = []
        for rsp, parsed in self._crawl(**kwargs):
            next_responses.append(rsp)
            self.reducer(parsed, action.name, results)
        if isinstance(action, Source):
            return [response]
        else:
            return next_responses

    def reducer(self, parsed, name, results):
        if parsed is None:
            return
        if isinstance(parsed, (str, bytes)):
            results[name].append(parsed)
        elif isinstance(parsed, abc.Mapping):
            results[name].append(parsed)
        elif isinstance(parsed, abc.Iterable):
            results[name].extend(list(parsed))

    def scrap(self, until=None):
        results = self._relay_patterns(
            self.get(self.ROOT_URL),
            self._handle_location,
            self._handle_link,
            self._handle_link,
            self.context,
            until
        )
        return results
