import argparse
import os

from practice.naver_webtoon_scraper.webtoon2 import retrive_webtoon
from practice.naver_kin_scraper.kin import naver_kin_with_image
from practice.im.im_review_scraper import review


MEDIA_ROOT = 'media'


def main():
    argparser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="TEST Scraper"
    )
    argparser.add_argument('keywords', help='검색할 키워드들 나열', nargs='*')
    argparser.add_argument('-titleId', '--titleId')

    argparser.add_argument('-search', '--search', nargs='?')

    argparser.add_argument('-start', '--start', type=int, default=1)
    argparser.add_argument('-end', '--end', type=int, default=1)

    args = argparser.parse_args()
    app = args.keywords[0]

    context = {
        'save_to': MEDIA_ROOT
    }

    if app in ['webtoon']:
        context['titleId'] = args.titleId
        retrive_webtoon(context)

    if app in ['kin']:
        context['save_to'] = os.path.join(MEDIA_ROOT, 'kin')
        naver_kin_with_image(params={'query': args.search}, context=context)

    if app in ['im']:
        context['save_to'] = os.path.join(MEDIA_ROOT, 'im')
        context['start'] = args.start
        context['end'] = args.end
        review(context)


if __name__ == "__main__":
    main()
