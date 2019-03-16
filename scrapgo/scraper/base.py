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

    def get(self, link, cache, headers=None):
        url = abs_path(self.ROOT_URL, link)
        return self.requests_manager._get(url, cache=cache, headers=headers)

    def _get_fuction(self, func, kind='urlfilter'):
        if callable(func):
            return func
        if isinstance(func, str):
            if hasattr(self, func):
                return getattr(self, func)
        return self. main_urlfilter if kind == 'urlfilter' else self.default_parser

    def _scrap_links(self, root, link_pattern, urlfilter, context=None, recursive=None, cache=True, set_headers=None):
        linkstack = SetStack([(root, self.requests_manager.get_header())])
        visited = set()
        set_headers = set_headers or (
            lambda location, previous, headers: headers
        )
        while linkstack:
            root, headers = linkstack.pop()
            requests = self.get(root, cache=cache, headers=headers)
            for link in self._parse_link(requests, link_pattern):
                if link not in visited:
                    visited.add(link)
                    if not self.main_urlfilter(link, link_pattern, context=context):
                        continue
                    if urlfilter(link, link_pattern, context=context):
                        if recursive:
                            current_headers = self.requests_manager.get_header()
                            headers = set_headers(link, root, current_headers)
                            linkstack.push((link, headers))
                        yield link

    def main_urlfilter(self, url, pattern, context=None):
        return True

    def default_parser(self, url, pattern, content=None, soup=None):
        return
