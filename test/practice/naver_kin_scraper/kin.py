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
            parser='img_parser',
            name='image',
            referer='detail'
        )
    ]


# class NaverKinScraper(LinkPatternScraper):
#     ROOT_URL = 'https://kin.naver.com/search/list.nhn'
#     SCRAP_TARGET_ATTRS = settings.SCRAP_TARGET_ATTRS + ('content', )

#     LINK_PATTERNS = [
#         href(
#             r'^/search/list.nhn\?query=(?P<query>.+)&page=(?P<page>.+)$',
#             recursive=True,
#             parser='result_page_parser',
#             name='page'
#         ),
#         href(
#             r'^https://kin.naver.com/qna/detail.nhn\?d1id=(?P<d1id>\d+)&dirId=(?P<dirId>\d+)&docId=(?P<docId>\d+).+$',
#             parser='result_detail_parser',
#             name='detail'
#         ),
#         src(
#             r'^https://kin-phinf.pstatic.net/(?P<date>.+)/.+/(?P<filename>.+)\?type=(?P<type>.+)$',
#             parser='result_img_parser',
#             name='image'
#         ),

#     ]

#     def result_page_parser(self, response, match, soup, context):
#         query = unquote(match('query'))
#         query = query.replace(' ', '_')
#         path = os.path.join(context['save_to'], query)
#         context['query_path'] = path
#         mkdir_p(path)

#     def result_detail_parser(self, response, match, soup, context):
#         context[response.url] = []
#         # print(response.url)

#     def result_img_parser(self, response, match, content, context):
#         fn = match('filename')
#         save_to = os.path.join(context['query_path'], fn)
#         # with open(save_to, 'wb') as fp:
#         #     fp.write(content)
#         context['render_path'] = save_to
#         return{
#             'href': response.referer,
#             'src': response.url
#         }


# nk = NaverKinScraper(params={'query': '파이썬 크롤링'},
#                      context={'save_to': 'media/kin'})
# # print(nk.LINK_PATTERNS)
# r = nk.scrap()

# save_to = os.path.join(nk.context['query_path'], 'results.html')
# render_img2referer(save_to, r['image'])


# def naver_kin_with_image(params, context):
#     nk = NaverKinScraper(params=params, context=context)
#     r = nk.scrap()
#     save_to = os.path.join(nk.context['query_path'], 'results.html')
#     render_img2referer(save_to, r['image'])
