import argparse
import os
import sys

# from practice.naver_kin_scraper.kin import naver_kin_with_image
# from practice.naver_webtoon_scraper.webtoon2 import retrive_webtoon
# from practice.durginfo.druginfo_scraper import drug_search
from practice.kofia_scraper import *

sys.path.append('.')


MEDIA_ROOT = 'media'


def main():
    argparser = argparse.ArgumentParser(
        formatter_class=argparse.ArgumentDefaultsHelpFormatter, description="TEST Scraper"
    )
    argparser.add_argument('keywords', help='검색할 키워드들 나열', nargs='*')
    argparser.add_argument('-titleId', '--titleId')

    argparser.add_argument('-search', '--search', nargs='?')

    argparser.add_argument('-start', '--start', type=int, default=0)
    argparser.add_argument('-end', '--end', type=int, default=0)
    argparser.add_argument('-sd', '--start_date', type=str)
    argparser.add_argument('-ed', '--end_date', type=str)
    argparser.add_argument('-o', '--output', type=str)
    argparser.add_argument('-fund_std_code', '--fund_std_code')
    argparser.add_argument('-cd', '--code')
    argparser.add_argument('-conn', '--db_connect_json_path')

    args = argparser.parse_args()
    try:
        app = args.keywords[0]
    except:
        return

    context = {
        'save_to': MEDIA_ROOT
    }

    if app in ['webtoon', 'toon']:
        context['titleId'] = args.titleId
        retrive_webtoon(context)

    if app in ['kin']:
        context['save_to'] = os.path.join(MEDIA_ROOT, 'kin')
        naver_kin_with_image(params={'query': args.search}, context=context)

    if app in ['druginfo', 'di']:
        params = {
            'q': args.search
        }
        drug_search(params)

    kwargs = {k: v for k, v in args._get_kwargs() if v is not None}
    if app in ['kofia']:
        sub_app = args.keywords[1]
        if sub_app in ['ls']:
            df = get_kofia_fundlist(**kwargs)
        # if sub_app in ['fund_list', 'fl']:
        #     print('test get_kofia_fund_list')
        #     df = get_kofia_fund_list(args.start, args.end)
        # elif sub_app in ['fund_detail', 'fd']:
        #     print('test get_kofia_fund_detail')
        #     df = get_kofia_fund_detail(args.fund_std_code)
        # elif sub_app in ['price_progress', 'fpg']:
        #     print('text get_kofia_fund_price_progress')
        #     df = get_kofia_fund_price_progress(args.fund_std_code)
        # elif sub_app in ['fund_settle_exso', 'exso']:
        #     print('test get_kofia_fund_settle_exso')
        #     df = get_kofia_fund_settle_exso(args.fund_std_code)
        print(df.head())


if __name__ == "__main__":
    main()
