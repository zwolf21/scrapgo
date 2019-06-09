# DB INSERT 용 컬럼 매핑

# RW_FUNDINFO TABLE
펀드정보테이블컬럼매핑 = {
    '표준코드': "forgcode",
    '회사': "fmngcomcd",
    '펀드명': "fundnm",
    '설정일': "setupymd",
    '펀드유형': "fundtype",
    '투자지역': "investpl",
    '수탁회사': "acctcomp",
    '대표판매사': "salecomp",
    '구분': "vfundgbnm",
    '상품분류': "ufundtypnm",
    '추가/단위구분': "vadditionalestmtdnm",
    '최초설정일': "establishmentdt",
    '분류코드': "classcd",
    '단축코드': "shortcd",
    '신탁회계기간': "trustacctrm",
    '투자지역구분': "vinvestrgngbnm",
    '판매지역구분': "vsalergngbnm",
    '운용실적공시분류': "vprofittypecdnm",
    '특성분류': "vtraitdivnm",
    '공시/사모구분': "vpripubgbnm",
    '최소설정기준가격': "establishmentcot",
    '신탁기간': "trusttrm",
    '운용보수': "managerewrate",
    '판매보수': "salerewrate",
    '수탁보수': "trustrewrate",
    '일반사무수탁보수': "generalofctrtrewrate",
    '보수합계': "rewsum",
    '총비율이율(TER)': "ter",
    '선취수수료': "frontendcmsrate",
    '후취수수료': "backendcmsrate",
    '운용회사': "vmanagecompnm",
    '일반사무수탁회사': "vgeneralofctrtcompnm",
    '수탁회사상세': "vtrustcompnm",
    '회사코드': "companycd",
    '설정원본': "uoriginalamt",
    '순자산총액': "netasstotamt",
    '스크랩여부': "_scrapyn",
    '상환여부': "_retyn",
    'created': "reg_date",
    'updated': "mod_date",
}


지수테이블컬럼매핑 = {
    '표준코드': 'forgcode',
    '기준일자': 'standarddt',
    '기준가격': 'standardcot',  # DB와 안맞아서 아래 거로 바꿈
    # '기준가격': 'standardassstdcot',
    '전일대비등락': 'vbefdayfltstdcot',
    '과표기준가격': 'standardassstdcot',
    '설정원본': 'uoriginalamt',
    'KOSPI': 'kospiepn',
    'KOSPI200': 'kospi200epn',
    # 'KOSPI200': 'kospiepn',  # DB와 안맞아서 아래 거로 바꿈
    'KOSDAQ': 'kosdaqepn',
    '국공채(3년만기)': 'tbondbnd3y',
    '회사채(3년만기)': 'companybnd3y',
    'created': "reg_date",
    'updated': "mod_date",
}

DBMAP_RW_FUNDSETTLE = {
    '표준코드': 'forgcode',
    '신탁회계기초': 'trustaccsrt',
    '신탁회계기말': 'trustaccend',
    '경과일수': 'vpassdaycnt',
    '기준':  'standardcot',
    '과표':  'standardasscot',
    '설정원본': 'uoriginalamt',
    '결산': 'vsettlegbnm',
    'created': "reg_date",
    'updated': "mod_date",
}

결산테이블컬럼매핑 = {
    '표준코드': 'forgcode',
    # '회사': "fmngcomcd",
    # '펀드명': "fundnm",
    '회계기초': 'trustaccsrt',
    '회계기말': 'trustaccend',
    '경과일수': 'vpassdaycnt',
    '기준':  'standardcot',
    '과표':  'standardasscot',
    '설정원본': 'uoriginalamt',
    '구분': 'vsettlegbnm',
    '분배율': 'distribrt',
    'created': "reg_date",
    'updated': "mod_date",
}

# 자주쓰는 DB 테이블 접근 변수

펀드정보테이블명 = 'KOFIA_FUNDINFO'
지수테이블명 = 'KOFIA_FUNDINDEX'
결산테이블명 = 'RW_FUNDSETTLE'


표준코드 = 펀드정보테이블컬럼매핑['표준코드']
회사코드 = 펀드정보테이블컬럼매핑['회사코드']
설정일 = 펀드정보테이블컬럼매핑['설정일']
스크랩여부 = 펀드정보테이블컬럼매핑['스크랩여부']
펀드명 = 펀드정보테이블컬럼매핑['펀드명']
상환여부 = 펀드정보테이블컬럼매핑['상환여부']
표준코드 = 펀드정보테이블컬럼매핑['표준코드']

기준일자 = 지수테이블컬럼매핑['기준일자']

회계기말 = 결산테이블컬럼매핑['회계기말']
구분 = 결산테이블컬럼매핑['구분']


펀드정보테이블기준키 = [표준코드]
지수테이블기준키 = [표준코드, 기준일자]
결산테이블기준키 = [회계기말, 표준코드, 구분]
