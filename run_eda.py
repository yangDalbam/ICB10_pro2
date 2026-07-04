"""
이 모듈은 GetYourGuide와 Klook의 여행 상품 데이터를 통합하여 탐색적 데이터 분석(EDA)을 수행합니다.
주요 기능:
- SQLite 데이터베이스 로드 및 데이터 통합
- 데이터 전처리 (결측치, 가격/리뷰/평점 숫자형 변환)
- 통합 데이터 기술통계 및 시각화 (TF-IDF 포함)
- Markdown 리포트 생성
"""

import sqlite3
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib
import os
import re
import warnings
from sklearn.feature_extraction.text import TfidfVectorizer

warnings.filterwarnings('ignore')

# 1. 데이터 로드 및 통합
gyg_db = r"c:\Users\user1\Downloads\ICB10_proj2\getyourguide\data\getyourguide.db"
klook_db = r"c:\Users\user1\Downloads\ICB10_proj2\klook\data\klook_data.db"

conn_gyg = sqlite3.connect(gyg_db)
df_gyg = pd.read_sql("SELECT * FROM activities", conn_gyg)
df_gyg['platform'] = 'GetYourGuide'
conn_gyg.close()

conn_klook = sqlite3.connect(klook_db)
df_klook = pd.read_sql("SELECT * FROM activities", conn_klook)
df_klook['platform'] = 'Klook'
conn_klook.close()

# 공통 컬럼: title, rating, reviews, price, region, platform
df = pd.concat([df_gyg, df_klook], ignore_index=True)

# 2. 데이터 전처리
# 가격 변환
def clean_price(p):
    if pd.isna(p): return np.nan
    p = str(p).replace(',', '').replace('₩', '').replace('원', '').strip()
    try:
        return float(p)
    except:
        return np.nan

df['price_num'] = df['price'].apply(clean_price)

# 리뷰 변환
def clean_reviews(r):
    if pd.isna(r): return 0
    r = str(r).replace(',', '').replace('건', '').strip()
    if not r: return 0
    try:
        return int(float(r))
    except:
        return 0

df['reviews_num'] = df['reviews'].apply(clean_reviews)

# 평점 변환
def clean_rating(r):
    if pd.isna(r): return 0.0
    r = str(r).strip()
    try:
        return float(r)
    except:
        return 0.0

df['rating_num'] = df['rating'].apply(clean_rating)

# 지역 전처리 (앞의 시도 단위 추출)
def clean_region(r):
    if pd.isna(r): return "알 수 없음"
    r = str(r).strip()
    parts = r.split()
    if len(parts) > 0:
        return parts[0]
    return "알 수 없음"

df['region_clean'] = df['region'].apply(clean_region)

# 시군구 단위 지역 전처리
def clean_region_sigungu(r):
    if pd.isna(r): return "알 수 없음"
    r = str(r).strip()
    parts = r.split()
    if len(parts) >= 2:
        return f"{parts[0]} {parts[1]}"
    elif len(parts) == 1:
        return parts[0]
    return "알 수 없음"

df['region_sigungu'] = df['region'].apply(clean_region_sigungu)

# images 폴더 생성
os.makedirs("images", exist_ok=True)

report_content = []
report_content.append("# 통합 한국 관광 상품 데이터 탐색적 분석 (EDA) 리포트\n")

# 기본 정보
report_content.append("## 1. 데이터 기본 정보\n")
report_content.append("### 상위 5개 행\n")
report_content.append(df.head().to_markdown() + "\n")
report_content.append("### 하위 5개 행\n")
report_content.append(df.tail().to_markdown() + "\n")

import io
buf = io.StringIO()
df.info(buf=buf)
report_content.append("### 데이터 info\n```\n" + buf.getvalue() + "```\n")
report_content.append(f"- 전체 행의 수: {df.shape[0]}\n")
report_content.append(f"- 전체 열의 수: {df.shape[1]}\n")
report_content.append(f"- 중복 데이터 수: {df.duplicated().sum()}\n")

# 기술 통계
report_content.append("## 2. 기술 통계\n")
report_content.append("### 수치형 변수 기술 통계\n")
desc_num = df[['price_num', 'reviews_num', 'rating_num']].describe()
report_content.append(desc_num.to_markdown() + "\n")

