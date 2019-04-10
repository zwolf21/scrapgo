import time

import requests
import requests_cache
from fake_useragent import FakeUserAgent

from scrapgo import settings
from scrapgo.lib.time.time import get_random_second


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

    def _get(self, url, headers=None, refresh=False, **kwargs):
        headers = headers or self.headers
        if refresh:
            if self.requests.cache.has_url(url):
                self.requests.cache.delete_url(url)
        r = self.requests.get(url, headers=headers, **kwargs)
        r.raise_for_status()

        if r.from_cache == False:
            delay = self._get_delay()
            time.sleep(delay)
            print('get {} from_cache: {} (delay:{}s)'.format(
                url, r.from_cache, delay))
        else:
            print('get {} from_cache: {}'.format(url, r.from_cache))

        if not r.content:
            self.requests.cache.delete_url(url)
            print('Warning: {} has no content!'.format(r.url))
        return r

    def _post(self, url, data, headers=None, refresh=True, **kwargs):
        headers = headers or self.headers
        if refresh:
            if self.requests.cache.has_url(url):
                print('Delete Cached:',  url)
                self.requests.cache.delete_url(url)
        r = self.requests.post(url, data=data, headers=headers, **kwargs)
        print('post {}'.format(url))
        r.raise_for_status()
        return r

    def _get_delay(self):
        if isinstance(self.REQUEST_DELAY, (tuple, list,)) and len(self.REQUEST_DELAY) == 2:
            return get_random_second(*self.REQUEST_DELAY)
        return self.REQUEST_DELAY

    def get_header(self):
        return self.headers.copy()

    def set_header(self, headers):
        self.headers = headers
