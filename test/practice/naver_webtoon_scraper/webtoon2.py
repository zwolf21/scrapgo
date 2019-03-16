from io import BytesIO

from scrapgo.scraper import RequestsSoupScraper, href, location, src


class NaverWebToonScraper(RequestsSoupScraper):
    SCRAP_RELAY = [
        location(
            'https://comic.naver.com/webtoon/weekday.nhn',
            filter='root_filter',
            parser='root_parser',
            refresh=True,
            name='root'
        ),
        href(
            r'^/webtoon/list.nhn\?titleId=(?P<titleId>\d+)&weekday=(?P<weekday>\w*)$',
            filter='toon_filter',
            parser='toon_parser',
            # refresh=True,
            name='toon',
        ),
        src(  # 이미지, 파일등 과같은 source 항목을 다운로드 필터링등 처리할 수 있다
            r'^https://shared-comic.pstatic.net/thumb/webtoon/(?P<titleId>\d+)/thumbnail/(?P<filename>.+)$',
            name='toon_thumb',
            parser='toon_thumb_parser'
        ),
        href(
            r'^/webtoon/list.nhn\?titleId=(?P<titleId>\d+)&weekday=(?P<weekday>\w*)&page=(?P<page>\d+)$',
            filter='toon_page_filter',
            recursive=True,  # 페이지 네이션 패턴을 재귀적으로 방문하여 모든 페이지에 방문함, 물론 필터링지정하면 필터링도 가능
            name='toon_page',
            refresh=True
        ),
        src(
            r'^https://shared-comic.pstatic.net/thumb/webtoon/(?P<titleId>\d+)/(?P<no>\d+)/(?P<filename>.+)$',
            parser='episode_thumb_parser', name='episode_thumb'
        ),
        href(
            r'^/webtoon/detail.nhn\?titleId=(?P<titleId>\d+)&no=(?P<no>\d+)&weekday=(?P<weekday>\w*)$',
            parser='episode_parser', name='episode'
        ),

    ]

    def main_filter(self, link, match, context):
        titleId = context.get('titleId')
        if titleId:
            if titleId == match('titleId'):
                # print('mainfilter:link=', link, '\n')
                return True

    def root_parser(self, response, match, soup, context):
        # print('root_parser:', response.url, '\n')
        return

    def toon_parser(self, response, match, soup, context):
        titlebar = soup.title.text.split('::')
        title = titlebar[0].strip()
        print('toon_parser:', response.url)
        titleId = match('titleId')
        weekday = match('weekday')

        author = soup.select('span.wrt_nm')[0].text.strip()

        return {
            'title': title,
            'author': author,
            'titleId': titleId,
            'weekday': weekday,
        }

    def episode_parser(self, response, match, soup, context):
        title = soup.select('div.tit_area > .view > h3')[0].text.strip()
        return {
            'titleId': match('titleId'),
            'no': match('no'),
            'episode_title': title,
        }

    def episode_thumb_parser(self, response, match, soup, context):
        return {
            'titleId': match('titleId'),
            'no': match('no'),
            'episode_thumbnail_filename': match('filename'),
            'episode_thumb_content': BytesIO(response.content),
        }

    def episode_cut_parser(self, link, match, content):
        return {
            'titleId': match('titleId'),
            'no': match('no'),
            'episode_cut_filename': match('filename'),
        }


n = NaverWebToonScraper()
# print(n.SCRAP_RELAY)
r = n.scrap(context={'titleId': '642653'})


for name, row in r.items():
    if name == 'episode':
        for r in row:
            print(r)