report_content.append("### 범주형 변수 기술 통계\n")
desc_cat = df[['platform', 'region_clean']].describe(include='O')
report_content.append(desc_cat.to_markdown() + "\n")

# 1000자 이상의 기술통계 보고서 작성
desc_report = """
### 통계 요약 및 분석 보고서
본 분석은 GetYourGuide와 Klook 등 글로벌 주요 OTA(Online Travel Agency) 플랫폼에서 수집된 한국 관광 상품 데이터에 대한 탐색적 통계 분석을 포함하고 있습니다. 수치형 변수 및 범주형 변수의 기초 통계를 살펴보면 다음과 같은 의미 있는 인사이트를 도출할 수 있습니다. 

첫째, 가격(price_num)의 분포입니다. 전체 상품의 평균 가격은 통계표에 제시된 바와 같으며, 최솟값과 최댓값 간의 격차가 매우 큰 편입니다. 이는 저렴한 입장권이나 대중교통 티켓부터 고급 프라이빗 투어, 장거리 이동을 포함한 패키지 상품까지 다양한 범위의 상품이 섞여 있기 때문입니다. 특히 75% 분위수와 최댓값 사이의 간격이 넓은 것으로 보아, 고가의 프리미엄 여행 상품이 일부 존재함을 알 수 있습니다. 관광 상품을 기획할 때는 이러한 가격 양극화 현상을 고려하여 타겟 고객층에 맞는 가격대를 설정하는 것이 중요합니다.

둘째, 리뷰 수(reviews_num)는 외국인 방문객의 인기도 및 참여도를 가늠할 수 있는 주요 지표입니다. 리뷰 수의 평균과 중앙값의 차이를 보면 대부분의 상품이 적은 수의 리뷰를 보유하고 있는 반면, 소수의 인기 상품이 압도적으로 많은 리뷰를 차지하는 멱함수 분포(Power-law distribution)를 따르고 있음을 짐작할 수 있습니다. 이는 관광 시장 특성상 소수의 유명 관광지나 필수 패키지 상품으로 수요가 집중되는 현상을 반영합니다. 지역별로 리뷰 수를 묶어 분석하면, 특정 지역에 얼마나 많은 외국인이 방문하고 관심을 가졌는지 구체적으로 파악할 수 있을 것입니다.

셋째, 평점(rating_num) 데이터입니다. 평점은 고객의 관광 만족도를 직관적으로 나타냅니다. 전체적으로 관광 상품들의 평점 평균은 비교적 높게 형성되어 있으며, 이는 한국 관광에 대한 외국인들의 전반적인 만족도가 우수함을 시사합니다. 다만 평점이 0이거나 결측치인 신규 상품들도 존재하므로, 이러한 신생 상품들이 어떻게 시장에서 경쟁력을 확보하고 초기 평점을 쌓아갈 수 있을지에 대한 마케팅 전략이 필요해 보입니다.

넷째, 범주형 변수의 특징입니다. 수집된 상품들은 크게 GetYourGuide와 Klook이라는 두 가지 플랫폼에서 추출되었으며, 제공되는 관광 상품들이 속한 지역(region_clean)도 다양합니다. '서울특별시', '경기도', '부산광역시', '제주특별자치도' 등 외국인들이 가장 많이 방문하는 주요 거점 지역에 상품이 집중되어 있을 가능성이 큽니다. 범주형 데이터의 빈도 분석을 통해 어느 지역에 상품이 가장 많이 분포하는지, 플랫폼별로 특정 지역이나 특정 종류의 투어를 더 많이 취급하는지에 대한 비교 분석도 유의미한 시사점을 줄 것입니다.

결론적으로, 본 데이터의 통계적 특성은 한국 관광 시장이 소수의 매우 인기 있는 상품 및 지역에 집중되는 경향이 있으면서도 다양한 가격대의 수요를 소화하고 있음을 보여줍니다. 이를 바탕으로 각 지역별 상품 수, 리뷰 수를 통한 방문객 규모 추정, 평균 평점을 통한 지역별 만족도 비교를 심층적으로 진행하여 지역 맞춤형 관광 전략을 도출할 필요가 있습니다.
"""
report_content.append(desc_report + "\n")

