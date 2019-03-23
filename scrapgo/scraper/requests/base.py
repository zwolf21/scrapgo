import re
import mimetypes

from scrapgo.lib.data_structure import SetStack
from scrapgo.utils.shortcuts import abs_path
from scrapgo.modules import CachedRequests, SoupParserMixin


class RequestsSoupCrawler(SoupParserMixin, CachedRequests):
    ROOT_URL = None

    def __init__(self, *args, url=None, **kwargs):
        self.ROOT_URL = url or self.ROOT_URL
        self.visited_cache = {}
        super().__init__(*args, **kwargs)

    def get(self, link, headers=None, refresh=False):
        url = abs_path(self.ROOT_URL, link)
        if url in self.visited_cache:
            return self.visited_cache[url]
        r = self._get(url, headers, refresh)
        self.visited_cache[url] = r
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
                        content_type = mimetypes.guess_type(link)[0]
                        if content_type and 'image' in content_type:
                            soup = None
                        else:
                            soup = self._get_soup(rsp.content)
                        if recursive:
                            linkstack.push((link, hdr))
                        yield link, parser(rsp, match, soup, context=context)
