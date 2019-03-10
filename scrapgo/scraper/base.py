from collections import OrderedDict

import requests

from scrapgo.lib.data_structure import SetStack
from scrapgo.utils.shortcuts import abs_path
from scrapgo.modules import RequestsManager, SoupParserMixin


class BaseScraper(SoupParserMixin):
    ROOT_URL = None
    requests_manager = RequestsManager()

    def __init__(self, root=None, **kwargs):
        super().__init__(**kwargs)
        self.ROOT_URL = self.ROOT_URL or root

    def _get(self, link):
        url = abs_path(self.ROOT_URL, link)
        return self.requests_manager._get(url)

    def _get_fuction(self, func, kind='urlfilter'):
        if callable(func):
            return func
        if isinstance(func, str):
            if hasattr(self, func):
                return getattr(self, func)
        return self. main_urlfilter if kind == 'urlfilter' else self.default_parser

    def _scrap_links(self, root, link_pattern, urlfilter, context=None, recursive=None):
        linkstack = SetStack([root])
        visited = set()

        while linkstack:
            root = linkstack.pop()
            requests = self._get(root)
            for link in self._parse_link(requests, link_pattern):
                if link not in visited:
                    visited.add(link)
                    if not self.main_urlfilter(link, link_pattern, context=context):
                        continue
                    if urlfilter(link, link_pattern, context=context):
                        if recursive:
                            linkstack.push(link)
                        yield link

    def main_urlfilter(self, url, pattern, context=None):
        return True

    def default_parser(self, url, pattern, content=None, soup=None):
        return
