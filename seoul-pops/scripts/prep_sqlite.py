"""
이 스크립트는 850만 건의 서울 생활인구 Parquet 원본 데이터를 읽어들여 대시보드 구동에 필요한 최소 단위로 집계(Aggregation)하고, 이를 SQLite 데이터베이스에 저장하여 대시보드 로딩 및 처리 속도를 극대화합니다.
주요 기능:
- Parquet 로딩 및 행정동코드 매핑 정보 조인
- 대시보드 차트용 집계 테이블(agg_pop) 생성 (약 28만 건)
- 구별 지도 시각화 전용 집계 테이블(map_gu) 생성 (약 600 건)
- 동별 지도 시각화 전용 집계 테이블(map_dong) 생성 (약 1만 건)
"""

import pandas as pd
import sqlite3
import os

def prep_sqlite():
    # 파일 경로 설정
    BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    DATA_PATH = os.path.join(BASE_DIR, 'data', 'LOCAL_PEOPLE_DONG_202606_optimized_final.parquet')
    MAP_EXCEL_PATH = os.path.join(BASE_DIR, 'data', '행정동코드_매핑정보_20241218.xlsx')
    DB_PATH = os.path.join(BASE_DIR, 'data', 'seoul_pops.db')

    print(f"Reading parquet data from {DATA_PATH}...")
    df = pd.read_parquet(DATA_PATH)
    pop_col = '총생활인구수' if '총생활인구수' in df.columns else '생활인구수' if '생활인구수' in df.columns else df.columns[3]
    
    print("Reading mapping excel...")
    df_map = pd.read_excel(MAP_EXCEL_PATH)
    df_map.columns = df_map.iloc[0]
    df_map = df_map.drop(0).reset_index(drop=True)
    df_map['H_DNG_CD'] = df_map['H_DNG_CD'].astype(str)
    
    df['행정동코드'] = df['행정동코드'].astype(str)
    
    # 조인하여 통계청 행정동코드(H_SDNG_CD), 시군구명(CT_NM), 행정동명(H_DNG_NM) 가져오기
    print("Merging mapping data...")
    merged = df.merge(df_map, left_on='행정동코드', right_on='H_DNG_CD', how='inner')
    merged['GU_CD'] = merged['H_SDNG_CD'].astype(str).str[:5]

    print("Aggregating main dashboard table (agg_pop)...")
    # 대시보드 필터 조합: 행정동코드, 성별, 연령대, 시간대구분
    agg_pop = merged.groupby(['행정동코드', '성별', '연령대', '시간대구분', 'CT_NM', 'H_DNG_NM'])[pop_col].mean().reset_index()

    print("Aggregating dong map table (map_dong)...")
    # 동별 지도는 '시간대구분', 'H_SDNG_CD' 필요
    map_dong = merged.groupby(['시간대구분', 'H_SDNG_CD', 'H_DNG_NM'])[pop_col].mean().reset_index()

    print("Aggregating gu map table (map_gu)...")
    # 구별 지도는 '시간대구분', 'GU_CD' 필요
    map_gu = merged.groupby(['시간대구분', 'GU_CD', 'CT_NM'])[pop_col].mean().reset_index()

    print("Writing to SQLite DB...")
    # 만약 기존 db가 있다면 삭제하거나 덮어쓰기
    if os.path.exists(DB_PATH):
        os.remove(DB_PATH)
        
    conn = sqlite3.connect(DB_PATH)
    agg_pop.to_sql('agg_pop', conn, index=False, if_exists='replace')
    map_dong.to_sql('map_dong', conn, index=False, if_exists='replace')
    map_gu.to_sql('map_gu', conn, index=False, if_exists='replace')
    
    # 인덱스 추가를 통한 조회 성능 극대화
    cursor = conn.cursor()
    cursor.execute('CREATE INDEX idx_agg_pop ON agg_pop(행정동코드, 성별, 연령대, 시간대구분);')
    cursor.execute('CREATE INDEX idx_map_dong ON map_dong(시간대구분, H_SDNG_CD);')
    cursor.execute('CREATE INDEX idx_map_gu ON map_gu(시간대구분, GU_CD);')
    
    conn.commit()
    conn.close()
    
    print(f"Successfully created SQLite database at {DB_PATH}")

if __name__ == '__main__':
    prep_sqlite()
