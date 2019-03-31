import os
import re
from io import BytesIO
from collections import namedtuple, OrderedDict

from scrapgo.scraper import LinkPatternScraper, href, location, src
from scrapgo.utils.shortcuts import mkdir_p, cp


class NaverWebToonScraper(LinkPatternScraper):
    ROOT_URL = 'https://comic.naver.com/webtoon/weekday.nhn'
    REQUEST_DELAY = 0.1
    # CACHE_BACKEND = 'memory'

    LINK_PATTERNS = [
        location(
            '/',
            filter='root_filter',
            parser='root_parser',
            refresh=True,
            name='root'
        ),
        href(
            r'^/webtoon/list.nhn\?titleId=(?P<titleId>\d+)&weekday=(?P<weekday>.+)$',
            parser='toon_parser',
            refresh=True,
            name='toon',
        ),
        src(  # 이미지, 파일등 과같은 source 항목을 다운로드 필터링등 처리할 수 있다
            r'^https://shared-comic.pstatic.net/thumb/webtoon/(?P<titleId>\d+)/thumbnail/(?P<filename>.+)$',
            name='toon_thumb',
            parser='toon_thumb_parser',
            referer='toon'  # 위에서 방문하였던 패턴의 주소를 request header 에 referer로 셋팅 할 수 있다
        ),
        href(
            r'^/webtoon/list.nhn\?titleId=(?P<titleId>\d+)&weekday=(?P<weekday>\w*)&page=(?P<page>\d+)$',
            recursive=True,  # 페이지 네이션 패턴을 재귀적으로 방문하여 모든 페이지에 방문함, 물론 필터링지정하면 필터링도 가능
            name='toon_page',
            parser='episode_pagination_parser',
            refresh=True
        ),
        src(
            r'^https://shared-comic.pstatic.net/thumb/webtoon/(?P<titleId>\d+)/(?P<no>\d+)/(?P<filename>.+)$',
            parser='episode_thumb_parser',
            name='episode_thumb',
            set_header='episode_cut_set_header',
            referer='toon_page'
        ),
        href(
            r'^/webtoon/detail.nhn\?titleId=(?P<titleId>\d+)&no=(?P<no>\d+)&weekday=(?P<weekday>\w*)$',
            parser='episode_parser',
            name='episode'
        ),
        src(
            r'^https://image-comic.pstatic.net/webtoon/(?P<titleId>\d+)/(?P<no>\d+)/(?P<filename>.+)$',
            parser='episode_cut_parser',
            name='episode_cut',
            set_header='episode_cut_set_header',
            referer='episode'
        )
    ]

    def main_filter(self, link, query, match, context):
        if not match:
            return True

        titleId = context.get('titleId')
        if titleId:
            if titleId == match('titleId'):
                return True

    def root_parser(self, response, match, soup, context):
        save_to = context['save_to']
        mkdir_p(save_to)
        context[response.url] = save_to

    def toon_parser(self, response, match, soup, context):
        titlebar = soup.title.text.split('::')
        title = titlebar[0].strip()
        titleId = match('titleId')
        weekday = match('weekday')
        author = soup.select('span.wrt_nm')[0].text.strip()

        toon_path = os.path.join(context[response.referer], title)
        mkdir_p(toon_path)
        context[response.url] = toon_path

        return {
            'toon_title': title,
            'author': author,
            'titleId': titleId,
            'weekday': weekday,
        }

    def toon_thumb_parser(self, response, match, soup, context):
        # print('toon_thumb_parser', response.request.headers)

        toon_path = context[response.referer]
        path = os.path.join(toon_path, match('filename'))
        cp(path, response.content)

    def episode_pagination_parser(self, response, match, soup, context):
        context[response.url] = context[response.referer]

    def episode_thumb_parser(self, response, match, soup, context):
        # print('episode_thumb_parser', response.request.headers)
        episode_path = context[response.referer]
        EpThumb = namedtuple('EpThumb', 'titleId no filename content')
        thumb = EpThumb(
            match('titleId'), match('no'), match('filename'), response.content
        )
        context.setdefault('episode_thumb', []).append(thumb)

    def episode_parser(self, response, match, soup, context):
        episode_titles = soup.select('div.tit_area > .view > h3')
        episode_title = episode_titles[0].text.strip()
        episode_no = match('no')
        titleId = match('titleId')
        toon_path = context[response.referer]
        episode_path = os.path.join(toon_path, episode_title)
        mkdir_p(episode_path)
        context[response.url] = episode_path

        return {
            'titleId': titleId,
            'no': episode_no,
            'episode_title': episode_title,
        }

    def episode_cut_parser(self, response, match, soup, context):
        episode_path = context[response.referer]
        path = os.path.join(episode_path, match('filename'))
        cp(path, response.content)

        # print('episode_cut_parser', response.request.headers)
        titleId = match('titleId')
        no = match('no')
        episode_thumb = None
        for thumb in context['episode_thumb']:
            if thumb.titleId == titleId and thumb.no == no:
                episode_thumb = thumb
        if episode_thumb is not None:
            thumb_path = os.path.join(episode_path, episode_thumb.filename)
            cp(thumb_path, episode_thumb.content)


def retrive_webtoon(context):
    n = NaverWebToonScraper(context=context)
    return n.scrap()
