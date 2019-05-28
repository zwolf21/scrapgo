from types import GeneratorType
from collections import namedtuple, abc

import pandas as pd

from scrapgo.lib.dataframe import dataframe2path, TableFrame

from .settings import OUTPUT_FILE_FORMAT

from .apps import get_kofia_fundlist
from .db.vars import (
    펀드정보테이블명, 펀드정보테이블기준키, 펀드정보테이블컬럼매핑,
)


App = namedtuple('App', 'prefix table uniques mapping')

apps = {
    get_kofia_fundlist: App(
        'FundList_{start_date}~{end_date}',
        펀드정보테이블명, 펀드정보테이블기준키, 펀드정보테이블컬럼매핑
    )
}

def pipe(app, **kwargs):
    output = kwargs.get('output')
    dbconn = kwargs.get('path_connect_info_jsonfile')
    meta = apps.get(app)
    if meta is None:
        raise ValueError(
            f"{app.__name__}은 설정 된 출력 파이프가 없습니다. pipeline.py 의 apps에서 지정할 수 있습니다."
        )
    df = app(**kwargs)
    if not isinstance(df, GeneratorType):
        df = [df]
    if output in OUTPUT_FILE_FORMAT or output is None:
        dataframe = pd.concat(df, ignore_index=True)
        if output is None:
            print(dataframe.head())
        else:
            filename = meta.prefix.format(**kwargs)
            dataframe2path(dataframe, filename, extension=output)
    elif output in ['db']:
        db = TableFrame(
            path_connect_info_jsonfile=dbconn
        )
        if not meta.table:
            raise ValueError("DB 로 Insert 할 테이블명이 설정 되지않았 습니다.")
        for dataframe in df:
            db.insert(
                dataframe, meta.table, meta.uniques, meta.mapping
            )
    else:
        print(df.head())

