"""
이 모듈은 서울시 생활인구 데이터를 분석하여 탐색적 데이터 분석(EDA)을 수행하는 기능을 합니다.
주요 기능:
- 데이터 로드 및 전처리
- 통계 지표 추출 및 요약
- 다양한 관점(성별, 연령대, 시간대)에서의 데이터 시각화
"""
import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib
import os
import io

os.makedirs('seoul-pops/images', exist_ok=True)
df = pd.read_parquet('seoul-pops/data/LOCAL_PEOPLE_DONG_202606_optimized_final.parquet')

# Replace column names manually to be sure they are correct, just in case
# The columns are likely: ['기준일ID', '시간대구분', '행정동코드', '총생활인구수', '성별', '연령대']
cols = ['기준일ID', '시간대구분', '행정동코드', '총생활인구수', '성별', '연령대']
if len(df.columns) == 6:
    df.columns = cols

with open('seoul-pops/eda_outputs.txt', 'w', encoding='utf-8') as f:
    f.write("=== 1. 기본 정보 ===\n")
    f.write(f"Shape: {df.shape}\n")
    
    buffer = io.StringIO()
    df.info(buf=buffer)
    f.write(buffer.getvalue())
    f.write("\n\n")
    
    f.write("=== 2. 상/하위 5개 행 ===\n")
    f.write("상위 5개:\n")
    f.write(df.head().to_string())
    f.write("\n\n하위 5개:\n")
    f.write(df.tail().to_string())
    f.write("\n\n")
    
    f.write("=== 3. 중복 데이터 ===\n")
    f.write(f"중복행 개수: {df.duplicated().sum()}\n\n")
    
    f.write("=== 4. 기술 통계 ===\n")
    f.write("수치형 변수:\n")
    f.write(df.describe().to_string())
    f.write("\n\n범주형 변수:\n")
    f.write(df.describe(include=['category', 'object']).to_string())
    f.write("\n\n")
    
    f.write("=== 5. 범주형 데이터 빈도수 (상위 30) ===\n")
    for col in ['성별', '연령대']:
        f.write(f"[{col}]\n")
        f.write(df[col].value_counts().head(30).to_string())
        f.write("\n\n")

# Start Plotting
# 1. Histogram of 총생활인구수
plt.figure(figsize=(10, 6))
# Sample data for histogram to avoid memory issues
plt.hist(df['총생활인구수'].sample(n=100000, random_state=42), bins=50, color='skyblue', edgecolor='black')
plt.title('총생활인구수 분포 (10만 샘플링)')
plt.xlabel('총생활인구수')
plt.ylabel('빈도')
plt.savefig('seoul-pops/images/plot1.png')
plt.close()

# 2. Gender frequency
plt.figure(figsize=(8, 5))
gender_counts = df['성별'].value_counts()
gender_counts.plot(kind='bar', color=['#ff9999','#66b3ff'])
plt.title('성별 빈도수')
plt.xlabel('성별')
plt.ylabel('빈도')
plt.xticks(rotation=0)
plt.savefig('seoul-pops/images/plot2.png')
plt.close()

# 3. Age frequency
plt.figure(figsize=(10, 6))
age_counts = df['연령대'].value_counts().sort_index()
age_counts.plot(kind='bar', color='lightgreen')
plt.title('연령대 빈도수')
plt.xlabel('연령대')
plt.ylabel('빈도')
plt.xticks(rotation=45)
plt.savefig('seoul-pops/images/plot3.png')
plt.close()

# 4. Average population by time
plt.figure(figsize=(10, 6))
time_mean = df.groupby('시간대구분')['총생활인구수'].mean()
time_mean.plot(kind='line', marker='o', color='purple')
plt.title('시간대별 평균 생활인구수')
plt.xlabel('시간대')
plt.ylabel('평균 생활인구수')
plt.grid(True, linestyle='--', alpha=0.6)
plt.savefig('seoul-pops/images/plot4.png')
plt.close()

