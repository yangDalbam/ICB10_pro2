"""
이 모듈은 ydata-profiling 라이브러리를 사용하여
서울시 생활인구 파켓 데이터셋의 데이터 프로파일링 리포트(HTML)를 생성합니다.
"""
import pandas as pd
from data_profiling import ProfileReport

print("Loading data...")
df = pd.read_parquet('seoul-pops/data/LOCAL_PEOPLE_DONG_202606_optimized_final.parquet')

# Optional: To speed up, we can use minimal=True or take a sample.
# Given the 8.5 million rows, let's use minimal=True.
print("Generating profiling report...")
profile = ProfileReport(df, title="Seoul Pops Profiling Report", minimal=True)

print("Saving to HTML...")
profile.to_file("seoul-pops/profiling_report.html")
print("Done. Report saved to seoul-pops/profiling_report.html")
