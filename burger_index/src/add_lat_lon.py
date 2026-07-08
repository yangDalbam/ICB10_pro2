"""
이 모듈은 burger.csv 파일에서 시도시군구별 위도와 경도의 중간값을 계산하고,
이를 기존의 sigungu_crosstab.csv 파일의 버거지수 옆에 병합하여 저장합니다.
"""

import pandas as pd

burger_path = 'burger_index/data/burger.csv'
crosstab_path = 'burger_index/report/sigungu_crosstab.csv'

# 1. 원본 데이터 로드
df_burger = pd.read_csv(burger_path)
df_cross = pd.read_csv(crosstab_path)

# 2. 시도시군구명 생성
df_burger['시도시군구명'] = df_burger['시도명'] + ' ' + df_burger['시군구명']

# 3. 시도시군구명 그룹화 -> 위도, 경도 중간값 계산
geo_median = df_burger.groupby('시도시군구명')[['위도', '경도']].median().reset_index()

# 4. 기존 열 제거 (이미 존재하는 경우 덮어쓰기 위해)
if '위도' in df_cross.columns:
    df_cross.drop(columns=['위도'], inplace=True)
if '경도' in df_cross.columns:
    df_cross.drop(columns=['경도'], inplace=True)

# 5. sigungu_crosstab.csv와 병합 (left join)
df_merged = pd.merge(df_cross, geo_median, on='시도시군구명', how='left')

# 6. 컬럼 순서 재배치 (위도와 경도를 버거지수 옆에 배치)
cols = list(df_merged.columns)
cols.remove('위도')
cols.remove('경도')
idx = cols.index('버거지수')
cols.insert(idx + 1, '위도')
cols.insert(idx + 2, '경도')

df_merged = df_merged[cols]

# 7. 파일 저장 (utf-8-sig 인코딩)
df_merged.to_csv(crosstab_path, index=False, encoding='utf-8-sig')

print("위도 및 경도 중간값 추가 완료되었습니다.")
