from scrapgo.scraper import LinkRelayScraper, url, urlpattern, urltemplate
from scrapgo.utils.shortcuts import mkdir_p, cp, parse_query, queryjoin, parse_root

curl = 'https://www.askcompany.kr/r/articles/508dbd1/',
HEADERS = {
    'Connection': 'keep-alive',
    'Cache-Control': 'max-age=0',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/73.0.3683.86 Safari/537.36',
    'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3',
    'Referer': 'https://www.askcompany.kr/r/sections/dfc55e7/',
    'Accept-Encoding': 'gzip, deflate, br',
    'Accept-Language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'Cookie': '_ga=GA1.2.1854103529.1548822083; _fbp=fb.1.1550256943431.2127390069; csrftoken=k1vHqbpVcBfPcbF2kLq33WCyXNr0GWsttBAgcSNXkdl01DJ7SpUBah0tj0PHhNZG; sessionid=f46a9turvcgcc5mfdxlwvrmyewncl65t; ARRAffinity=217486509fc227a70c3dc13d19fed9b804c68ab5eb0ebb8b56c0606f7ffa2b4f; _gid=GA1.2.201713794.1554746918; _gat=1'
}


class AskCompanyScraper(LinkRelayScraper):
    ROOT_URL = 'https://www.askcompany.kr/r/'
    HEADERS = HEADERS
    LINK_RELAY = [
        urlpattern(

        )
    ]
