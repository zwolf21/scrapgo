import pandas as pd
import os
import re
import json
from io import BytesIO
from collections import namedtuple, OrderedDict

from scrapgo.scraper import LinkRelayScraper, url, urlpattern, urltemplate
from scrapgo.utils.shortcuts import mkdir_p, cp, parse_query, queryjoin, parse_root, parse_jsonp


COMMENT_PAGE_SIZE = 100


class NaverWebToonScraper(LinkRelayScraper):
    ROOT_URL = 'https://comic.naver.com/webtoon/weekday.nhn'
    REQUEST_DELAY = 0
    LINK_RELAY = [
        url(
            '/',
            as_root=True,
            parser='root_parser',
            refresh=True,
            name='root'
        ),
        urlpattern(
            r'^/webtoon/list.nhn\?titleId=(?P<titleId>\d+)&weekday=(?P<weekday>\w+)$',
            parser='toon_parser',
            refresh=True,
            name='toon',
        ),
        # urlpattern(  # 이미지, 파일등 과같은 source 항목을 다운로드 필터링등 처리할 수 있다
        #     r'^https://shared-comic.pstatic.net/thumb/webtoon/(?P<titleId>\d+)/thumbnail/(?P<filename>.+)$',
        #     name='toon_thumb',
        #     parser='toon_thumb_parser',
        # ),
        urlpattern(
            r'^/webtoon/list.nhn\?titleId=(?P<titleId>\d+)&weekday=(?P<weekday>\w*)&page=(?P<page>\d+)$',
            name='toon_page',
            parser='episode_pagination_parser',
            refresh=True,
            recursive=True  # 페이지 네이션 패턴을 재귀적으로 방문하여 모든 페이지에 방문함, 물론 필터링지정하면 필터링도 가능
        ),
        # urlpattern(
        #     r'^https://shared-comic.pstatic.net/thumb/webtoon/(?P<titleId>\d+)/(?P<no>\d+)/(?P<filename>.+)$',
        #     parser='episode_thumb_parser',
        #     name='episode_thumb',
        # ),
        urlpattern(
            r'^/webtoon/detail.nhn\?titleId=(?P<titleId>\d+)&no=(?P<no>\d+)&weekday=(?P<weekday>\w*)$',
            parser='episode_parser',
            name='episode',
        ),
        # urlpattern(
        #     r'^https://image-comic.pstatic.net/webtoon/(?P<titleId>\d+)/(?P<no>\d+)/(?P<filename>.+)$',
        #     parser='episode_cut_parser',
        #     name='episode_cut',
        #     referer='episode',
        # ),
        url(
            'https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json',
            set_params='comment_page_counter_set_params',
            name='comment_page_counter',
            parser='get_comment_page_count',
            referer='episode',
            # refresh=True,
        ),
        url(
            'https://apis.naver.com/commentBox/cbox/web_naver_list_jsonp.json',
            set_params='comment_set_params',
            name='comment',
            parser='comment_parser',
            referer='episode',
            # refresh=True,
        )
    ]

    def main_filter(self, link, query, match, context=None):
        if not match:
            return True
        titleId = context.get('titleId')
        return titleId and titleId == match('titleId')

    def root_parser(self, response, match, soup, context=None):
        print('root_parser:', response.url)

    def toon_parser(self, response, match, soup, context=None):
        print('toon_parser', response.url)
        pass

    def toon_thumb_parser(self, response, match, soup, context=None):
        # print('toon_thumb_parser:', response.url)
        pass

    def episode_pagination_parser(self, response, match, soup, context=None):
        # print('episode_pagination_parser:', response.url)
        pass

    def episode_parser(self, response, match, soup, context=None):
        # context['titleId'] = match('no')
        pass

    def episode_thumb_parser(self, response, match, soup, context=None):
        pass

    def episode_cut_parser(self, response, match, soup, context=None):
        print(response.request.headers['Referer'])
        pass

    def comment_page_counter_set_params(self, referer_response, url, root_params, context):
        params = self._get_comment_params(referer_response.url, page=1)
        yield queryjoin(url, params)

    def _get_comment_params(self, referer_response_url, page):
        query = parse_query(referer_response_url)
        params = dict(
            ticket='comic',
            templateId='webtoon',
            pool='cbox3',
            _callback='jQuery112406101924163625125_1554234985140',
            lang='ko',
            country='KR',
            objectId='{titleId}_{no}'.format(**query),
            pageSize=COMMENT_PAGE_SIZE,
            indexSize=10,
            listType='OBJECT',
            pageType='default',
            page=page,
            refresh='false',
            sort='NEW',
        )
        return params

    def get_comment_page_count(self, response, match, soup, context=None):
        comment = parse_jsonp(response.text)
        pageSize = comment['result']['pageModel']['pageSize']
        totalCount = comment['result']['count']['total']
        context[response.previous] = {'page_count': totalCount//pageSize + 1}

    def comment_set_params(self, referer_response, url, root_params, context):
        page_count = context[referer_response.url]['page_count']
        print('comment_set_params:', page_count)
        for page in range(1, page_count+1):
            params = self._get_comment_params(referer_response.url, page)
            yield queryjoin(url, params)

    def comment_parser(self, response, *args, **kwargs):
        comment = parse_jsonp(response.text)
        comments = comment['result']['commentList']
        return comments


def retrive_webtoon(context):
    comment_save_to = os.path.join(context['save_to'], 'comment.csv')
    n = NaverWebToonScraper()
    r = n.scrap(context=context)
    comments = r['comment']
    df = pd.DataFrame(comments)
    df.to_csv(comment_save_to)


# context = {'titleId': 638845, 'save_to': 'media'}

# retrive_webtoon(context)
