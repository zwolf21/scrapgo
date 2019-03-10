# scrapgo
## 개요 및 특징
### 1. django 스타일의 라우터에 링크 페턴과 그 패턴에 해당하는 액션과 옵션 기재 - 필터링, 파싱
### 2. 라우터에 적힌 순서대로 URL방문, LINK패턴방문, SOURCE(이미지,파일)등을 수집및 파싱
### 3. 라우터배열의 앞쪽에 있는 출력을 다음순번의 link파서가 처리하는 형태- 페이지 방문 루트를 정할수 있다.
### 4. 파싱된 결과물 REDUCER 로 통합 - 딕셔너리 리스트(table) 형태로 리턴
### 5. requests-cache 를 이용한 캐쉬기능 - 라이브러리 테스트 활용시 서버부담 감소
### 6. 재귀적 크롤링으로 링크 패턴 수집- 페이지네이션된 수집용이, 마지막 페이지, 페이지 카운트 계산하지 않아도 모든 페이지 방문 가능
