from scrapgo.scraper import Scraper
from scrapgo.actions import location, href, src


class NaverWebtoonScraper(Scraper):
    ROOT_URL = 'https://comic.naver.com/webtoon/weekday.nhn'
    LINK_ROUTER = [
        location(
            '/',
            'root_parser', name='root'
        ),
        href(
            r'^/webtoon/list.nhn\?titleId=(?P<titleId>\d+)&weekday=(?P<weekday>\w*)$',
            'toon_urlfilter', 'toon_parser', name='toon'
        ),
        src(
            r'^https://shared-comic.pstatic.net/thumb/webtoon/(?P<titleId>\d+)/thumbnail/(?P<filename>.+)$',
            name='toon_thumb'
        ),
        href(
            r'^/webtoon/list.nhn\?titleId=(?P<titleId>\d+)&weekday=(?P<weekday>\w*)&page=(?P<page>\d+)$',
            recursive=True, name='toon_page'
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
    print(name, row[:5])
    pass
