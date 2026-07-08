"""
이 모듈은 연남동 행정동 데이터만 필터링하여 
fg-data-profiling(ydata-profiling) 리포트를 생성합니다.
"""
import pandas as pd
from data_profiling import ProfileReport

print("Loading mapping info...")
mapping_df = pd.read_excel('seoul-pops/data/행정동코드_매핑정보_20241218.xlsx', header=1)

yeonnam_row = mapping_df[mapping_df['H_DNG_NM'] == '연남동']
if yeonnam_row.empty:
    raise ValueError("연남동을 매핑 파일에서 찾을 수 없습니다.")

yeonnam_code = int(yeonnam_row['H_DNG_CD'].values[0])
print(f"연남동 행정동코드: {yeonnam_code}")

print("Loading parquet data...")
df = pd.read_parquet('seoul-pops/data/LOCAL_PEOPLE_DONG_202606_optimized_final.parquet')

print("Filtering for 연남동...")
df_yeonnam = df[df['행정동코드'] == yeonnam_code]
print(f"Filtered rows: {len(df_yeonnam)}")

print("Generating profiling report...")
# 데이터 크기가 작으므로 minimal=False를 적용하여 상세한 프로파일링을 수행합니다.
profile = ProfileReport(df_yeonnam, title="Yeonnam-dong Profiling Report", minimal=False)
profile.to_file("seoul-pops/yeonnam_profiling_report.html")
print("Done. Report saved to seoul-pops/yeonnam_profiling_report.html")
