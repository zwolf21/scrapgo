import re
from collections import namedtuple

from bs4 import BeautifulSoup

from scrapgo.utils.shortcuts import parse_src
from scrapgo import settings


def is_parsable(response, allowed_content_types=settings.PARSE_CONTENT_TYPES):
    content_type_info = response.headers.get('Content-Type')
    if content_type_info:
        for ctype in allowed_content_types:
            if ctype in content_type_info:
                return True
    return False


class SoupParserMixin(object):
    SCRAP_TARGET_ATTRS = settings.SCRAP_TARGET_ATTRS
    PARSE_CONTENT_TYPES = settings.PARSE_CONTENT_TYPES

    def __init__(self, parser=settings.BEAUTIFULSOUP_PARSER, **kwargs):
        super().__init__(**kwargs)
        self.parser = parser

    def _is_parsable(self, response):
        content_type_info = response.headers.get('Content-Type')
        if not content_type_info:
            return False
        for ctype in self.PARSE_CONTENT_TYPES:
            if ctype in content_type_info:
                return True
        return False

    def _get_soup(self, response):
        if self._is_parsable(response):
            content = response.content
            return BeautifulSoup(content, self.parser)
        return BeautifulSoup('', self.parser)

    def _parse_link(self, response, link_patterns):
        soup = self._get_soup(response)
        parsed = set()

        if not isinstance(link_patterns, (list, tuple, set)):
            link_patterns = [link_patterns]

        for pattern in link_patterns:
            if isinstance(pattern, str):
                yield pattern
            else:
                for attr in self.SCRAP_TARGET_ATTRS:
                    for link in soup('', {attr: pattern}):
                        if link not in parsed:
                            parsed.add(link[attr])
                            yield link[attr]

    def find_texts(self, soup, *args, **kwargs):
        ret = []
        for tag in soup(*args, **kwargs):
            text = tag.text or ''
            ret.append(text.strip())
        return ret
