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
                 use_request_cache=True, use_session=True, **kwargs):
        self.headers = headers

        if use_request_cache:
            requests_cache.install_cache(
                cache_name=cache_name, backend=cache_backend, expire_after=cache_expiration, **kwargs)
        self.requests = requests
        if use_session:
            self.requests = requests.Session()

    def _get(self, url, cache=True, headers=None, **kwargs):
        headers = headers or self.headers
        print('Requestmanager._get:url', url)
        print('Requestmanager._get:headers', headers, '\n')
        if cache == True:
            return self.requests.get(url, headers=headers, **kwargs)
        with requests_cache.disabled():
            print('manager.py:disable_cache', url)
            return self.requests.get(url, headers=headers, **kwargs)

    def _post(self, url, headers=None, data=None, **kwargs):
        headers = headers or self.headers
        return self.requests.post(url, data, headers=headers, **kwargs)

    def get_header(self):
        return self.headers.copy()
