import re
from scrapgo import LinkRelayScraper, urlpattern, url, root


class PharmRecurtScraper(LinkRelayScraper):
    REQUEST_DELAY = 0
    ROOT_URL = 'http://job.dailypharm.com/JobUsers/JobOffer/index.html'
    LINK_RELAY = [
        url(
            'http://job.dailypharm.com/JobUsers/JobOffer/index.html',
            name='home',
            parser='home_parser',
        ),
        url(
            'http://job.dailypharm.com/JobUsers/JobOffer/index.html',
            name='list',
            parser='list_parser',
            generator='list_url_renderer'
        ),
        urlpattern(
            r'^http://job.dailypharm.com/JobUsers/JobOffer/JobOffer_View.html\?mode=(?P<view>.*)&ID=(?P<id>\d+)&smode=(?P<smode>.*)&subType=(?P<subType>.*)&AdType=(?P<AdType>\d+)&AdType2=(?P<AdType2>\d+)&nowType=(?P<nowType>.*)&listAll=(?P<listAll>.+)&retStart=(?P<retStart>\d*)&searchWork1=(?P<searchWork1>.*)&searchWork2=(?P<serachWork2>.*)&searchSiDo=(?P<searchSiDo>.*)&searchGuGun=(?P<searchGuGun>.*)&searchDong=(?P<searchDong>.*)$',
            name='detail',
            parser='detail_parser'
        )
    ]

    def home_parser(self, response, **kwargs):
        soup = response.scrap.soup
        regx_page = re.compile(
            r'/JobUsers/JobOffer/index.html\?nStart=(?P<nStart>\d+)&searchWord=&')
        soup_page_link = soup(href=regx_page)
        pages = []
        for page in soup_page_link:
            link = page['href']
            m = regx_page.match(link)
            nPage = int(m.group('nStart'))
            pages.append(nPage)
        self.last_page = max(pages)

    def list_url_renderer(self, parent_response, path):
        for nPage in range(0, self.last_page, 20):
            yield dict(
                nStart=nPage,
                searchWord=''
            )

    def list_parser(self, response, **kwargs):
        print('list_parser:', response.url)

    def detail_parser(self, response, **kwargs):
        print('detail_parser:', response.url)