from .modules import PharmRecurtScraper
from listorm import Listorm

from .vars import convert2mapping


def get_dailypharm_recruit(**kwargs):
    phr = PharmRecurtScraper()
    r = phr.scrap(**kwargs)
    lst_detail = Listorm(r['detail'])
    lst_content = Listorm(r['content'])
    lst = lst_detail.join(lst_content, on='id')
    records = lst.to_records()
    conv = convert2mapping(records)
    return conv
