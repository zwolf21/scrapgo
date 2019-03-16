import re
from collections import namedtuple

from bs4 import BeautifulSoup

from scrapgo import settings


class SoupParserMixin(object):

    def __init__(self, parser=settings.BEAUTIFULSOUP_PARSER, **kwargs):
        super().__init__(**kwargs)
        self.parser = parser

    def _get_soup(self, content):
        return BeautifulSoup(content, self.parser)

    def _parse_link(self, response, link_pattern, attrs=settings.SCRAP_TARGET_ATTRS):
        soup = self._get_soup(response.content)
        parsed = set()
        pattern = re.compile(link_pattern)
        for attr in attrs:
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
