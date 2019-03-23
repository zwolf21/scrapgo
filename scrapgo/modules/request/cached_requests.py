import requests
import requests_cache
from requests_cache.backends.base import BaseCache
from fake_useragent import FakeUserAgent

from scrapgo import settings


class CachedRequests(object):
    USER_AGENT_NAME = settings.USER_AGENT_NAME  # default to 'chrome'
    CACHE_NAME = settings.CACHE_NAME
    CACHE_BACKEND = settings.CACHE_BACKEND
    CACHE_EXPIRATION = settings.CACHE_EXPIRATION

    def __init__(self, **kwargs):
        super().__init__(**kwargs)
        self.headers = {
            'User-Agent': getattr(FakeUserAgent(), self.USER_AGENT_NAME)
        }

        self.requests = requests_cache.CachedSession(
            cache_name=self.CACHE_NAME,
            backend=self.CACHE_BACKEND,
            expire_after=self.CACHE_EXPIRATION
        )

    def _get(self, url, headers=None, refresh=False):
        headers = headers or self.headers
        if refresh:
            if self.requests.cache.has_url(url):
                # print('CachedRequests._get:url=(from_cached)', url)
                self.requests.cache.delete_url(url)
        r = self.requests.get(url, headers=headers)
        r.raise_for_status()
        return r

    def _post(self, url, headers=None, data=None, **kwargs):
        headers = headers or self.headers
        return self.requests.post(url, data, headers=headers, **kwargs)

    def get_header(self):
        return self.headers.copy()

    def set_header(self, headers):
        self.headers = headers
