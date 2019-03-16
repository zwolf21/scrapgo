import requests
import requests_cache
from requests_cache.backends.base import BaseCache
from fake_useragent import FakeUserAgent

from scrapgo import settings


REQUEST_HEADER = {
    'User-Agent': getattr(FakeUserAgent(), settings.USER_AGENT)
}


class RequestsManager(object):

    def __init__(self,
                 headers=REQUEST_HEADER, cache_name=settings.CACHE_NAME,
                 cache_backend=settings.CACHE_BACKEND, cache_expiration=settings.CACHE_EXPIRATION,
                 use_request_cache=True, **kwargs):
        self.headers = headers

        if use_request_cache:
            s = requests_cache.CachedSession(
                cache_name=cache_name, backend=cache_backend, expire_after=cache_expiration)
        else:
            s = requests.Session()
        self.requests = s

    def _get(self, url, cache=True, headers=None, **kwargs):
        headers = headers or self.headers
        print('Requestmanager._get:url', url)
        print('Requestmanager._get:headers', headers, '\n')
        if cache == True:
            r = self.requests.get(url, headers=headers, **kwargs)
        else:
            with self.requests.cache_disabled():
                print('manager.py:disable_cache', url)
                r = self.requests.get(url, headers=headers, **kwargs)
        r.raise_for_status()
        return r

    def _post(self, url, headers=None, data=None, **kwargs):
        headers = headers or self.headers
        return self.requests.post(url, data, headers=headers, **kwargs)

    def get_header(self):
        return self.headers.copy()
