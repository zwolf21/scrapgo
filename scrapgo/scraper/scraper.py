import re
from collections import namedtuple, abc

from .base import BaseScraper
from scrapgo.modules import SoupParserMixin

Link = namedtuple(
    'Link', 'pattern urlfilter parser name recursive'
)

Location = namedtuple('Location', 'url parser name')

Source = namedtuple('Source', 'pattern, urlfilter parser name')


def location(url, parser, name=None):
    return Location(url, parser, name or url)


def href(pattern, urlfilter=None, parser=None, name=None, recursive=False):
    regx = re.compile(pattern)
    return Link(
        regx,
        urlfilter,
        parser,
        name or pattern,
        recursive,
    )


def src(pattern, urlfilter=None, parser=None, name=None):
    regx = re.compile(pattern)
    return Source(
        regx,
        urlfilter,
        parser,
        name or pattern
    )


class Scraper(BaseScraper):
    LINK_ROUTER = None

    def __init__(self, *args, **kwargs):
        super().__init__(*args, **kwargs)
        loc = location(self.ROOT_URL, self.default_parser, self.ROOT_URL)
        if not self.LINK_ROUTER:
            self.LINK_ROUTER = [loc]
        if not isinstance(self.LINK_ROUTER[0], Location):
            self.LINK_ROUTER.insert(0, loc)

    def get_link_pattern(self, name):
        for step in self.LINK_ROUTER:
            if step.name == name:
                return step.pattern

    def scrap(self, context=None, until=None):
        self.scrap_results = {}
        urls = []
        for step in self.LINK_ROUTER:
            next_urls = []
            name = step.name
            parser = self._get_fuction(step.parser, 'parser')
            if isinstance(step, Location):
                url = self.ROOT_URL if step.url == '/' else step.url
                r = self._get(url)
                soup = self._get_soup(r.content)
                parsed = parser(url, re.compile(url).match(url), soup=soup)
                self.reducer(parsed, name)
                next_urls.append(url)
            elif isinstance(step, Link):
                pattern = step.pattern
                urlfilter = self._get_fuction(step.urlfilter)
                recursive = step.recursive
                for url in urls:
                    for link in self._scrap_links(url, pattern, urlfilter, context, recursive):
                        r = self._get(link)
                        parsed = parser(
                            link, pattern.match(link).group, soup=self._get_soup(r.content))
                        self.reducer(parsed, name)
                        next_urls.append(link)
            else:
                pattern = step.pattern
                urlfilter = self._get_fuction(step.urlfilter)
                for url in urls:
                    for src in self._scrap_links(url, pattern, urlfilter, context):
                        r = self._get(src)
                        parsed = parser(src, pattern.match(
                            src).group, content=r.content)
                        self.reducer(parsed, name)
                continue
            if until is not None and until == name:
                break
            urls = next_urls
        return self.scrap_results

    def reducer(self, parsed, name):
        if parsed is None:
            return
        if isinstance(parsed, (str, bytes)):
            return self.scrap_results.setdefault(name, []).append(parsed)
        elif isinstance(parsed, abc.Mapping):
            return self.scrap_results.setdefault(name, []).append(parsed)
        elif isinstance(parsed, abc.Iterable):
            return self.scrap_results.setdefault(name, []).extend(list(parsed))
        return parsed
