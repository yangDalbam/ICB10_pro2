"""
이 모듈은 제공된 두 개의 관광 데이터(업종별 소비액 추이 및 국가별 소비 비율)를 통합적으로 분석하여 
탐색적 데이터 분석(EDA) 보고서를 자동 생성하는 기능을 수행합니다.
주요 기능:
- 데이터 로드 및 결측치/중복치 등 기본 검증 수행
- 교차표, 피봇 테이블, 범주형 및 수치형 변수에 대한 기술 통계 추출
- matplotlib 및 koreanize-matplotlib를 활용한 10개 이상의 시각화 그래프 생성 (일변량, 이변량, 다변량 포함)
- TF-IDF를 이용한 텍스트 데이터 중요 키워드 시각화
- 산출물을 바탕으로 마크다운(Markdown) 기반의 통합 리포트 파일 초안 생성
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import koreanize_matplotlib
from sklearn.feature_extraction.text import TfidfVectorizer
import os

# Set paths
base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, 'data')
image_dir = os.path.join(base_dir, 'images')
report_dir = os.path.join(base_dir, 'report')

os.makedirs(image_dir, exist_ok=True)
os.makedirs(report_dir, exist_ok=True)

df1_path = os.path.join(data_dir, '20260620155141_업종별 관광소비 추이 CSV 다운로드.csv')
df2_path = os.path.join(data_dir, '20260620155314_국가별 관광소비 유형 CSV 다운로드.csv')

df_industry = pd.read_csv(df1_path)
df_country = pd.read_csv(df2_path)

# Convert 기준년월일 to string then datetime if possible, but keeping as string is fine for now
df_industry['기준년월일'] = df_industry['기준년월일'].astype(str)

out_md = []
out_md.append("# 관광 데이터 통합 탐색적 데이터 분석(EDA) 및 데이터 검증 결과\n")

# 1. 데이터 기본 정보
out_md.append("## 1. 데이터 기본 정보 및 검증\n")

def check_data(df, name):
    out_md.append(f"### {name} 데이터\n")
    out_md.append(f"- **전체 행/열**: {df.shape[0]} 행, {df.shape[1]} 열\n")
    out_md.append(f"- **중복 데이터 수**: {df.duplicated().sum()}\n")
    out_md.append(f"- **결측치 수**:\n```text\n{df.isnull().sum().to_string()}\n```\n")
    
    out_md.append(f"**상위 5개 행**\n\n{df.head().to_markdown()}\n\n")
    out_md.append(f"**하위 5개 행**\n\n{df.tail().to_markdown()}\n\n")
    
check_data(df_industry, "업종별 관광소비 추이")
check_data(df_country, "국가별 관광소비 비율")

# 2. 기술통계
out_md.append("## 2. 기술통계 및 상세 분석 보고서\n")

# 분리: 수치형과 범주형
out_md.append("### 업종별 관광소비 추이 - 기술통계\n")
out_md.append("#### 수치형 변수\n")
out_md.append(f"{df_industry.describe().to_markdown()}\n\n")
out_md.append("#### 범주형 변수\n")
out_md.append(f"{df_industry.describe(include=['object']).to_markdown()}\n\n")

out_md.append("### 국가별 관광소비 비율 - 기술통계\n")
out_md.append("#### 수치형 변수\n")
out_md.append(f"{df_country.describe().to_markdown()}\n\n")
out_md.append("#### 범주형 변수\n")
out_md.append(f"{df_country.describe(include=['object']).to_markdown()}\n\n")

out_md.append("<!-- REPORT_PLACEHOLDER_1 -->\n\n")

# 3. 데이터 시각화
out_md.append("## 3. 데이터 시각화 분석\n")

# Plot 1: 연월별 소비액 총합 (전체)
plt.figure(figsize=(10, 5))
df_total = df_industry[df_industry['업종별 구분'] == '전체'].sort_values('기준년월일')
plt.plot(df_total['기준년월일'], df_total['소비액(천원)'], marker='o')
plt.title("월별 전체 관광소비 추이")
plt.xlabel("연월")
plt.ylabel("소비액(천원)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(image_dir, "plot1_total_trend.png"))
plt.close()

out_md.append("### 3.1 월별 전체 관광소비 추이 (일변량-시계열)\n")
out_md.append("![월별 전체 관광소비 추이](../images/plot1_total_trend.png)\n")
out_md.append("\n**관련 교차표/피봇테이블**\n")
out_md.append(f"{df_total[['기준년월일', '소비액(천원)']].to_markdown(index=False)}\n")
out_md.append("\n<!-- DESC_PLACEHOLDER_1 -->\n\n")


# Plot 2: 소비액 분포 (업종별 제외, '전체' 제외)
plt.figure(figsize=(10, 5))
df_sub = df_industry[df_industry['업종별 구분'] != '전체']
plt.hist(df_sub['소비액(천원)'], bins=20, color='skyblue', edgecolor='black')
plt.title("업종별 소비액(천원) 빈도 분포")
plt.xlabel("소비액(천원)")
plt.ylabel("빈도수")
plt.tight_layout()
plt.savefig(os.path.join(image_dir, "plot2_hist_consumption.png"))
plt.close()

out_md.append("### 3.2 업종별 소비액 빈도 분포 (일변량)\n")
out_md.append("![업종별 소비액 분포](../images/plot2_hist_consumption.png)\n")
out_md.append("\n**기술 통계표**\n")
out_md.append(f"{df_sub[['소비액(천원)']].describe().to_markdown()}\n")
out_md.append("\n<!-- DESC_PLACEHOLDER_2 -->\n\n")


# Plot 3: 업종별 평균 소비액 (이변량)
plt.figure(figsize=(10, 5))
ind_mean = df_sub.groupby('업종별 구분')['소비액(천원)'].mean().sort_values(ascending=False)
ind_mean.plot(kind='bar', color='coral')
plt.title("업종별 평균 소비액")
plt.xlabel("업종")
plt.ylabel("평균 소비액(천원)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(image_dir, "plot3_mean_by_industry.png"))
plt.close()

out_md.append("### 3.3 업종별 평균 소비액 (이변량)\n")
out_md.append("![업종별 평균 소비액](../images/plot3_mean_by_industry.png)\n")
out_md.append("\n**교차표/피봇테이블 (업종별 평균/합계 소비액)**\n")
pivot_ind = df_sub.groupby('업종별 구분').agg({'소비액(천원)': ['mean', 'sum', 'count']})
out_md.append(f"{pivot_ind.to_markdown()}\n")
out_md.append("\n<!-- DESC_PLACEHOLDER_3 -->\n\n")


# Plot 4: 업종별 월별 소비 추이 (다변량)
plt.figure(figsize=(12, 6))
pivot_trend = df_sub.pivot(index='기준년월일', columns='업종별 구분', values='소비액(천원)')
pivot_trend.plot(kind='line', marker='o', ax=plt.gca())
plt.title("업종별 월별 관광소비 추이")
plt.xlabel("연월")
plt.ylabel("소비액(천원)")
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(image_dir, "plot4_trend_by_industry.png"))
plt.close()

out_md.append("### 3.4 업종별 월별 관광소비 추이 (다변량)\n")
out_md.append("![업종별 월별 관광소비 추이](../images/plot4_trend_by_industry.png)\n")
out_md.append("\n**피봇테이블**\n")
out_md.append(f"{pivot_trend.to_markdown()}\n")
out_md.append("\n<!-- DESC_PLACEHOLDER_4 -->\n\n")


# Plot 5: 소비액 기준 상위 5개 국가 소비 비율 (일변량/범주)
plt.figure(figsize=(8, 8))
top_countries = df_country[df_country['국가'] != '기타'].sort_values('소비 비율', ascending=False).head(10)
plt.pie(top_countries['소비 비율'], labels=top_countries['국가'], autopct='%1.1f%%', startangle=140)
plt.title("상위 10개국 관광소비 비율")
plt.tight_layout()
plt.savefig(os.path.join(image_dir, "plot5_pie_top10_countries.png"))
plt.close()

out_md.append("### 3.5 상위 10개국 관광소비 비율 (일변량-범주형)\n")
out_md.append("![상위 10개국 관광소비 비율](../images/plot5_pie_top10_countries.png)\n")
out_md.append("\n**상위 10개국 데이터 요약**\n")
out_md.append(f"{top_countries.to_markdown(index=False)}\n")
out_md.append("\n<!-- DESC_PLACEHOLDER_5 -->\n\n")


# Plot 6: 국가별 소비비율 분포 (일변량)
plt.figure(figsize=(10, 5))
plt.hist(df_country['소비 비율'], bins=15, color='lightgreen', edgecolor='black')
plt.title("국가별 소비 비율 빈도 분포")
plt.xlabel("소비 비율(%)")
plt.ylabel("국가 수")
plt.tight_layout()
plt.savefig(os.path.join(image_dir, "plot6_hist_country_ratio.png"))
plt.close()

out_md.append("### 3.6 국가별 소비 비율 분포 (일변량)\n")
out_md.append("![국가별 소비 비율 분포](../images/plot6_hist_country_ratio.png)\n")
out_md.append("\n**기술 통계표**\n")
out_md.append(f"{df_country[['소비 비율']].describe().to_markdown()}\n")
out_md.append("\n<!-- DESC_PLACEHOLDER_6 -->\n\n")


# Plot 7: 업종별 박스플롯 (이변량)
plt.figure(figsize=(10, 6))
df_sub.boxplot(column='소비액(천원)', by='업종별 구분', grid=False, ax=plt.gca())
plt.title("업종별 소비액 분포 (Boxplot)")
plt.suptitle("")
plt.xlabel("업종별 구분")
plt.ylabel("소비액(천원)")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(image_dir, "plot7_boxplot_industry.png"))
plt.close()

out_md.append("### 3.7 업종별 소비액 Boxplot (이변량)\n")
out_md.append("![업종별 소비액 Boxplot](../images/plot7_boxplot_industry.png)\n")
out_md.append("\n**관련 통계 (최댓값, 최솟값, 중앙값)**\n")
boxplot_stats = df_sub.groupby('업종별 구분')['소비액(천원)'].describe()[['min', '25%', '50%', '75%', 'max']]
out_md.append(f"{boxplot_stats.to_markdown()}\n")
out_md.append("\n<!-- DESC_PLACEHOLDER_7 -->\n\n")


# Plot 8: 업종과 시간 피봇 히트맵 (다변량 대체 - 막대그래프로 구현, 히트맵은 seaborn이 없어도 가능하나 plt.pcolor사용)
plt.figure(figsize=(10, 6))
heatmap_data = df_sub.pivot(index='업종별 구분', columns='기준년월일', values='소비액(천원)')
plt.pcolor(heatmap_data, cmap='Blues')
plt.yticks(np.arange(0.5, len(heatmap_data.index), 1), heatmap_data.index)
plt.xticks(np.arange(0.5, len(heatmap_data.columns), 1), heatmap_data.columns, rotation=45)
plt.colorbar(label='소비액(천원)')
plt.title("업종별 월별 관광소비액 히트맵")
plt.tight_layout()
plt.savefig(os.path.join(image_dir, "plot8_heatmap_industry_time.png"))
plt.close()

out_md.append("### 3.8 업종별 월별 관광소비액 히트맵 (다변량)\n")
out_md.append("![업종별 월별 관광소비액 히트맵](../images/plot8_heatmap_industry_time.png)\n")
out_md.append("\n**피봇테이블**\n")
out_md.append(f"{heatmap_data.to_markdown()}\n")
out_md.append("\n<!-- DESC_PLACEHOLDER_8 -->\n\n")


# Plot 9: 전체 소비액 대 업종 수 비율 (이변량/교차)
plt.figure(figsize=(8, 6))
industry_counts = df_sub['업종별 구분'].value_counts()
industry_counts.plot(kind='bar', color='mediumpurple')
plt.title("업종별 데이터 빈도수 (월별 수집 건수)")
plt.xlabel("업종별 구분")
plt.ylabel("수집 건수(개월 수)")
plt.tight_layout()
plt.savefig(os.path.join(image_dir, "plot9_bar_industry_freq.png"))
plt.close()

out_md.append("### 3.9 범주형 데이터(업종) 빈도 분포 (일변량)\n")
out_md.append("![업종 빈도수](../images/plot9_bar_industry_freq.png)\n")
out_md.append("\n**빈도표**\n")
out_md.append(f"{industry_counts.to_frame('빈도').to_markdown()}\n")
out_md.append("\n<!-- DESC_PLACEHOLDER_9 -->\n\n")

# Plot 10: TF-IDF 국가명 추출 (요구사항: 텍스트 TF-IDF 상위 30개 시각화)
vectorizer = TfidfVectorizer(max_features=30)
tfidf_matrix = vectorizer.fit_transform(df_country['국가'])
feature_names = vectorizer.get_feature_names_out()
tfidf_sum = tfidf_matrix.sum(axis=0).A1
tfidf_df = pd.DataFrame({'키워드': feature_names, 'TF-IDF 합계': tfidf_sum}).sort_values(by='TF-IDF 합계', ascending=False)

plt.figure(figsize=(10, 8))
plt.barh(tfidf_df['키워드'][::-1], tfidf_df['TF-IDF 합계'][::-1], color='orange')
plt.title("국가명 대상 TF-IDF 키워드 상위 30개 추출")
plt.xlabel("TF-IDF 중요도")
plt.tight_layout()
plt.savefig(os.path.join(image_dir, "plot10_tfidf_country.png"))
plt.close()

out_md.append("### 3.10 텍스트 데이터 TF-IDF 분석: 국가명 상위 키워드\n")
out_md.append("![TF-IDF 국가명](../images/plot10_tfidf_country.png)\n")
out_md.append("\n**TF-IDF 키워드 상위 테이블**\n")
out_md.append(f"{tfidf_df.to_markdown(index=False)}\n")
out_md.append("\n<!-- DESC_PLACEHOLDER_10 -->\n\n")

# Plot 11: 모든 국가 소비비율 수평 막대 그래프 (전체 비교)
plt.figure(figsize=(10, 10))
df_country_sorted = df_country.sort_values('소비 비율', ascending=True)
plt.barh(df_country_sorted['국가'], df_country_sorted['소비 비율'], color='teal')
plt.title("전체 국가별 소비 비율 분포도")
plt.xlabel("소비 비율(%)")
plt.tight_layout()
plt.savefig(os.path.join(image_dir, "plot11_barh_all_countries.png"))
plt.close()

out_md.append("### 3.11 전체 국가별 소비 비율 수평 막대그래프 (이변량)\n")
out_md.append("![전체 국가 소비비율](../images/plot11_barh_all_countries.png)\n")
out_md.append("\n**전체 국가별 소비비율 데이터**\n")
out_md.append(f"{df_country_sorted.to_markdown(index=False)}\n")
out_md.append("\n<!-- DESC_PLACEHOLDER_11 -->\n\n")


# Write final output
with open(os.path.join(report_dir, 'eda_integrated_report.md'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(out_md))

print("EDA Analysis complete. Report generated at report/eda_integrated_report.md")
