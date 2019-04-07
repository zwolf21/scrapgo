import os
from urllib.parse import unquote

from scrapgo.scraper import LinkRelayScraper, urlpattern
from scrapgo import settings
from scrapgo.utils.shortcuts import mkdir_p, cp
from scrapgo.modules.output.render import ImageReferer, render_img2referer


class NaverKinScraper(LinkRelayScraper):
    ROOT_URL = 'https://kin.naver.com/search/list.nhn'
    SCRAP_TARGET_ATTRS = settings.SCRAP_TARGET_ATTRS + ('content', )

    LINK_RELAY = [
        urlpattern(
            r'^/search/list.nhn\?query=(?P<query>.+)&page=(?P<page>.+)$',
            parser='list_parser',
            name='list'
        ),
        urlpattern(
            r'^https://kin.naver.com/qna/detail.nhn\?d1id=(?P<d1id>\d+)&dirId=(?P<dirId>\d+)&docId=(?P<docId>\d+).+$',
            parser='detail_parser',
            name='detail'
        ),
        urlpattern(
            r'^https://kin-phinf.pstatic.net/(?P<date>.+)/.+/(?P<filename>.+)\?type=(?P<type>.+)$',
            parser='image_parser',
            name='image',
            referer='detail'
        )
    ]

    def list_parser(self, response, match, soup, context):
        return

    def detail_parser(self, response, match, soup, context):
        print('detail_parser:', response.url)
        return

    def image_parser(self, response, match, soup, context):
        print('image_parser:', response.url)


def naver_kin_with_image(params, context):
    nk = NaverKinScraper()
    r = nk.scrap(root_params=params, context=context)
