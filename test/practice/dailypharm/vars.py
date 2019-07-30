from collections import OrderedDict

COLUMM_MAPPING = {
    'id': 'no',
    'AdType': 'adtype',
    'AdType2': 'adtype2',
    'E-Mail': 'email',
    'content': 'content',
    'smode': 'smode',
    'timestamp': 'published',
    '경력': 'career',
    '구인기간': 'rucuntil',
    '근무지역': 'workloc',
    '급여사항': 'payment',
    '기관명(상호)': 'company_name',
    '나이': 'age_limit',
    '담당업무': 'workcharge',
    '담당자명': 'charger',
    '모집인원': 'rucnum',
    '모집제목': 'ructitle',
    '성별': 'gender',
    '입사지원서': 'resume',
    '전화번호': 'tel',
    '주변지하철': 'sursubway',
    '채용대상': 'ructarget',
    '학력': 'edulevel',
    '휴대폰번호': 'cellphone'
}


def convert2mapping(records):
    records = [
        OrderedDict(
            (COLUMM_MAPPING.get(col, col), val) for col, val in row.items()
        )
        for row in records
    ]
    return records
