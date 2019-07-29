from .modules import PharmRecurtScraper
from listorm import Listorm


def get_dailypharm_recruit(**kwargs):
    phr = PharmRecurtScraper()
    r = phr.scrap(**kwargs)
    lst_detail = Listorm(r['detail'])
    lst_content = Listorm(r['content'])
    lst = lst_detail.join(lst_content, on='id')
    return lst