# 5. Average population by gender
plt.figure(figsize=(8, 5))
gender_mean = df.groupby('성별')['총생활인구수'].mean()
gender_mean.plot(kind='bar', color=['#ff9999','#66b3ff'])
plt.title('성별 평균 생활인구수')
plt.xlabel('성별')
plt.ylabel('평균 생활인구수')
plt.xticks(rotation=0)
plt.savefig('seoul-pops/images/plot5.png')
plt.close()

# 6. Average population by age
plt.figure(figsize=(10, 6))
age_mean = df.groupby('연령대')['총생활인구수'].mean()
age_mean.plot(kind='bar', color='orange')
plt.title('연령대별 평균 생활인구수')
plt.xlabel('연령대')
plt.ylabel('평균 생활인구수')
plt.xticks(rotation=45)
plt.savefig('seoul-pops/images/plot6.png')
plt.close()

# 7. Time and Gender average population
plt.figure(figsize=(10, 6))
time_gender = df.pivot_table(index='시간대구분', columns='성별', values='총생활인구수', aggfunc='mean')
time_gender.plot(kind='line', marker='o', ax=plt.gca())
plt.title('시간대 및 성별 평균 생활인구수')
plt.xlabel('시간대')
plt.ylabel('평균 생활인구수')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(title='성별')
plt.savefig('seoul-pops/images/plot7.png')
plt.close()

# 8. Date trend
plt.figure(figsize=(12, 6))
date_sum = df.groupby('기준일ID')['총생활인구수'].sum()
date_sum.plot(kind='line', marker='x', color='brown')
plt.title('일자별 총 생활인구수 합계 추이')
plt.xlabel('일자 (기준일ID)')
plt.ylabel('총 생활인구수 합계')
plt.grid(True, linestyle='--', alpha=0.6)
plt.savefig('seoul-pops/images/plot8.png')
plt.close()

# 9. Time and Age heatmap approximation (using multiple lines for clarity)
plt.figure(figsize=(12, 8))
time_age = df.pivot_table(index='시간대구분', columns='연령대', values='총생활인구수', aggfunc='mean')
time_age.plot(kind='line', ax=plt.gca(), colormap='tab20')
plt.title('시간대 및 연령대별 평균 생활인구수')
plt.xlabel('시간대')
plt.ylabel('평균 생활인구수')
plt.legend(title='연령대', bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig('seoul-pops/images/plot9.png')
plt.close()

# 10. Date and Gender trend
plt.figure(figsize=(12, 6))
date_gender = df.pivot_table(index='기준일ID', columns='성별', values='총생활인구수', aggfunc='sum')
date_gender.plot(kind='line', marker='s', ax=plt.gca())
plt.title('일자 및 성별 총 생활인구수 합계 추이')
plt.xlabel('일자')
plt.ylabel('총 생활인구수 합계')
plt.grid(True, linestyle='--', alpha=0.6)
plt.legend(title='성별')
plt.savefig('seoul-pops/images/plot10.png')
plt.close()

# Write table data for plots
with open('seoul-pops/eda_tables.txt', 'w', encoding='utf-8') as f:
    f.write("=== Plot 4 Table ===\n")
    f.write(time_mean.to_string())
    f.write("\n\n=== Plot 5 Table ===\n")
    f.write(gender_mean.to_string())
    f.write("\n\n=== Plot 6 Table ===\n")
    f.write(age_mean.to_string())
    f.write("\n\n=== Plot 7 Pivot Table ===\n")
    f.write(time_gender.to_string())
    f.write("\n\n=== Plot 8 Table ===\n")
    f.write(date_sum.to_string())
    f.write("\n\n=== Plot 9 Pivot Table ===\n")
    f.write(time_age.to_string())
    f.write("\n\n=== Plot 10 Pivot Table ===\n")
    f.write(date_gender.to_string())
    f.write("\n")

print("EDA visualzation and table extraction complete.")
