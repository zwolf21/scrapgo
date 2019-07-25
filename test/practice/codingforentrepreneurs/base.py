import os
from urllib.parse import quote, quote_plus

from scrapgo import LinkRelayScraper
from scrapgo.utils.fileutils import cp
from .logger import logger


class BaseScraper(LinkRelayScraper):
    CACHE_NAME = 'CODINGFORENTREPRENEURS_CACHE'
    REQUEST_DELAY = 0
    RETRY_INTERVAL_SECONDS = 1, 2,

    def _save_media(self, url, save_to, overwrite=False):
        if overwrite is False:
            if os.path.exists(save_to):
                return
        try:
            r = self._get(url)
        except:
            logger.error(save_to)
        else:
            cp(r.content, save_to)
