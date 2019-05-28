import pandas as pd


from scrapgo.utils.datecuts import slice_dates
from .utils import starts_after

from .scraper import *
from .db.vars import 펀드정보테이블명, 설정일

@starts_after(table_name=펀드정보테이블명, date_column_name=설정일)
@slice_dates(by='month')
def get_kofia_fundlist(**kwargs):
    sc = KofiaFundListScraper()
    r = sc.scrap(**kwargs)
    return pd.DataFrame(r['fund_list'])
        