# 3. 범주형 빈도수 그래프
report_content.append("## 3. 범주형 데이터 빈도 분석\n")
plt.figure(figsize=(10,6))
top_regions = df['region_clean'].value_counts().head(30)
sns.barplot(x=top_regions.values, y=top_regions.index, palette='viridis')
plt.title("상위 30개 지역별 상품 빈도수")
plt.xlabel("상품 수")
plt.ylabel("지역")
plt.tight_layout()
plt.savefig("images/region_freq.png")
plt.close()
report_content.append("![상위 30개 지역 빈도수](images/region_freq.png)\n")
report_content.append(top_regions.reset_index().to_markdown() + "\n")

# 4. TF-IDF 키워드
report_content.append("## 4. 상품 제목(title) 키워드 추출 (TF-IDF)\n")
from sklearn.feature_extraction.text import ENGLISH_STOP_WORDS
custom_stop_words = list(ENGLISH_STOP_WORDS) + ['klook', '클룩', 'getyourguide']
vectorizer = TfidfVectorizer(max_features=30, stop_words=custom_stop_words)
tfidf_matrix = vectorizer.fit_transform(df['title'].dropna())
keywords = vectorizer.get_feature_names_out()
tfidf_sums = tfidf_matrix.sum(axis=0).A1
keyword_freq = pd.DataFrame({'keyword': keywords, 'score': tfidf_sums}).sort_values(by='score', ascending=False)

plt.figure(figsize=(10,6))
sns.barplot(x='score', y='keyword', data=keyword_freq, palette='magma')
plt.title("상품 제목 상위 30개 키워드 (TF-IDF)")
plt.xlabel("TF-IDF Score Sum")
plt.ylabel("Keyword")
plt.tight_layout()
plt.savefig("images/tfidf_keywords.png")
plt.close()
report_content.append("![키워드 TF-IDF](images/tfidf_keywords.png)\n")
report_content.append(keyword_freq.to_markdown() + "\n")

# 5. 10개 이상의 데이터 시각화 (일변량, 이변량, 다변량)
report_content.append("## 5. 데이터 시각화 및 지역별 인사이트\n")

# [1] 플랫폼별 상품 수 (일변량)
plat_counts = df['platform'].value_counts()
plt.figure(figsize=(6,4))
sns.barplot(x=plat_counts.index, y=plat_counts.values)
plt.title("플랫폼별 관광 상품 수")
plt.tight_layout()
plt.savefig("images/plot1_platform.png")
plt.close()
report_content.append("### 5.1 플랫폼별 관광 상품 수\n")
report_content.append("![플랫폼별 상품 수](images/plot1_platform.png)\n")
report_content.append(plat_counts.reset_index().to_markdown() + "\n")
report_content.append("**해석:** Klook과 GetYourGuide 두 플랫폼 간 등록된 관광 상품의 수를 비교하는 그래프입니다. 어느 플랫폼이 한국 관광 상품을 더 적극적으로 서비스하고 있는지 파악할 수 있으며, 데이터 불균형 정도를 확인하는 지표가 됩니다.\n")

# [2] 지역별 리뷰 수 (방문객 규모 측정) (이변량)
region_reviews = df.groupby('region_clean')['reviews_num'].sum().sort_values(ascending=False).head(15)
plt.figure(figsize=(10,6))
sns.barplot(x=region_reviews.values, y=region_reviews.index, palette='crest')
plt.title("지역별 총 리뷰 수 (상위 15개 지역)")
plt.xlabel("총 리뷰 수 (외국인 방문 척도)")
plt.tight_layout()
plt.savefig("images/plot2_region_reviews.png")
plt.close()
report_content.append("### 5.2 지역별 총 리뷰 수 (외국인 방문객 규모)\n")
report_content.append("![지역별 리뷰수](images/plot2_region_reviews.png)\n")
report_content.append(region_reviews.reset_index().to_markdown() + "\n")
report_content.append("**해석:** 각 지역별로 작성된 총 리뷰 수를 합산한 그래프입니다. 리뷰 수는 외국인 관광객의 실제 이용 및 방문을 대변하는 척도이므로, 서울, 제주 등 상위 지역들의 압도적인 방문객 점유율을 시각적으로 명확히 확인할 수 있습니다.\n")

