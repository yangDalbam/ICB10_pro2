# 🗺️ 한국관광공사 API 연동 & Streamlit 대시보드 구축 작업 계획서

본 계획서는 한국관광공사의 공공데이터 및 방한 외래관광객 통계 데이터를 연동하여 동적인 Streamlit 대시보드를 구축하기 위한 기획 및 설계안입니다.

---

## 1. 프로젝트 개요 및 목표
* **목표**: 글로벌 방한 외래관광객 트렌드와 국내 지역별 관광 다양성 및 수요 데이터를 입체적으로 분석하고 시각화하는 동적 Streamlit 대시보드 앱 구현
* **주요 타겟 데이터**:
  1. 방한 외래관광객 상세 월별 집계 데이터 (ODCloud)
  2. 지역별 관광 다양성 지표 데이터 (한국관광공사)
  3. 지역별 관광 자원 및 서비스 수요 데이터 (한국관광공사)

---

## 2. 프로젝트 폴더 구조 (상대경로)

```
korea-trip-data/
├── .env                # API 인증키 등 환경변수 관리
├── data/              # 수집된 RAW JSON 및 가공 데이터 저장
├── docs/              # API 상세 문서 및 본 작업 계획서 보관
│   └── work_plan.md
├── images/            # 시각화 리포트용 차트 이미지 보관
├── report/            # EDA 및 데이터 분석 리포트 보관
└── src/
    ├── api/
    │   ├── __init__.py
    │   ├── odcloud_api.py  # 방한 외래객 API 요청 모듈
    │   └── kto_api.py      # 관광 다양성/수요 API 요청 모듈
    ├── pages/
    │   ├── 1_Foreigner_Trend.py   # 방한 외래객 분석 화면
    │   ├── 2_Tourism_Diversity.py # 지역별 관광 다양성 화면
    │   └── 3_Demand_Analysis.py   # 관광 자원 및 서비스 수요 화면
    └── app.py          # Streamlit 메인 홈 화면 및 핵심 KPI 요약
```

---

## 3. 연동 대상 API 및 활용 계획

### API 1: 방한 외래관광객 상세 월별 집계
* **Base URL**: `https://api.odcloud.kr/api`
* **Namespace**: `15136774/v1`
* **인증 방식**: Query Parameter (`serviceKey` 전달)
* **주요 활용 지표**: 국적별, 성별, 연령대별, 교통수단별 월간 방한 외래관광객 수 추이 분석

### API 2: 지역별 관광 다양성 서비스
* **Endpoint**: `https://apis.data.go.kr/B551011/AreaTarDivService`
* **주요 오퍼레이션**:
  * `getAreaTarVisitorDivList` (관광객 다양성)
  * `getAreaTarSpendDivList` (관광소비 다양성)
  * `getAreaTarIntlDivList` (국제적 다양성)
* **주요 활용 지표**: 전국 시군구별 관광객 분포 및 관광 소비 금액 다양성 지수 비교

### API 3: 지역별 관광 자원 수요 서비스
* **Endpoint**: `https://apis.data.go.kr/B551011/AreaTarResDemService`
* **주요 오퍼레이션**:
  * `getAreaTarServDemList` (지역별 관광 서비스 수요 - SNS 언급량, 소비액, 내비게이션 목적지 검색량)
  * `getAreaTarCultDemList` (지역별 문화 자원 수요 - 내비게이션 목적지 검색량)
* **주요 활용 지표**: 소셜 미디어 및 실시간 내비게이션 목적지 검색 데이터를 통한 관광지 관심도 추적

---

## 4. 단계별 구현 계획

### 1단계: API 클라이언트 개발 및 연결 검증
* `korea-trip-data/.env` 파일 생성 후 인증키 등록
* `korea-trip-data/src/api/odcloud_api.py` 및 `korea-trip-data/src/api/kto_api.py` 구현
* 호출 캐싱(`st.cache_data`) 적용 및 예외 처리(인증 오류, 타임아웃, 예외 발생 시 로컬 캐시 활용) 구조화

### 2단계: 데이터 전처리 및 탐색적 데이터 분석 (EDA)
* 수집한 JSON 데이터를 Pandas DataFrame으로 변환 후 정형화하여 `korea-trip-data/data/`에 보관
* `eda-basic` 워크플로우에 기반한 기본 데이터 탐색(일변량/다변량 교차 분석 10종 이상 수행)
* 시각화 차트를 `korea-trip-data/images/`에 저장하고 한국어 분석 리포트(`korea-trip-data/report/eda_report.md`) 작성

### 3단계: Streamlit 웹앱 대시보드 UI 개발
* `korea-trip-data/src/app.py`에 메인 화면 구축
* `korea-trip-data/src/pages/` 하위에 다중 페이지 구현
* Plotly 및 Mapbox(지도 매핑)를 활용한 동적 인터랙티브 차트 구현
* 연도, 월, 지역 대분류/소분류 등 동적 필터 사이드바 연동

### 4단계: 테스트 및 배포 준비
* API 호출 한계 및 데이터 오류 상황에 대한 Fallback 로직 테스트
* 로컬 테스트 진행 후 Streamlit Cloud 배포 최적화
