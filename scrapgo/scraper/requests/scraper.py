from collections import abc

from scrapgo.modules import CachedRequests, SoupParserMixin
from .base import RequestsSoupCrawler
from .actions import *


class LinkPatternScraper(LinkPatternContainerMixin, RequestsSoupCrawler):

    def __init__(self, *args, context=None, **kwargs):
        self.context = context or {}
        super().__init__(*args, **kwargs)
        self._set_root(self.ROOT_URL)

    def _get_method(self, func, kind):
        if callable(func):
            return func
        if isinstance(func, str):
            if hasattr(self, func):
                return getattr(self, func)

        return {
            'filter': self.main_filter,
            'parser': self.default_parser,
            'set_header': self.set_headers
        }[kind]

    def default_parser(self, response, match, soup, context=None):
        return

    def main_filter(self, link, match, context=None):
        return True

    def set_headers(self, location, previous, headers):
        return headers

    def _handle_location(self, action, context, results):
        parser = self._get_method(action.parser, 'parser')
        set_header = self._get_method(action.set_header, 'set_header')
        url = self.ROOT_URL if action.url == '/' else action.url
        headers = set_header(url, url, self.get_header())
        response = self.get(url, headers, action.refresh)
        match = None
        soup = self._get_soup(response.content)
        parsed = parser(response, match, soup, context=context)
        self.reducer(parsed, action.name, results)
        return [action.url]

    def _handle_link(self, action, root, context, results):
        kwargs = {
            'root': root,
            'pattern': action.pattern,
            'filter': self._get_method(action.filter, 'filter'),
            'set_header': self._get_method(action.set_header, 'set_header'),
            'parser': self._get_method(action.parser, 'parser'),
            'context': context,
            'recursive': action.recursive,
            'refresh': action.refresh
        }
        next_urls = []
        for link, parsed in self._crawl(**kwargs):
            next_urls.append(link)
            self.reducer(parsed, action.name, results)
        if isinstance(action, Source):
            return [root]
        else:
            return next_urls

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
            self.ROOT_URL,
            self._handle_location,
            self._handle_link,
            self._handle_link,
            self.context
        )
        return results