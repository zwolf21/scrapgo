import re
import mimetypes
from functools import lru_cache
from collections import abc, UserDict

from scrapgo.utils.urlparser import queryjoin, parse_src
from scrapgo.lib.data_structure.hashable import kwargs2hashable
from scrapgo.lib.data_structure import SetStack
from scrapgo.utils.shortcuts import abs_path
from scrapgo.modules import CachedRequests, SoupParserMixin


class RequestsSoupCrawler(SoupParserMixin, CachedRequests):
    ROOT_URL = None

    def __init__(self, url=None, params=None, **kwargs):
        self.ROOT_URL = queryjoin(url or self.ROOT_URL, params)
        super().__init__(**kwargs)

    @kwargs2hashable
    @lru_cache(maxsize=128)
    def get(self, link, refresh=False, **kwargs):
        url = abs_path(self.ROOT_URL, link)
        r = self._get(url, refresh=refresh, **kwargs)
        return r

    def _crawl(self, root, pattern, filter, parser, set_header, context, recursive, refresh):
        linkstack = SetStack([(root, self.get_header())])
        visited = set()
        first = True
        while linkstack:
            root, headers = linkstack.pop()
            response = self.get(root, headers=headers, refresh=refresh)
            if first:
                previous = response.url
                first = False

            for link in self._parse_link(response, pattern):
                if link not in visited:
                    visited.add(link)
                    match = pattern.match(link).group
                    if not self.main_filter(link, match, context=context):
                        continue
                    if filter(link, match, context=context):
                        location = abs_path(self.ROOT_URL, link)
                        hdr = set_header(location, previous, headers)
                        rsp = self.get(link, headers=hdr, refresh=refresh)
                        setattr(rsp, 'referer', previous)
                        src = parse_src(link)
                        content_type = mimetypes.guess_type(src)[0]
                        if content_type and 'image' in content_type:
                            soup = rsp.content
                        else:
                            soup = self._get_soup(rsp.content)
                        if recursive:
                            linkstack.push((link, hdr))
                        yield link, parser(rsp, match, soup, context=context)
