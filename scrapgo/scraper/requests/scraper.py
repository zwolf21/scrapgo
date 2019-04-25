from collections import abc, defaultdict, deque, namedtuple
from itertools import chain
import re

from scrapgo.utils.shortcuts import *
from scrapgo.modules import CachedRequests, SoupParserMixin
from scrapgo.lib.history import HistoryDict
from .action.actions import Root, Url


ResponseMeta = namedtuple(
    'ResponseMeta', ['match', 'query', 'soup', 'history', 'context'])


class LinkRelayScraper(SoupParserMixin, CachedRequests):
    ROOT_URL = None
    LOGIN_URL = None
    LINK_RELAY = None

    def __init__(self, url=None, root_params=None, **kwargs):
        super().__init__(**kwargs)
        self.ROOT_URL = queryjoin(url or self.ROOT_URL, root_params)
        self.history = HistoryDict()
        self.LINK_RELAY = self.LINK_RELAY or []

    def _set_history(self, url, previous, name):
        url = abs_path(self.ROOT_URL, url)
        self.history.set_history(url, previous, name)

    def _parse_query_match(self, link, pattern=None):
        match = None
        query = parse_query(link)
        if pattern is not None and isinstance(pattern, re.Pattern):
            match = pattern.match(link).group
        return match, query

    def _set_response_meta(self, response, link, pattern=None, parent_response=None):
        match, query = self._parse_query_match(link, pattern)
        soup = self._get_soup(response)
        if parent_response is not None:
            context = parent_response.context
        else:
            context = {}
        meta = ResponseMeta(match, query, soup, self.history, context)
        setattr(response, 'scrap', meta)

    def _link_filter(self, link, pattern=None, filter=None, **kwargs):
        match, query = self._parse_query_match(link, pattern)
        if not self.main_filter(link, query, match, **kwargs):
            return False
        if filter:
            if not filter(link, query, match, **kwargs):
                return False
        return True

    def _set_referer(self, link, referer=None):
        header = self.get_header()
        if referer:
            previous = self.history.get_previous(link, referer)
            header['Referer'] = previous
        return header

    def _get_method(self, func, kind):
        if callable(func):
            return func
        if isinstance(func, str):
            if hasattr(self, func):
                return getattr(self, func)

        return {
            'filter': self.main_filter,
            'parser': self.default_parser,
            'previewer': self.url_previewer,
            'generator': self.query_generator,
            'breaker': self.crawl_breaker
        }[kind]

    def _crawl_link_pattern(self, parent_response, action, results, **kwargs):
        visited = set()
        responses = deque([parent_response])
        parent_url = parent_response.url
        parser = self._get_method(action.parser, 'parser')
        breaker = self._get_method(action.breaker, 'breaker')
        isbreak = False
        while responses:
            if isbreak:
                break
            r = responses.pop()
            for link in self._parse_link(r, action.regex):
                if link not in visited:
                    visited.add(link)
                    filtered = self._link_filter(
                        link=link,
                        pattern=action.regex,
                        filter=action.filter,
                        **kwargs
                    )
                    if not filtered:
                        continue
                    self._set_history(link, parent_url, action.name)
                    headers = self._set_referer(link, action.referer)
                    res = self.get(
                        link=link,
                        headers=headers,
                        refresh=action.refresh,
                        fields=action.fields
                    )
                    self._set_response_meta(res, link, action.regex)
                    parsed = parser(res, **kwargs)
                    self.reducer(parsed, action.name, results)
                    if action.recursive == True:
                        responses.append(res)
                    if self._is_parsable(res):
                        yield res
                    else:
                        if action.static == False:
                            action.static = True
                    isbreak = breaker(res, **kwargs)
                    if isbreak:
                        break

        if action.static == True:
            yield parent_response

    def _visited_links(self, links, parent_response, action, results, **kwargs):
        if isinstance(links, (str, abc.Mapping)):
            links = [links]

        if parent_response is None:
            parent_url = None
        else:
            parent_url = parent_response.url

        parser = self._get_method(action.parser, 'parser')
        breaker = self._get_method(action.breaker, 'breaker')

        for link in links:
            if isinstance(link, (abc.Mapping)):
                link = queryjoin(action.url, link)
            if self._link_filter(link, **kwargs):
                self._set_history(link, parent_url, action.name)
                headers = self._set_referer(link, action.referer)
                res = self.get(
                    link=link,
                    headers=headers,
                    refresh=action.refresh,
                    fields=action.fields
                )
                self._set_response_meta(res, link)
                parsed = parser(res, **kwargs)
                self.reducer(parsed, action.name, results)
                if self._is_parsable(res):
                    yield res
                else:
                    if action.static == False:
                        action.static = True
                if breaker(res, **kwargs):
                    break

        if action.static == True:
            yield parent_response

    def _handle_action(self, action, parent_response=None, results=None, **kwargs):
        if parent_response is None:
            parent_response = self.get(self.ROOT_URL, refresh=True)
            self._set_response_meta(parent_response, parent_response.url,)
            self._set_history(self.ROOT_URL, None, 'root')

        if isinstance(action, (Root, Url)):
            if isinstance(action, Root):
                if action.url == '/':
                    links = self.ROOT_URL
                else:
                    links = action.url
            elif isinstance(action, Url):
                generator = self._get_method(action.generator, 'generator')
                links = []
                if action.previewer:
                    lnks = []
                    previewer = self._get_method(action.previewer, 'previewer')
                    prev_urls = previewer(
                        parent_response, action.url, **kwargs)
                    prev_responses = self._visited_links(prev_urls)
                    for prev_res in prev_responses:
                        lnk = generator(prev_res, action.url, **kwargs)
                        links.append(lnk)
                    links = chain(*links)
                links = generator(parent_response, action.url, **kwargs)
            responses = self._visited_links(
                links=links,
                parent_response=parent_response,
                action=action,
                results=results,
                **kwargs
            )
        else:
            responses = self._crawl_link_pattern(
                parent_response=parent_response,
                action=action,
                results=results,
                **kwargs
            )
        return responses

    def get(self, link, **kwargs):
        url = abs_path(self.ROOT_URL, link)
        response = self._get(url, **kwargs)
        return response

    def post(self, url, **kwargs):
        response = self._post(url, **kwargs)
        return response

    def login(self, login_data):
        url = self.LOGIN_URL or self.ROOT_URL
        r = self.post(url, data=login_data, refresh=True)

    def scrap(self, until=None, _response=None, _relay=None, _results=None, **kwargs):
        _results = _results or defaultdict(list)
        action, *rest = _relay or self.LINK_RELAY
        responses = self._handle_action(
            action=action,
            parent_response=_response,
            results=_results,
            **kwargs
        )
        for response in responses:
            if until is not None and until == action.name:
                return
            if rest:
                self.scrap(
                    until=until,
                    _response=response,
                    _relay=rest,
                    _results=_results,
                    **kwargs
                )
        return _results

    def reducer(self, parsed, name, results):
        if parsed is None:
            return
        if isinstance(parsed, (str, bytes)):
            results[name].append(parsed)
        elif isinstance(parsed, abc.Mapping):
            results[name].append(parsed)
        elif isinstance(parsed, abc.Iterable):
            results[name].extend(list(parsed))

    def get_action(self, name, many=False):
        actions = []
        for action in self.LINK_RELAY:
            if action.name == name:
                if many == False:
                    return action
                else:
                    actions.append(action)
        if actions:
            return actions
        raise ValueError('Invalid name: {}'.format(name))

    def main_filter(self, link, query, match, **kwargs):
        return True

    def default_parser(self, response, **kwargs):
        return []

    def query_generator(self, parent_response, path, **kwargs):
        yield path

    def url_previewer(self, parent_response, path, **kwargs):
        yield path

    def crawl_breaker(self, response, **kwargs):
        return False