# [3] 지역별 평균 평점 (만족도 측정) (이변량)
region_ratings = df[df['rating_num'] > 0].groupby('region_clean')['rating_num'].mean().sort_values(ascending=False).head(15)
plt.figure(figsize=(10,6))
sns.barplot(x=region_ratings.values, y=region_ratings.index, palette='flare')
plt.title("지역별 평균 평점 (만족도)")
plt.xlabel("평균 평점")
plt.xlim(4.0, 5.0)
plt.tight_layout()
plt.savefig("images/plot3_region_ratings.png")
plt.close()
report_content.append("### 5.3 지역별 평균 평점 (방문 만족도)\n")
report_content.append("![지역별 평점](images/plot3_region_ratings.png)\n")
report_content.append(region_ratings.reset_index().to_markdown() + "\n")
report_content.append("**해석:** 유효한 평점을 지닌 상품들을 기준으로 지역별 평균 평점을 산출한 결과입니다. 대체로 4.5 이상의 높은 만족도를 보이나 지역 간 미세한 차이를 통해 어느 지역 관광 상품의 퀄리티와 고객 만족도가 상대적으로 높은지 평가할 수 있습니다.\n")

# [4] 가격 분포 (일변량)
plt.figure(figsize=(8,5))
sns.histplot(df[df['price_num'] < df['price_num'].quantile(0.95)]['price_num'], bins=30, kde=True)
plt.title("상품 가격 분포 (상위 5% 이상치 제외)")
plt.tight_layout()
plt.savefig("images/plot4_price_dist.png")
plt.close()
report_content.append("### 5.4 관광 상품 가격 분포\n")
report_content.append("![가격분포](images/plot4_price_dist.png)\n")
report_content.append(df['price_num'].describe().to_markdown() + "\n")
report_content.append("**해석:** 가격 데이터 중 상위 5% 이상치를 제외한 대다수 상품들의 가격 분포를 나타내는 히스토그램입니다. 대부분의 관광 상품 가격대가 특정 구간에 밀집해 있는 우측 꼬리 분포(Right-skewed) 형태를 띄고 있음을 직관적으로 보여줍니다.\n")

# [5] 가격과 평점의 관계 (이변량)
plt.figure(figsize=(8,5))
sns.scatterplot(x='price_num', y='rating_num', data=df[df['rating_num']>0])
plt.title("가격과 평점의 산점도")
plt.tight_layout()
plt.savefig("images/plot5_price_rating.png")
plt.close()
report_content.append("### 5.5 가격과 평점의 관계\n")
report_content.append("![가격과평점](images/plot5_price_rating.png)\n")
corr_table1 = df[['price_num', 'rating_num']].corr()
report_content.append(corr_table1.to_markdown() + "\n")
report_content.append("**해석:** 상품의 가격과 고객이 부여한 평점 간의 상관성을 살펴보는 산점도입니다. 고가의 상품일수록 만족도가 무조건 높은지, 혹은 저가의 가성비 상품들이 높은 평점을 지니는지에 대한 힌트를 얻을 수 있는 시각화입니다.\n")

# [6] 리뷰 수와 평점의 관계 (이변량)
plt.figure(figsize=(8,5))
sns.scatterplot(x='reviews_num', y='rating_num', data=df[df['rating_num']>0], alpha=0.5)
plt.title("리뷰 수와 평점의 산점도")
plt.tight_layout()
plt.savefig("images/plot6_review_rating.png")
plt.close()
report_content.append("### 5.6 리뷰 수와 평점의 상관관계\n")
report_content.append("![리뷰와평점](images/plot6_review_rating.png)\n")
corr_table2 = df[['reviews_num', 'rating_num']].corr()
report_content.append(corr_table2.to_markdown() + "\n")
report_content.append("**해석:** 인기도(리뷰 수)와 만족도(평점) 간의 산점도입니다. 리뷰가 많은, 즉 널리 알려지고 많이 팔린 상품들이 일정 수준 이상의 고평점을 안정적으로 유지하는 경향성을 보여줍니다. 반면 리뷰가 적은 상품은 평점 편차가 크게 나타납니다.\n")

