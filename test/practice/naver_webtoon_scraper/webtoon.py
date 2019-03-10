from scrapgo.scraper import Scraper
from scrapgo.actions import location, href, src  # 액션 함수


class NaverWebtoonScraper(Scraper):
    ROOT_URL = 'https://comic.naver.com/webtoon/weekday.nhn'
    LINK_ROUTER = [
        location(  # 주어진 사이트의 주소에서 작업
            '/',  # self.ROOT_URL 의미한다
            'root_parser',  # 문자열 입력 시 본 클래스의 인스턴스로 파서함수를 작성해야한다
            name='root',  # 나중에 파싱 결과물 리듀싱할 때 분류될 namespace
            caching=False
        ),
        href(  # 라우터의 바로 앞의 결과물 페이징서 파싱할 링크 주소의 패턴, 패턴필터링, 파서등을 지정한다.
            # 각 웹툰페이지링크 주소 패턴
            r'^/webtoon/list.nhn\?titleId=(?P<titleId>\d+)&weekday=(?P<weekday>\w*)$',
            # url주소를 이용한 필터링, 필터된 항목들은 리듀싱밑 다음 단계의 액션으로 전달되지 않는다.
            urlfilter='toon_urlfilter',
            parser='toon_parser',
            name='toon',
            caching=False
        ),
        src(  # 이미지, 파일등 과같은 source 항목을 다운로드 필터링등 처리할 수 있다
            r'^https://shared-comic.pstatic.net/thumb/webtoon/(?P<titleId>\d+)/thumbnail/(?P<filename>.+)$',
            name='toon_thumb'
        ),
        href(
            r'^/webtoon/list.nhn\?titleId=(?P<titleId>\d+)&weekday=(?P<weekday>\w*)&page=(?P<page>\d+)$',
            recursive=True,  # 페이지 네이션 패턴을 재귀적으로 방문하여 모든 페이지에 방문함, 물론 필터링지정하면 필터링도 가능
            name='toon_page'
        ),
        src(
            r'^https://shared-comic.pstatic.net/thumb/webtoon/(?P<titleId>\d+)/(?P<no>\d+)/(?P<filename>.+)$',
            parser='episode_thumb_parser', name='episode_thumb'
        ),
        href(
            r'^/webtoon/detail.nhn\?titleId=(?P<titleId>\d+)&no=(?P<no>\d+)&weekday=(?P<weekday>\w*)$',
            parser='episode_parser', name='episode'
        ),
        src(
            r'^https://image-comic.pstatic.net/webtoon/(?P<titleId>\d+)/(?P<no>\d+)/(?P<filename>.+)\.jpg$',
            parser='episode_cut_parser', name='episode_cut'
        )
    ]

    # toon 단계에서 필터링 하면 이후의 라우팅 액션에서도 다른 툰하위 페이지에는 접근 하지 않는다
    def toon_urlfilter(self, link, match, context):
        titleId = context.get('titleId')
        if titleId in link:
            # print('toon_urlfilter:', link)
            return True

    def toon_parser(self, link, match, soup):
        titlebar = soup.title.text.split('::')
        title = titlebar[0].strip()

        titleId = match('titleId')
        weekday = match('weekday')

        author = soup.select('span.wrt_nm')[0].text.strip()

        return {
            'title': title,
            'author': author,
            'titleId': titleId,
            'weekday': weekday,
        }

    def episode_parser(self, link, match, soup):
        title = soup.select('div.tit_area > .view > h3')[0].text.strip()
        return {
            'titleId': match('titleId'),
            'no': match('no'),
            'episode_title': title,
        }

    def episode_thumb_parser(self, link, match, content):
        return {
            'titleId': match('titleId'),
            'no': match('no'),
            'episode_thumbnail_filename': match('filename'),
            'episode_thumb_content': content,
        }

    def episode_cut_parser(self, link, match, content):
        return {
            'titleId': match('titleId'),
            'no': match('no'),
            'episode_cut_filename': match('filename'),

        }


r = NaverWebtoonScraper().scrap(
    context={'titleId': '642653'}, until='episode')
for name, row in r.items():
    # print(name, row[:5])
    pass
