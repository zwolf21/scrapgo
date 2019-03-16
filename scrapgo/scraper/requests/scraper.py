from collections import OrderedDict, defaultdict, abc

from scrapgo.lib.data_structure import SetStack
from scrapgo.utils.shortcuts import abs_path
from scrapgo.modules import CachedRequests, SoupParserMixin
from .actions import *


class RequestsSoupScraper(SoupParserMixin, CachedRequests):
    ROOT_URL = None
    SCRAP_RELAY = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        self._set_root()
        self.visited_cache = {}

    def _set_root(self):
        if self.ROOT_URL is None:
            self.ROOT_URL = self.SCRAP_RELAY[0].url
        elif self.SCRAP_RELAY is None:
            loc = Location(self.ROOT_URL, self.default_parser, self.ROOT_URL)
            self.SCRAP_RELAY = [loc]

    def get(self, link, headers=None, refresh=False):
        url = abs_path(self.ROOT_URL, link)
        if url in self.visited_cache:
            return self.visited_cache[url]
        r = self._get(url, headers, refresh)
        self.visited_cache[url] = r
        return r

    def _get_method(self, func, kind):
        if callable(func):
            return func
        if isinstance(func, str):
            if hasattr(self, func):
                # print('_get_method:func', func)
                return getattr(self, func)

        return {
            'filter': self.main_filter,
            'parser': self.default_parser,
            'set_header': self.set_header
        }[kind]

    def _crawl(self, root, pattern, filter, parser, set_header, action, context, recursive, refresh):
        print('_crawl:root', root)

        linkstack = SetStack([(root, self.get_header())])
        visited = set()
        while linkstack:
            root, headers = linkstack.pop()
            response = self.get(root, headers=headers, refresh=refresh)
            for link in self._parse_link(response, pattern):
                if link not in visited:
                    visited.add(link)
                    match = pattern.match(link).group

                    if not self.main_filter(link, match, context=context):
                        continue
                    if filter(link, match, context=context):
                        location = abs_path(self.ROOT_URL, link)
                        hdr = set_header(location, root, headers)
                        rsp = self.get(link, headers=hdr, refresh=refresh)
                        if isinstance(action, Source):
                            soup = None
                        else:
                            soup = self._get_soup(rsp.content)
                        if recursive:
                            linkstack.push((link, hdr))
                        yield link, parser(rsp, match, soup, context=context)

    def scrap(self, context=None, until=None):
        results = defaultdict(list)
        urls = []

        def set_header(l, p, h):
            return self.get_header()
        for act in self.SCRAP_RELAY:
            next_urls = []
            name = act.name
            refresh = act.refresh
            recursive = act.recursive
            filter = self._get_method(act.filter, 'filter')
            parser = self._get_method(act.parser, 'parser')
            set_header = self._get_method(act.set_header, 'set_header')
            # print('scrap:filter', filter)
            if isinstance(act, Location):
                urls.append(act.url)
                hdr = set_header(act.url, act.url, self.get_header())
                response = self.get(act.url, hdr, refresh)
                match = re.compile(act.url).match(act.url).group
                soup = self._get_soup(response.content)
                parsed = parser(response, match, soup, context=context)
                self.reducer(parsed, name, results)
                continue
                pattern = act.url
            else:
                pattern = act.pattern

            for url in urls:
                for link, parsed in self._crawl(url, pattern, filter, parser, set_header, act, context=context, recursive=recursive, refresh=refresh):
                    # print('scrp:link', link)
                    self.reducer(parsed, name, results)
                    if not isinstance(act, Source):
                        next_urls.append(link)

            if not isinstance(act, Source):
                urls = next_urls
        return results

    def reducer(self, parsed, name, results):
        if parsed is None:
            return
        if isinstance(parsed, (str, bytes)):
            results[name].append(parsed)
        elif isinstance(parsed, abc.Mapping):
            results[name].append(parsed)
        elif isinstance(parsed, abc.Iterable):
            results[name].extend(list(parsed))

    def default_parser(self, response, match, soup, context=None):
        return

    def main_filter(self, link, match, context=None):
        return True

    def set_headers(self, location, previous, headers):
        return headers
