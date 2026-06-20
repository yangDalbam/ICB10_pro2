"""
이 모듈은 외국인 관광객 관련 3개의 데이터셋(지역별 방문자 수, 거주지 국가 비율, 국적별 입국현황)을
통합적으로 분석하여 탐색적 데이터 분석(EDA) 보고서를 자동 생성하는 기능을 수행합니다.
주요 기능:
- 3종 데이터 로드 및 결측치, 중복치 등 기본 무결성 검증
- 교차표, 피봇 테이블 생성 및 기초 통계량 추출
- matplotlib과 koreanize_matplotlib을 활용한 10종 이상의 통계 시각화 생성(일변량, 이변량, 다변량 포함)
- 텍스트 데이터에 대한 TF-IDF 키워드 추출 및 시각화 적용
- 산출물을 바탕으로 마크다운(Markdown) 기반의 통합 리포트 초안 생성
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import koreanize_matplotlib
from sklearn.feature_extraction.text import TfidfVectorizer
import os

base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
data_dir = os.path.join(base_dir, 'data')
image_dir = os.path.join(base_dir, 'images')
report_dir = os.path.join(base_dir, 'report')

os.makedirs(image_dir, exist_ok=True)
os.makedirs(report_dir, exist_ok=True)

df_region_path = os.path.join(data_dir, '20260620154323_외국인 지역별 방문자 수 추이.csv')
df_residence_path = os.path.join(data_dir, '20260620154411_외국인 방문자 거주지(국가).csv')
df_entry_path = os.path.join(data_dir, '20260620155533_입국자 국적별 입국현황.csv')

df_region = pd.read_csv(df_region_path)
df_residence = pd.read_csv(df_residence_path)
df_entry = pd.read_csv(df_entry_path)

df_region['날짜'] = df_region['날짜'].astype(str)

out_md = []
out_md.append("# 외국인 방문자 데이터 통합 탐색적 데이터 분석(EDA) 및 검증\n")

# 1. 데이터 기본 정보
out_md.append("## 1. 데이터 기본 정보 및 검증\n")

def check_data(df, name):
    out_md.append(f"### {name} 데이터\n")
    out_md.append(f"- **전체 행/열**: {df.shape[0]} 행, {df.shape[1]} 열\n")
    out_md.append(f"- **중복 데이터 수**: {df.duplicated().sum()}\n")
    out_md.append(f"- **결측치 수**:\n```text\n{df.isnull().sum().to_string()}\n```\n")
    out_md.append(f"**상위 5개 행**\n\n{df.head().to_markdown()}\n\n")
    out_md.append(f"**하위 5개 행**\n\n{df.tail().to_markdown()}\n\n")
    
check_data(df_region, "지역별 방문자 수 추이")
check_data(df_residence, "방문자 거주지 비율")
check_data(df_entry, "국적별 입국현황")

# 2. 기술통계
out_md.append("## 2. 기술통계 및 상세 분석 보고서\n")

out_md.append("### 지역별 방문자 수 추이 - 기술통계\n")
out_md.append(f"{df_region.describe().to_markdown()}\n\n")
out_md.append(f"{df_region.describe(include=['object']).to_markdown()}\n\n")

out_md.append("### 방문자 거주지 비율 - 기술통계\n")
out_md.append(f"{df_residence.describe().to_markdown()}\n\n")
out_md.append(f"{df_residence.describe(include=['object']).to_markdown()}\n\n")

out_md.append("### 국적별 입국현황 - 기술통계\n")
out_md.append(f"{df_entry.describe().to_markdown()}\n\n")
out_md.append(f"{df_entry.describe(include=['object']).to_markdown()}\n\n")

out_md.append("<!-- REPORT_PLACEHOLDER_1 -->\n\n")

# 3. 데이터 시각화
out_md.append("## 3. 데이터 시각화 분석\n")

# Plot 1: 월별 방문자수 총합 추이 (일변량-시계열)
plt.figure(figsize=(10, 5))
df_region_total = df_region.groupby('날짜')['외국인 방문자수'].sum().reset_index()
plt.plot(df_region_total['날짜'], df_region_total['외국인 방문자수'], marker='o', color='teal')
plt.title("월별 전체 외국인 방문자 수 추이")
plt.xlabel("날짜")
plt.ylabel("방문자수")
plt.xticks(rotation=45)
plt.tight_layout()
plt.savefig(os.path.join(image_dir, "vplot1_total_trend.png"))
plt.close()

out_md.append("### 3.1 월별 전체 외국인 방문자 수 추이 (일변량)\n")
out_md.append("![월별 방문자 추이](../images/vplot1_total_trend.png)\n")
out_md.append("\n**월별 합계 데이터**\n")
out_md.append(f"{df_region_total.to_markdown(index=False)}\n")
out_md.append("\n<!-- DESC_PLACEHOLDER_1 -->\n\n")


# Plot 2: 지역별 총 방문자 수 (이변량)
plt.figure(figsize=(10, 6))
df_region_sum = df_region.groupby('지역')['외국인 방문자수'].sum().sort_values(ascending=True)
df_region_sum.plot(kind='barh', color='salmon')
plt.title("지역별 총 외국인 방문자 수")
plt.xlabel("총 방문자수")
plt.ylabel("지역")
plt.tight_layout()
plt.savefig(os.path.join(image_dir, "vplot2_region_sum.png"))
plt.close()

out_md.append("### 3.2 지역별 총 방문자 수 (이변량)\n")
out_md.append("![지역별 총 방문자 수](../images/vplot2_region_sum.png)\n")
out_md.append("\n**지역별 합계/평균 데이터**\n")
pivot_region = df_region.groupby('지역').agg({'외국인 방문자수': ['sum', 'mean']})
out_md.append(f"{pivot_region.to_markdown()}\n")
out_md.append("\n<!-- DESC_PLACEHOLDER_2 -->\n\n")


# Plot 3: 방문자수 분포 (일변량 히스토그램)
plt.figure(figsize=(10, 5))
plt.hist(df_region['외국인 방문자수'].dropna(), bins=20, color='lightblue', edgecolor='black')
plt.title("외국인 방문자 수 빈도 분포")
plt.xlabel("방문자수")
plt.ylabel("빈도")
plt.tight_layout()
plt.savefig(os.path.join(image_dir, "vplot3_region_hist.png"))
plt.close()

out_md.append("### 3.3 외국인 방문자 수 빈도 분포 (일변량)\n")
out_md.append("![방문자수 분포](../images/vplot3_region_hist.png)\n")
out_md.append("\n**통계량 요약**\n")
out_md.append(f"{df_region[['외국인 방문자수']].describe().to_markdown()}\n")
out_md.append("\n<!-- DESC_PLACEHOLDER_3 -->\n\n")


# Plot 4: 상위 5개 지역의 월별 추이 (다변량)
top5_regions = df_region_sum.tail(5).index
df_top5 = df_region[df_region['지역'].isin(top5_regions)]
pivot_top5 = df_top5.pivot(index='날짜', columns='지역', values='외국인 방문자수')
plt.figure(figsize=(12, 6))
pivot_top5.plot(kind='line', marker='o', ax=plt.gca())
plt.title("상위 5개 지역의 월별 방문자 수 추이")
plt.xlabel("날짜")
plt.ylabel("방문자수")
plt.legend(bbox_to_anchor=(1.05, 1), loc='upper left')
plt.tight_layout()
plt.savefig(os.path.join(image_dir, "vplot4_top5_trend.png"))
plt.close()

out_md.append("### 3.4 상위 5개 지역 월별 방문자 수 추이 (다변량)\n")
out_md.append("![상위 5개 지역 추이](../images/vplot4_top5_trend.png)\n")
out_md.append("\n**상위 5개 지역 피봇 테이블**\n")
out_md.append(f"{pivot_top5.to_markdown()}\n")
out_md.append("\n<!-- DESC_PLACEHOLDER_4 -->\n\n")


# Plot 5: 지역별 박스플롯 (이변량)
plt.figure(figsize=(12, 6))
df_region.boxplot(column='외국인 방문자수', by='지역', grid=False, ax=plt.gca())
plt.title("지역별 방문자 수 분포 (Boxplot)")
plt.suptitle("")
plt.xticks(rotation=45)
plt.ylabel("방문자수")
plt.tight_layout()
plt.savefig(os.path.join(image_dir, "vplot5_region_boxplot.png"))
plt.close()

out_md.append("### 3.5 지역별 방문자 수 Boxplot (이변량)\n")
out_md.append("![지역별 박스플롯](../images/vplot5_region_boxplot.png)\n")
out_md.append("\n**분포 요약표 (사분위수)**\n")
out_md.append(f"{df_region.groupby('지역')['외국인 방문자수'].describe()[['min', '25%', '50%', '75%', 'max']].to_markdown()}\n")
out_md.append("\n<!-- DESC_PLACEHOLDER_5 -->\n\n")


# Plot 6: 거주지 국가 상위 10개국 비율 (일변량)
plt.figure(figsize=(8, 8))
top10_residence = df_residence[df_residence['국가명'] != '기타'].sort_values('비율(%)', ascending=False).head(10)
plt.pie(top10_residence['비율(%)'], labels=top10_residence['국가명'], autopct='%1.1f%%', startangle=140)
plt.title("상위 10개국 거주지 비율")
plt.tight_layout()
plt.savefig(os.path.join(image_dir, "vplot6_residence_pie.png"))
plt.close()

out_md.append("### 3.6 거주지 상위 10개국 비율 (일변량-범주형)\n")
out_md.append("![거주지 상위 10개국](../images/vplot6_residence_pie.png)\n")
out_md.append("\n**상위 10개국 비율 표**\n")
out_md.append(f"{top10_residence.to_markdown(index=False)}\n")
out_md.append("\n<!-- DESC_PLACEHOLDER_6 -->\n\n")


# Plot 7: 입국자 국적별 입국자 수 막대 그래프 (일변량)
plt.figure(figsize=(10, 6))
df_entry_sorted = df_entry.sort_values('입국자 수(명)', ascending=True)
plt.barh(df_entry_sorted['입국자 국적'], df_entry_sorted['입국자 수(명)'], color='mediumpurple')
plt.title("국적별 입국자 수 현황")
plt.xlabel("입국자 수(명)")
plt.tight_layout()
plt.savefig(os.path.join(image_dir, "vplot7_entry_barh.png"))
plt.close()

out_md.append("### 3.7 국적별 입국자 수 현황 (일변량)\n")
out_md.append("![국적별 입국자 수](../images/vplot7_entry_barh.png)\n")
out_md.append("\n**입국자 현황 원본 표**\n")
out_md.append(f"{df_entry_sorted[['입국자 국적', '입국자 수(명)']].to_markdown(index=False)}\n")
out_md.append("\n<!-- DESC_PLACEHOLDER_7 -->\n\n")


# Plot 8: 시간 및 지역 피봇 히트맵 (다변량)
plt.figure(figsize=(10, 8))
heatmap_data = df_region.pivot(index='지역', columns='날짜', values='외국인 방문자수')
plt.pcolor(heatmap_data, cmap='Oranges')
plt.yticks(np.arange(0.5, len(heatmap_data.index), 1), heatmap_data.index)
plt.xticks(np.arange(0.5, len(heatmap_data.columns), 1), heatmap_data.columns, rotation=45)
plt.colorbar(label='방문자수')
plt.title("지역별 월별 방문자 수 히트맵")
plt.tight_layout()
plt.savefig(os.path.join(image_dir, "vplot8_region_heatmap.png"))
plt.close()

out_md.append("### 3.8 지역별 월별 방문자 수 히트맵 (다변량)\n")
out_md.append("![히트맵](../images/vplot8_region_heatmap.png)\n")
out_md.append("\n**히트맵 피봇 데이터**\n")
out_md.append(f"{heatmap_data.to_markdown()}\n")
out_md.append("\n<!-- DESC_PLACEHOLDER_8 -->\n\n")


# Plot 9: 지역명 카테고리 빈도수 (일변량)
plt.figure(figsize=(8, 6))
region_counts = df_region['지역'].value_counts()
region_counts.plot(kind='bar', color='gray')
plt.title("지역별 데이터 빈도수 (월별 데이터 건수)")
plt.xlabel("지역")
plt.ylabel("건수")
plt.tight_layout()
plt.savefig(os.path.join(image_dir, "vplot9_region_freq.png"))
plt.close()

out_md.append("### 3.9 지역 데이터 빈도수 (범주형 일변량)\n")
out_md.append("![지역 빈도](../images/vplot9_region_freq.png)\n")
out_md.append("\n**지역별 빈도 요약**\n")
out_md.append(f"{region_counts.to_frame('데이터 건수').to_markdown()}\n")
out_md.append("\n<!-- DESC_PLACEHOLDER_9 -->\n\n")


# Plot 10: 텍스트 TF-IDF 중요도 분석 (국가명 대상)
# df_entry의 '입국자 국적' 사용
vectorizer = TfidfVectorizer(max_features=30)
tfidf_matrix = vectorizer.fit_transform(df_entry['입국자 국적'])
feature_names = vectorizer.get_feature_names_out()
tfidf_sum = tfidf_matrix.sum(axis=0).A1
tfidf_df = pd.DataFrame({'키워드(국적)': feature_names, 'TF-IDF 중요도': tfidf_sum}).sort_values(by='TF-IDF 중요도', ascending=True)

plt.figure(figsize=(10, 6))
plt.barh(tfidf_df['키워드(국적)'], tfidf_df['TF-IDF 중요도'], color='gold')
plt.title("국적명 텍스트 TF-IDF 키워드 분석")
plt.xlabel("TF-IDF 가중치")
plt.tight_layout()
plt.savefig(os.path.join(image_dir, "vplot10_tfidf_nationality.png"))
plt.close()

out_md.append("### 3.10 입국 국적명 텍스트 TF-IDF 중요도 분석\n")
out_md.append("![TF-IDF 국적명](../images/vplot10_tfidf_nationality.png)\n")
out_md.append("\n**TF-IDF 상위 중요도 테이블**\n")
out_md.append(f"{tfidf_df.sort_values(by='TF-IDF 중요도', ascending=False).to_markdown(index=False)}\n")
out_md.append("\n<!-- DESC_PLACEHOLDER_10 -->\n\n")

# Write final output
with open(os.path.join(report_dir, 'eda_visitor_report.md'), 'w', encoding='utf-8') as f:
    f.write('\n'.join(out_md))

print("EDA Visitor Analysis complete. Report generated at report/eda_visitor_report.md")
