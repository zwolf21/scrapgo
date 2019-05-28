import pandas as pd

from scrapgo.lib.dataframe import TableFrame

from .kofia import *
from .utils import *
from .db_column_mappings import (
    DBMAP_RW_FUNDINFO,
    DBMAP_RW_FUNDINDEX,
    DBMAP_RW_FUNDSETTLE_BY_DATE
)


MIN_SEARCH_DATE = '19900101'
MAX_SEARCH_DATE = '20991231'
DEFAULT_AGO_DAYS = 7

FUNDINFO_TABLE = 'RW_FUNDINFO'
FUNDSETTLE_EXSO_TABLE = 'RW_FUNDSETTLE'
RW_FUNDINDEX_TABLE = 'RW_FUNDINDEX'



def _get_search_date_range(start_date=None, end_date=None, table_name=None, date_column_name=None, output=None, **kwargs):
    if start_date is None:
        if output in ['csv', 'xlsx', 'excel']:
            start_date = get_ago_str_date(days=DEFAULT_AGO_DAYS)
        elif output in ['db']:
            db = TableFrame(**kwargs)
            start_date = db.max(table_name, date_column_name)
        else:
            start_date = get_ago_str_date(days=DEFAULT_AGO_DAYS)
    if end_date is None:
        end_date = get_today_str_date()
    return start_date, end_date




def get_kofia_fundlist(**kwargs):
    start_date, end_date = _get_search_date_range(
        table_name=FUNDINFO_TABLE,
        date_column_name=DBMAP_RW_FUNDINFO['설정일'],
        **kwargs
    )
    s = KofiaFundListScraper()
    r = s.scrap(start_date=start_date, end_date=end_date)
    return pd.DataFrame(r['fund_list'])