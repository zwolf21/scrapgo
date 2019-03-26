import re
import mimetypes

from scrapgo.utils.urlparser import queryjoin, parse_src, parse_query
from scrapgo.lib.data_structure import SetStack
from scrapgo.utils.shortcuts import abs_path
from scrapgo.modules import CachedRequests, SoupParserMixin


class RequestsSoupCrawler(SoupParserMixin, CachedRequests):
    ROOT_URL = None

    def __init__(self, url=None, params=None, **kwargs):
        super().__init__(**kwargs)
        self.ROOT_URL = queryjoin(url or self.ROOT_URL, params)

    def get(self, link, refresh=False, **kwargs):
        url = abs_path(self.ROOT_URL, link)
        return self._get(url, refresh=refresh, **kwargs)

    def _crawl(self, response, pattern, filter, parser, set_header, context, recursive, refresh):
        linkstack = SetStack([response])
        visited = set()
        first = True
        while linkstack:
            response = linkstack.pop()
            if first:
                previous = response.url
                first = False

            for link in self._parse_link(response, pattern):
                if link not in visited:
                    visited.add(link)
                    match = pattern.match(link).group
                    query = parse_query(link)
                    if not self.main_filter(link, query, match, context=context):
                        continue
                    if filter(link, query, match, context=context):
                        location = abs_path(self.ROOT_URL, link)
                        headers = set_header(
                            location, previous, self.get_header())
                        rsp = self.get(link, headers=headers, refresh=refresh)
                        setattr(rsp, 'referer', previous)
                        src = parse_src(link)
                        content_type = mimetypes.guess_type(src)[0]
                        if content_type and 'image' in content_type:
                            soup = rsp.content
                        else:
                            soup = self._get_soup(rsp.content)
                        if recursive:
                            linkstack.push(rsp)
                        yield rsp, parser(rsp, match, soup, context=context)