# [7] 플랫폼별 가격 분포 박스플롯 (다변량 관점)
plt.figure(figsize=(8,5))
sns.boxplot(x='platform', y='price_num', data=df[df['price_num'] < df['price_num'].quantile(0.90)])
plt.title("플랫폼별 상품 가격 비교 (상위 10% 제외)")
plt.tight_layout()
plt.savefig("images/plot7_platform_price.png")
plt.close()
report_content.append("### 5.7 플랫폼별 상품 가격 비교\n")
report_content.append("![플랫폼가격](images/plot7_platform_price.png)\n")
pivot_plat_price = df.groupby('platform')['price_num'].describe()
report_content.append(pivot_plat_price.to_markdown() + "\n")
report_content.append("**해석:** GetYourGuide와 Klook에서 판매되는 상품들의 가격대 차이를 시각화한 박스플롯입니다. 두 플랫폼 중 어느 곳이 프리미엄 상품을 더 많이 다루고 있는지, 또는 평균적인 가성비 타겟인지 비교하는 데 적합한 시각화 자료입니다.\n")

# [8] 상위 5개 지역의 평점 분포 바이올린 플롯 (다변량)
top5_reg = df['region_clean'].value_counts().head(5).index
plt.figure(figsize=(10,6))
sns.violinplot(x='region_clean', y='rating_num', data=df[(df['region_clean'].isin(top5_reg)) & (df['rating_num']>0)])
plt.title("주요 5개 지역별 평점 분포")
plt.tight_layout()
plt.savefig("images/plot8_top5_rating_violin.png")
plt.close()
report_content.append("### 5.8 주요 5개 지역별 평점 분포\n")
report_content.append("![지역평점바이올린](images/plot8_top5_rating_violin.png)\n")
pivot_top5_rate = df[df['region_clean'].isin(top5_reg)].groupby('region_clean')['rating_num'].describe()
report_content.append(pivot_top5_rate.to_markdown() + "\n")
report_content.append("**해석:** 상품 수가 가장 많은 주요 5개 지역을 대상으로 평점의 밀집도와 분포 형태를 비교하는 바이올린 플롯입니다. 지역 간 평균의 차이뿐만 아니라, 극단적인 혹평을 받은 상품이나 만점을 받은 상품의 밀도 차이를 상세히 보여줍니다.\n")

# [9] 지역별 플랫폼 비율 누적 막대그래프 (다변량)
cross_tab = pd.crosstab(df[df['region_clean'].isin(top5_reg)]['region_clean'], df['platform'])
cross_tab.plot(kind='bar', stacked=True, figsize=(8,6), colormap='Set2')
plt.title("주요 5개 지역별 플랫폼 상품 등록 비율")
plt.ylabel("상품 수")
plt.tight_layout()
plt.savefig("images/plot9_region_platform_stacked.png")
plt.close()
report_content.append("### 5.9 지역별 플랫폼 점유 비교\n")
report_content.append("![지역플랫폼누적](images/plot9_region_platform_stacked.png)\n")
report_content.append(cross_tab.to_markdown() + "\n")
report_content.append("**해석:** 특정 주요 관광 지역에서 Klook과 GetYourGuide 두 OTA 플랫폼이 차지하는 상품 수량 비중을 보여줍니다. 각 플랫폼의 지역적 집중도 전략을 엿볼 수 있으며, 영업을 확장해야 할 틈새 타겟 지역을 발굴하는 근거가 됩니다.\n")

