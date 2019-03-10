import requests
import requests_cache
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

    def _get(self, url, params=None):
        return self.requests.get(url, params=params, headers=self.request_header)

    def _post(self, url, data=None):
        return self.requests.post(url, data, headers=self.request_header)
