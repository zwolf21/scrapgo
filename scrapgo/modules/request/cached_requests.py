import time

import requests
import requests_cache
from fake_useragent import FakeUserAgent

from scrapgo import settings
from scrapgo.lib.time.time import get_random_second
from scrapgo.utils.shortcuts import filter_params


class CachedRequests(object):
    USER_AGENT_NAME = settings.USER_AGENT_NAME  # default to 'chrome'
    HEADERS = None
    REQUEST_DELAY = settings.REQUEST_DELAY
    CACHE_NAME = settings.CACHE_NAME
    CACHE_BACKEND = settings.CACHE_BACKEND
    CACHE_EXPIRATION = settings.CACHE_EXPIRATION
    CACHE_METHODS = settings.CACHE_METHODS

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.headers = {
            'User-Agent': getattr(FakeUserAgent(), self.USER_AGENT_NAME)
        }
        if self.HEADERS:
            self.headers.update(self.HEADERS)

        self.requests = requests_cache.CachedSession(
            cache_name=self.CACHE_NAME,
            backend=self.CACHE_BACKEND,
            expire_after=self.CACHE_EXPIRATION,
            allowable_methods=self.CACHE_METHODS
        )

    def _refresh_cache(self, url, method='get'):
        if method == 'get':
            if self.requests.cache.has_url(url):
                self.requests.cache.delete_url(url)
        else:
            self.requests.remove_expired_responses()

    def _delay_control(self, response, payloads=None):
        if response.from_cache == False:
            delay = self._get_delay()
            time.sleep(delay)
            if payloads is not None:
                log = 'POST {} from cache=={} (delay:{}s, payloads:{})'
                print(log.format(response.url, response.from_cache, delay, payloads))
            else:
                log = 'GET {} from cache=={} (delay:{}s, payloads:{})'
                print(log.format(response.url, response.from_cache, delay))
        else:
            if payloads is not None:
                log = 'POST {} from_cache=={} (payloads:{})'
                print(log.format(response.url, response.from_cache, payloads))
            else:
                log = 'GET {} from_cache=={}'
                print(log.format(response.url, response.from_cache))

    def _get_delay(self):
        if isinstance(self.REQUEST_DELAY, (tuple, list,)) and len(self.REQUEST_DELAY) == 2:
            return get_random_second(*self.REQUEST_DELAY)
        return self.REQUEST_DELAY

    def _validate_response(self, response):
        if not response.content:
            self.requests.cache.delete_url(url)
            print('Warning: {} has no content!'.format(response.url))

    def _get(self, url, headers=None, refresh=False, fields=None):
        headers = headers or self.get_header()
        url = filter_params(url, fields)
        if refresh:
            self._refresh_cache(url)

        r = self.requests.get(url, headers=headers)
        r.raise_for_status()
        self._delay_control(r)
        self._validate_response(r)
        return r

    def _post(self, url, payload, headers=None, refresh=True, fields=None):
        headers = headers or self.headers
        url = filter_params(url, fields)
        r = self.requests.post(url, data=payload, headers=headers)
        r.raise_for_status()
        self._delay_control(r, payloads=len(payload))
        return r

    def get_header(self):
        return dict(self.headers)

    def set_header(self, headers):
        self.headers = headers