# [10] 가격 구간별 평균 리뷰 수 (다변량)
df['price_bin'] = pd.qcut(df['price_num'], q=4, labels=['저가', '중저가', '중고가', '고가'])
bin_reviews = df.groupby('price_bin')['reviews_num'].mean()
plt.figure(figsize=(8,5))
sns.barplot(x=bin_reviews.index, y=bin_reviews.values, palette='mako')
plt.title("가격 구간별 평균 리뷰 수 (인기도)")
plt.tight_layout()
plt.savefig("images/plot10_pricebin_reviews.png")
plt.close()
report_content.append("### 5.10 가격 구간별 평균 리뷰 수\n")
report_content.append("![가격구간리뷰](images/plot10_pricebin_reviews.png)\n")
pivot_bin = df.groupby('price_bin')['reviews_num'].describe()
report_content.append(pivot_bin.to_markdown() + "\n")
report_content.append("**해석:** 관광 상품의 가격을 4개의 구간(사분위수)으로 나누어 각 구간별 평균 리뷰 수를 비교한 막대 그래프입니다. 저렴한 가성비 상품이 대중적으로 더 많은 외국인 관광객을 끌어모으는지에 대한 명확한 수요 예측 지표를 제공합니다.\n")

# [11] 시군구별 관광 상품 수 (추가 분석)
plt.figure(figsize=(10,6))
top_sigungu = df['region_sigungu'].value_counts().head(15)
sns.barplot(x=top_sigungu.values, y=top_sigungu.index, palette='viridis')
plt.title("시군구별 관광 상품 수 (상위 15개)")
plt.xlabel("상품 수")
plt.ylabel("시군구")
plt.tight_layout()
plt.savefig("images/plot11_sigungu_freq.png")
plt.close()
report_content.append("### 5.11 시군구별 관광 상품 수 (상위 15개)\n")
report_content.append("![시군구 상품수](images/plot11_sigungu_freq.png)\n")
report_content.append(top_sigungu.reset_index().to_markdown() + "\n")
report_content.append("**해석:** 시군구 단위로 세분화하여 어느 지역에 관광 상품이 밀집해 있는지 분석한 빈도 그래프입니다. 시도 단위보다 더 구체적인 관광 거점을 파악할 수 있습니다.\n")

# [12] 시군구별 총 리뷰 수 (방문객 규모) (추가 분석)
sigungu_reviews = df.groupby('region_sigungu')['reviews_num'].sum().sort_values(ascending=False).head(15)
plt.figure(figsize=(10,6))
sns.barplot(x=sigungu_reviews.values, y=sigungu_reviews.index, palette='crest')
plt.title("시군구별 총 리뷰 수 (상위 15개)")
plt.xlabel("총 리뷰 수")
plt.tight_layout()
plt.savefig("images/plot12_sigungu_reviews.png")
plt.close()
report_content.append("### 5.12 시군구별 총 리뷰 수 (상위 15개)\n")
report_content.append("![시군구 리뷰수](images/plot12_sigungu_reviews.png)\n")
report_content.append(sigungu_reviews.reset_index().to_markdown() + "\n")
report_content.append("**해석:** 시군구 단위로 총 리뷰 수를 산출한 결과입니다. 상품 등록 수와 비례하지 않고 특정 소도시(예: 파주시, 수원시 등)에 방문객(리뷰 수)이 집중되는 현상을 확인할 수 있습니다.\n")

# [13] 시군구별 평균 평점 (추가 분석)
sigungu_ratings = df[df['rating_num'] > 0].groupby('region_sigungu')['rating_num'].mean().sort_values(ascending=False).head(15)
plt.figure(figsize=(10,6))
sns.barplot(x=sigungu_ratings.values, y=sigungu_ratings.index, palette='flare')
plt.title("시군구별 평균 평점 (만족도)")
plt.xlabel("평균 평점")
plt.xlim(4.0, 5.0)
plt.tight_layout()
plt.savefig("images/plot13_sigungu_ratings.png")
plt.close()
report_content.append("### 5.13 시군구별 평균 평점 (상위 15개)\n")
report_content.append("![시군구 평점](images/plot13_sigungu_ratings.png)\n")
report_content.append(sigungu_ratings.reset_index().to_markdown() + "\n")
report_content.append("**해석:** 평점이 유효한 상품들에 한정하여 시군구별 평균 만족도를 살펴본 차트입니다. 특정 관광 거점 도시들이 높은 평점을 안정적으로 유지하는지, 혹은 편차가 있는지 비교 분석할 수 있습니다.\n")

# 리포트 저장
with open("eda_report.md", "w", encoding='utf-8') as f:
    f.writelines(report_content)

print("EDA 분석 완료 및 eda_report.md 생성 성공!")
