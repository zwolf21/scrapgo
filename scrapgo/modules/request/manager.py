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
                 request_header=REQUEST_HEADER, cache_name=settings.CACHE_NAME,
                 cache_backend=settings.CACHE_BACKEND, cache_expiration=settings.CACHE_EXPIRATION,
                 use_request_cache=True, use_session=True, **kwargs):
        super().__init__(**kwargs)
        self.request_header = request_header

        if use_request_cache:
            requests_cache.install_cache(
                cache_name=cache_name, backend=cache_backend, expire_after=cache_expiration)
        self.requests = requests
        if use_session:
            self.requests = requests.Session()

    def _get(self, url, cache=True, headers=None, **kwargs):
        headers = headers or self.request_header
        if cache == True:
            return self.requests.get(url, headers=headers, **kwargs)
        with requests_cache.disabled():
            print('manager.py:disable_cache', url)
            return self.requests.get(url, headers=headers, **kwargs)

    def _post(self, url, headers=None, data=None, **kwargs):
        headers = headers or self.request_header
        return self.requests.post(url, data, headers=headers, **kwargs)
