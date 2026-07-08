"""
문화체육관광부 추천여행지 데이터를 전처리하고 SQLite DB에 저장하는 스크립트입니다.
"""

import pandas as pd
import sqlite3
import os

def parse_location(x):
    """문자열을 시도, 시군구, 읍면동으로 분리하는 함수"""
    parts = str(x).strip().split()
    if len(parts) >= 3:
        return parts[0], parts[1], ' '.join(parts[2:])
    elif len(parts) == 2:
        return parts[0], parts[1], None
    elif len(parts) == 1:
        word = parts[0]
        if word[-1] in ['시', '군', '구']:
            return None, word, None
        else:
            return None, None, word
    else:
        return None, None, None

# 1. 파일 읽기
# 작업 디렉토리 기준 상대경로 (korea-trip-data 폴더 안이라고 가정)
file_path = 'data/문화체육관광부_추천여행지(20260602).csv'
if not os.path.exists(file_path):
    # 상위 경로에서 실행했을 경우 대응
    file_path = 'korea-trip-data/data/문화체육관광부_추천여행지(20260602).csv'

df = pd.read_csv(file_path, encoding='utf-8')

# 2. 결측치 제거 및 쉼표 기준으로 행 분리(explode)
df_tidy = df[['TITLE', 'SPATIALCOVERAGE']].copy()
df_tidy = df_tidy.dropna(subset=['SPATIALCOVERAGE'])
df_tidy['SPATIALCOVERAGE'] = df_tidy['SPATIALCOVERAGE'].astype(str).str.split(',')
df_tidy = df_tidy.explode('SPATIALCOVERAGE')

# 3. 별도 컬럼으로 분리 적용
parsed_cols = df_tidy['SPATIALCOVERAGE'].apply(parse_location).apply(pd.Series)
parsed_cols.columns = ['지역_시도', '지역_시군구', '지역_읍면동']
df_tidy = pd.concat([df_tidy, parsed_cols], axis=1)

# 4. 누락된 데이터 일괄 채우기 (Forward Fill 적용)
df_tidy['지역_시도'] = df_tidy.groupby(level=0)['지역_시도'].ffill()
df_tidy['지역_시군구'] = df_tidy.groupby(level=0)['지역_시군구'].ffill()

# 5. '지역_시도'와 '지역_시군구'를 '지역_시도시군구'로 병합 및 기존 컬럼 삭제
df_tidy['지역_시도시군구'] = df_tidy['지역_시도'].astype(str) + ' ' + df_tidy['지역_시군구'].astype(str)
# 'nan nan' 이나 결측치가 발생했을 경우 빈 값 처리
df_tidy['지역_시도시군구'] = df_tidy['지역_시도시군구'].replace('nan nan', None)
df_tidy = df_tidy.drop(columns=['지역_시도', '지역_시군구'])

# 보기 편하게 컬럼 순서 재배치
df_tidy = df_tidy[['TITLE', 'SPATIALCOVERAGE', '지역_시도시군구', '지역_읍면동']]

# 결과 출력
print("=== 전처리 완료 데이터 상위 6건 ===")
print(df_tidy.head(6))

# 6. SQLite DB로 저장
db_path = 'data/tourist_spots.db'
if not os.path.exists('data'):
    db_path = 'korea-trip-data/data/tourist_spots.db'

conn = sqlite3.connect(db_path)
df_tidy.to_sql('recommended_spots', conn, if_exists='replace', index=False)
conn.close()

print(f"\n성공적으로 SQLite DB에 저장되었습니다! (저장 위치: {db_path})")
