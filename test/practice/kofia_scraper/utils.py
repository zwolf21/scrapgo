from datetime import datetime, timedelta

from dateutil.relativedelta import relativedelta
from dateutil.parser import parse
from dateutil.rrule import rrule, MONTHLY, YEARLY


DATESTR_FMT = "%Y%m%d"



def datetime2str(datetime, fmt=DATESTR_FMT):
    return datetime.strftime(fmt)


def get_today_str_date(fmt=DATESTR_FMT):
    today = datetime.today()
    str_today = today.strftime(fmt)
    return str_today


def get_ago_str_date(fmt=DATESTR_FMT, **kwargs):
    today = datetime.today()
    ago = today - relativedelta(**kwargs)
    str_ago = ago.strftime(fmt)
    return str_ago


def get_date_ago_range(start_date=None, end_date=None, days_ago=None, months_ago=None, years_ago=None, default_ago_days=7, **kwargs):
    end_date = end_date or get_today_str_date()

    if start_date:
        start_date = start_date
    elif days_ago:
        start_date = get_ago_str_date(days=days_ago)
    elif months_ago:
        start_date = get_ago_str_date(months=months_ago)
    elif years_ago:
        start_date = get_ago_str_date(years=years_ago)
    else:
        start_date = get_ago_str_date(days=default_ago_days)

    if start_date > end_date:
        raise ValueError('start_date > end_date')
    return start_date, end_date



def parse_date(date, fmt=None):
    if isinstance(date, datetime):
        d = date
    elif isinstance(date, str):
        d = parse(date)
    if fmt is not None:
        return d.strftime(fmt)
    return d


def get_first_date(date, of='year', fmt=None):
    d = parse_date(date)
    if of == 'year':
        y, m, d = d.year, 1, 1
    else:
        y, m, d = d.year, d.month, 1
    fdate = datetime(y, m, d)
    return parse_date(fdate, fmt=fmt)


def get_last_date(date, of='year', fmt=None):
    d = parse_date(date)
    if of == 'year':
        ndate = d + relativedelta(years=1)
    else:
        ndate = d + relativedelta(months=1)
    nfdate = get_first_date(ndate, of=of)
    ldate = nfdate - relativedelta(days=1)
    return parse_date(ldate, fmt=fmt)


def slice_date_range(start_date, end_date, by='year', fmt=DATESTR_FMT):
    start_date = parse_date(start_date)
    end_date = parse_date(end_date)
    ini_start_date = get_first_date(start_date, of=by)
    fin_end_date = get_last_date(end_date, of=by)
    freq = YEARLY if by == 'year' else MONTHLY
    date_list = list(rrule(freq=freq, dtstart=ini_start_date,
                           until=fin_end_date, interval=1))
    if start_date not in date_list:
        date_list.insert(0, start_date)
    for i, d in enumerate(date_list):
        if d < start_date:
            continue
        s = d
        e = get_last_date(s, of=by)
        if e >= end_date:
            e = end_date
        yield parse_date(s, fmt), parse_date(e, fmt)

from collections import OrderedDict


def parse_xml_table_tag(soup, tag, column_mapping=None, many=True):
    if column_mapping is not None:
        records = [
            OrderedDict(
                (column_mapping.get(r.name, r.name), r.text)
                for r in r.children
                if r.name in column_mapping
            )
            for r in soup(tag)
        ]
    else:
        records = [
            OrderedDict((r.name, r.text))
            for r in r.children
            if r.name
        ]
    if many == True:
        return records
    if records:
        return records[0]
    return {}
