from collections import abc, defaultdict
from itertools import chain

from scrapgo.utils.shortcuts import parse_query, parse_path, filter_params, abs_path
from scrapgo.modules import CachedRequests, SoupParserMixin
from scrapgo.lib.history import HistoryDict
from .crawler import RequestsSoupCrawler
from .action import *


class LinkRelayScraper(ActionContainer, RequestsSoupCrawler):
    LOGIN_URL = None

    def __init__(self, login_data=None, **kwargs):
        super().__init__(**kwargs)

    def login(self, login_data):
        url = self.LOGIN_URL or self.ROOT_URL
        r = self.post(url, data=login_data, refresh=True)

    def reducer(self, parsed, name, results):
        if parsed is None:
            return
        if isinstance(parsed, (str, bytes)):
            results[name].append(parsed)
        elif isinstance(parsed, abc.Mapping):
            results[name].append(parsed)
        elif isinstance(parsed, abc.Iterable):
            results[name].extend(list(parsed))

    def scrap(self, root_params=None, context=None, until=None, _response=None, _link_relay=None, _results=None, crawl_style='depth'):
        self.context = context or {}
        self.root_params = root_params
        if crawl_style == 'depth':
            _results = _results or defaultdict(list)
            action, *rest_relay = _link_relay or self.LINK_RELAY
            for response in self._handle_actions(action, _response, context, _results):
                if until is not None and until == action.name:
                    return
                if rest_relay:
                    self.scrap(root_params, context, until,
                               response, rest_relay, _results, crawl_style)
            return _results
        else:
            return self._relay_actions(
                self._handle_actions,
                context,
                until
            )

    def _handle_actions(self, action, response, context, results):
        # print('_handle_action:', self.history)
        if response is None:
            response = self.get(self.ROOT_URL, refresh=True)
            previous = None
        else:
            previous = response.url

        kwargs = {
            'response': response,
            'context': context,
            'filter': action.filter,
            'parser': action.parser,
            'refresh': action.refresh,
            'referer': self.find_referer(action, response),
            'fields': action.fields
        }
        if isinstance(action, (Root, Url)):
            if action.url == '/':
                action.url = self.ROOT_URL
            url = action.set_params(
                response, action.url, self.root_params, context)
            if isinstance(url, str):
                patterns = [url]
            else:
                patterns = list(url)
        elif isinstance(action, RegexUrl):
            patterns = [action.regex]
            kwargs['recursive'] = action.recursive
        elif isinstance(action, FormatUrl):
            patterns = action.formater(action.template, context=context)
            if isinstance(patterns, str):
                patterns = [patterns]
            patterns = list(patterns)
        else:
            patterns = [action.url]

        next_responses = []
        for pattern in patterns:
            kwargs['pattern'] = pattern
            for rsp, parsed in self._crawl(**kwargs):
                action.urls.append(rsp.url)
                self.history.set_history(rsp.url, previous, action.name)
                self.reducer(parsed, action.name, results)
                if not self._is_parsable(rsp):
                    action.static = True
                else:
                    yield rsp

        if action.static == True:
            yield response

    # def find_referer(self, action, response):
    #     if response is None:
    #         return self.ROOT_URL
    #     if not action.referer or not hasattr(response, 'trace'):
    #         return
    #     referer_actions = self.get_action(action.referer, many=True)
    #     trace_url = set(response.trace)
    #     trace_link = set(map(parse_path, response.trace))
    #     urls = set(chain(*(a.urls for a in referer_actions)))
    #     url = trace_url & urls | trace_link & urls
    #     if url:

    def find_referer(self, action, response):
        if response is None:
            return self.ROOT_URL
        url = self.history.get_previous(response.url, action.referer)
        if url:
            return filter_params(url, response.fields)
        return self.ROOT_URL
