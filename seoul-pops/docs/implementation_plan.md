# SQLite 데이터베이스 구축 및 대시보드 로드 속도 최적화 계획

기존에 850만 건의 원본 Parquet 데이터를 메모리에 전체 로드하여 실시간으로 계산하던 구조에서, **미리 집계된(Aggregated) 데이터를 SQLite DB에 저장**하고 이를 조회하는 방식으로 아키텍처를 대폭 최적화합니다. 특히 지도 시각화를 위한 데이터는 요구사항에 맞춰 시간대별/구별/동별로 별도의 전용 테이블로 분리 저장하여 연산 부하를 제로(Zero)에 가깝게 만듭니다.

## ⚠️ User Review Required
- 이 최적화 작업은 새로운 데이터베이스 파일(`seoul_pops.db`)을 생성하기 위해 일회성 전처리 스크립트를 백그라운드에서 실행해야 합니다. 데이터베이스 생성이 완료된 후 대시보드 코드가 변경됩니다.
- SQLite DB를 사용하면 초기 로딩 속도와 필터 적용 속도가 **최대 10배 이상 비약적으로 향상**됩니다.
- 필터 적용 시 수학적인 평균(Mean of Means) 차이를 방지하기 위해, 원본 데이터에서 기준일(Day)에 대한 평균을 먼저 구하여 `agg_pop` 테이블에 저장합니다.

## 🛠 Proposed Changes

### 1. 데이터베이스 구축 스크립트 작성 (`seoul-pops/scripts/prep_sqlite.py`)
#### [NEW] [prep_sqlite.py](file:///c:/Users/user1/Downloads/ICB10_proj2/seoul-pops/scripts/prep_sqlite.py)
- 원본 `parquet` 파일과 매핑 엑셀을 읽어들여 3개의 집계 테이블을 생성하고 SQLite DB로 내보냅니다.
- **테이블 1 (`agg_pop`)**: 대시보드 일반 차트용. `['행정동코드', '성별', '연령대', '시간대구분']` 기준으로 평균 생활인구수를 집계. (850만행 -> 약 28만행으로 96% 압축)
- **테이블 2 (`map_dong`)**: 동별 지도 전용. `['시간대구분', '행정동코드']` 기준 집계.
- **테이블 3 (`map_gu`)**: 구별 지도 전용. `['시간대구분', 'GU_CD']` 기준 집계.

### 2. Streamlit Application & Utils 수정

#### [MODIFY] [utils.py](file:///c:/Users/user1/Downloads/ICB10_proj2/seoul-pops/src/utils.py)
- 기존 `pd.read_parquet` 로직을 제거하고, `sqlite3` 모듈을 이용해 `seoul_pops.db`에서 데이터를 불러오도록 `load_data()` 재작성.
- 지도 시각화를 위한 전용 쿼리 함수 `load_map_data_dong(time_filters)` 및 `load_map_data_gu(time_filters)` 추가.
- Streamlit의 `@st.cache_data`를 결합하여 DB 조회 결과 또한 메모리에 캐싱하여 극강의 속도 확보.

#### [MODIFY] [app.py](file:///c:/Users/user1/Downloads/ICB10_proj2/seoul-pops/src/app.py)
- 15개 시각화 차트는 최적화된 `agg_pop` 테이블을 기반으로 렌더링되도록 연결.
- 4번째 탭(지도 시각화)은 더 이상 복잡한 `merge` 연산이나 집계(groupby)를 런타임에 하지 않고, 새로 만든 `utils.load_map_data_...` 함수를 호출하여 즉시 코로플리스 맵에 바인딩.

## ✅ Verification Plan

### Automated/Manual Verification
- 터미널을 통해 `uv run python seoul-pops/scripts/prep_sqlite.py`를 실행하여 `.db` 파일이 정상 생성되는지 확인.
- DB 생성 완료 후 `app.py`를 실행하여 대시보드 진입 속도가 기존 대비 개선되었는지 확인.
- 필터 조건(성별, 시간대 등) 변경 후 "🚀 필터 적용하기" 버튼 클릭 시 지연 시간(Latency) 없이 차트와 지도가 즉시 갱신되는지 확인.
- Folium 맵의 데이터와 차트의 데이터가 기존 결과와 동일한 수치를 나타내는지 정합성 확인.
- 산출물을 `seoul-pops/docs`에 최종 백업.
