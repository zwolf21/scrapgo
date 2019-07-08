import os
from urllib.parse import quote, quote_plus

from scrapgo import LinkRelayScraper


class BaseScraper(LinkRelayScraper):
    CACHE_NAME = 'CODINGFORENTREPRENEURS_CACHE'
    REQUEST_DELAY = 0
    RETRY_INTERVAL_SECONDS = 1, 2,
