import time

import requests
import requests_cache
from requests_cache.backends.base import BaseCache
from fake_useragent import FakeUserAgent

from scrapgo import settings


class CachedRequests(object):
    USER_AGENT_NAME = settings.USER_AGENT_NAME  # default to 'chrome'
    HEADERS = None
    REQUEST_DELAY = settings.REQUEST_DELAY
    CACHE_NAME = settings.CACHE_NAME
    CACHE_BACKEND = settings.CACHE_BACKEND
    CACHE_EXPIRATION = settings.CACHE_EXPIRATION

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
            expire_after=self.CACHE_EXPIRATION
        )

    def _get(self, url, params=None, headers=None, refresh=False):
        headers = headers or self.headers
        if refresh:
            if self.requests.cache.has_url(url):
                self.requests.cache.delete_url(url)
                # print('CachedRequests._get:url=(from_cached:False)', url)
        r = self.requests.get(url, params=params, headers=headers)
        r.raise_for_status()
        # print('CachedRequests._get:from_cached', r.from_cache, url)
        if r.from_cache == False:
            time.sleep(self.REQUEST_DELAY)
        if not r.content:
            self.requests.cache.delete_url(url)
            # print('CachedRequests._get:no_content!', r.url)
        return r

    def _post(self, url, headers=None, data=None, **kwargs):
        headers = headers or self.headers
        return self.requests.post(url, data=data, headers=headers, **kwargs)

    def get_header(self):
        return self.headers.copy()

    def set_header(self, headers):
        self.headers = headers
