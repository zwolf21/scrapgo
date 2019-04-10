import re
from collections import deque

from scrapgo.utils.urlparser import queryjoin, parse_src, parse_query, filter_params
from scrapgo.utils.shortcuts import abs_path
from scrapgo.modules import CachedRequests, SoupParserMixin


class RequestsSoupCrawler(SoupParserMixin, CachedRequests):
    ROOT_URL = None

    def __init__(self, url=None, params=None, **kwargs):
        super().__init__(**kwargs)
        self.ROOT_URL = queryjoin(url or self.ROOT_URL, params)

    def get(self, link, refresh=False, previous=None, fields=None, **kwargs):
        url = abs_path(self.ROOT_URL, link)
        raw_url = url  # 사이트에서 사용중인 가공되지 않은 url
        if fields is not None:  # url 가공
            url = filter_params(url, fields)
        r = self._get(url, refresh=refresh, **kwargs)
        setattr(r, 'raw_url', raw_url)
        setattr(r, 'fields', fields)
        # trace, referer 설치
        if previous:
            setattr(r, 'previous', previous.url)
            if not hasattr(previous, 'trace'):
                setattr(previous, 'trace', [self.ROOT_URL])
            setattr(r, 'trace', [raw_url])
            r.trace += previous.trace
        else:
            setattr(r, 'previous', self.ROOT_URL)
        return r

    def post(self, url, data, refresh=False, referer=None, **kwargs):
        headers = self.get_header()
        if referer is not None:
            headers['Referer'] = referer
        r = self._post(url, data, headers=headers, refresh=refresh, **kwargs)
        return r

    def _crawl(self, response, pattern, filter, parser, context=None, recursive=False, refresh=False, referer=None, fields=None):
        linkstack = deque([response])
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
                    if isinstance(pattern, re.Pattern):
                        match = pattern.match(link).group
                    else:
                        match = None
                    query = parse_query(link)
                    if not self.main_filter(link, query, match, context=context):
                        continue
                    if filter(link, query, match, context=context):
                        location = abs_path(self.ROOT_URL, link)
                        headers = self.get_header()
                        if referer is not None:
                            headers['Referer'] = referer
                        rsp = self.get(
                            link,
                            headers=headers,
                            refresh=refresh,
                            previous=response,
                            fields=fields
                        )
                        soup = self._get_soup(rsp)
                        if recursive and soup is not None:
                            linkstack.append(rsp)
                        yield rsp, parser(rsp, match, soup, context=context)
