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
            parser='detail_parser',
            filter='detail_filter',
            breaker='detail_breaker',
        ),
        url(
            'http://job.dailypharm.com/JobUsers/JobOffer/AdMemoView.html',
            generator='content_url_renderer',
            name='content',
            parser='content_parser'
        )
    ]

    def home_parser(self, response, page_limit=None):
        if page_limit:
            self.last_page = page_limit
            return
        soup = response.scrap.soup
        regx_page = re.compile(
            r'/JobUsers/JobOffer/index.html\?nStart=(?P<nStart>\d+)&searchWord=&'
        )
        soup_page_link = soup(href=regx_page)
        pages = []
        for page in soup_page_link:
            link = page['href']
            m = regx_page.match(link)
            nPage = int(m.group('nStart'))
            pages.append(nPage)
        self.last_page = max(pages)

    def list_url_renderer(self, parent_response, path, **kwargs):
        for nPage in range(0, self.last_page, 20):
            yield dict(
                nStart=nPage,
                searchWord=''
            )

    def list_parser(self, response, **kwargs):
        print('list_parser:', response.url)

    def detail_filter(self, link, query, match, **kwargs):
        return True

    def detail_breaker(self, response, **kwargs):
        print('detail_breaker:', response.url)
        return True

    def detail_parser(self, response, **kwargs):
        print('detail_parser:', response.url)
        soup = response.scrap.soup
        m = response.scrap.match
        self.id = m('id')
        record = dict(
            id=m('id'),
            smode=m('smode'),
            AdType=m('AdType'),
            AdType2=m('AdType2'),
        )

        def parse_upper_table(soup):
            upper_fields = [
                '모집제목', '주변지하철', '기관명(상호)', '담당업무', '채용대상', '모집인원',
                '근무지역', '급여사항', '성별', '나이', '학력', '경력'
            ]
            ret = {}
            for tr in soup('tr'):
                td_list = tr('td')
                if len(td_list) != 6:
                    continue
                c1, s1, v1, c2, s2, v2 = map(self.prettify_textarea, td_list)
                if c1 in upper_fields:
                    ret[c1] = v1
                    ret[c2] = v2
            return ret
        r = parse_upper_table(soup)
        record.update(r)

        def parse_lower_table(soup):
            lower_fields = [
                '구인기간', '입사지원서', '담당자명', '전화번호', '휴대폰번호', 'E-Mail'
            ]
            ret = {}
            for tr in soup('tr'):
                td_list = tr('td', class_='viewPage')
                if len(td_list) != 12:
                    continue
                구인기간, v1, 입사지원서, v2, 담당자명, v3, 전화번호, v4, 휴대폰번호, v5, EMail, v6 = map(
                    self.prettify_textarea, td_list)
                if 구인기간 in lower_fields:
                    ret[구인기간] = v1
                    ret[입사지원서] = v2
                    ret[담당자명] = v3
                    ret[전화번호] = v4
                    ret[휴대폰번호] = v5
                    ret[EMail] = v6
            return ret
        r = parse_lower_table(soup)
        record.update(r)
        return record

    def content_url_renderer(self, parent_response, path, **kwargs):
        yield dict(ID=self.id)

    def content_parser(self, response, **kwargs):
        # print('content_parser:', response.url)
        soup = response.scrap.soup
        regx_timestamp = re.compile(
            r'게시일\s*:\s*(?P<year>\d+)년\s*(?P<month>\d+)월\s*(?P<day>\d+)일\s*(?P<hour>\d+)시\s*(?P<minute>\d+)분'
        )
        record = dict(
            id=self.id,
            content='',
            timestamp=None
        )
        for table in soup.select('table table'):
            content = self.prettify_textarea(table)
            record['content'] = content

        for strong in soup('strong'):
            text = self.prettify_textarea(strong)
            m = regx_timestamp.search(text)
            if m:
                record['timestamp'] = '{}-{}-{} {}:{}:00'.format(*m.groups())

        return record
