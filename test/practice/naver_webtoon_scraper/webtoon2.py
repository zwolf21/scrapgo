import os
from io import BytesIO

from listorm import Listorm

from scrapgo.scraper import RequestsSoupScraper, href, location, src
from .parsers import *


class NaverWebToonScraper(RequestsSoupScraper):
    SCRAP_RELAY = [
        location(
            'https://comic.naver.com/webtoon/weekday.nhn',
            filter='root_filter',
            parser=root_parser,
            refresh=True,
            name='root'
        ),
        href(
            r'^/webtoon/list.nhn\?titleId=(?P<titleId>\d+)&weekday=(?P<weekday>.+)$',
            parser=toon_parser,
            refresh=True,
            name='toon',
        ),
        src(  # 이미지, 파일등 과같은 source 항목을 다운로드 필터링등 처리할 수 있다
            r'^https://shared-comic.pstatic.net/thumb/webtoon/(?P<titleId>\d+)/thumbnail/(?P<filename>.+)$',
            name='toon_thumb',
            parser=toon_thumb_parser
        ),
        href(
            r'^/webtoon/list.nhn\?titleId=(?P<titleId>\d+)&weekday=(?P<weekday>\w*)&page=(?P<page>\d+)$',
            recursive=True,  # 페이지 네이션 패턴을 재귀적으로 방문하여 모든 페이지에 방문함, 물론 필터링지정하면 필터링도 가능
            name='toon_page',
            parser=episode_pagination_parser,
            refresh=True
        ),
        src(
            r'^https://shared-comic.pstatic.net/thumb/webtoon/(?P<titleId>\d+)/(?P<no>\d+)/(?P<filename>.+)$',
            parser=episode_thumb_parser,
            name='episode_thumb',
            refresh=True,
            set_header='episode_cut_set_header'
        ),
        href(
            r'^/webtoon/detail.nhn\?titleId=(?P<titleId>\d+)&no=(?P<no>\d+)&weekday=(?P<weekday>\w*)$',
            parser=episode_parser,
            name='episode'
        ),
        src(
            r'^https://image-comic.pstatic.net/webtoon/(?P<titleId>\d+)/(?P<no>\d+)/(?P<filename>.+)$',
            parser=episode_cut_parser,
            name='episode_cut',
            set_header='episode_cut_set_header'
        )

    ]

    def main_filter(self, link, match, context):
        titleId = context.get('titleId')
        if titleId:
            if titleId == match('titleId'):
                # print('mainfilter:link=', link, '\n')
                return True


def retrive_webtoon(titleId):
    context = {
        'save_to': './media',
        'titleId': titleId
    }
    n = NaverWebToonScraper(context=context)
    return n.scrap()


r = retrive_webtoon('642653')
