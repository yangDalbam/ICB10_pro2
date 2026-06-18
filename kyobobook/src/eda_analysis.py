"""
이 모듈은 교보문고 베스트셀러 데이터를 바탕으로 탐색적 데이터 분석(EDA)을 수행하는 스크립트입니다.
주요 기능:
- 데이터 로드 및 결측치, 요약 통계량 계산
- 범주형 및 수치형 변수에 대한 기술 통계 추출
- 도서명 대상 TF-IDF 키워드 추출
- matplotlib 및 koreanize-matplotlib를 활용한 10개 이상의 시각화 차트 생성 및 저장
- 분석 결과 텍스트를 eda_results.json으로 내보내어 이후 리포트 작성에 활용
"""

import os
import json
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import koreanize_matplotlib
from sklearn.feature_extraction.text import TfidfVectorizer

def run_eda():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'kyobo_bestseller.csv')
    img_dir = os.path.join(base_dir, 'images')
    os.makedirs(img_dir, exist_ok=True)
    
    df = pd.read_csv(data_path)
    
    results = {}
    
    # 1. 기본 정보
    results['head'] = df.head(5).to_dict(orient='records')
    results['tail'] = df.tail(5).to_dict(orient='records')
    results['shape'] = list(df.shape)
    results['duplicates'] = int(df.duplicated().sum())
    
    import io
    buf = io.StringIO()
    df.info(buf=buf)
    results['info'] = buf.getvalue()
    results['info'] = buf.getvalue()
    
    # 2. 기술통계 (수치형)
    num_cols = df.select_dtypes(include=[np.number]).columns.tolist()
    results['desc_num'] = df[num_cols].describe().to_dict()
    
    # 3. 기술통계 (범주형)
    cat_cols = ['저자', '출판사']
    results['desc_cat'] = df[cat_cols].describe(include='all').to_dict()
    
    # 범주형 빈도수 (상위 30)
    top_publishers = df['출판사'].value_counts().head(30)
    top_authors = df['저자'].value_counts().head(30)
    results['freq_publishers'] = top_publishers.to_dict()
    results['freq_authors'] = top_authors.to_dict()
    
    # 4. TF-IDF 텍스트 분석 (도서명)
    # 간단한 형태소 분석 없이 키워드 추출 (단어 단위)
    tfidf = TfidfVectorizer(max_features=1000, stop_words=['의', '를', '에', '가', '은', '는'])
    tfidf_matrix = tfidf.fit_transform(df['도서명'].fillna(''))
    feature_names = tfidf.get_feature_names_out()
    sums = tfidf_matrix.sum(axis=0)
    
    tfidf_scores = []
    for col, term in enumerate(feature_names):
        tfidf_scores.append((term, sums[0, col]))
    tfidf_scores = sorted(tfidf_scores, key=lambda x: x[1], reverse=True)[:30]
    results['tfidf_top30'] = {item[0]: float(item[1]) for item in tfidf_scores}
    
    # 5. 파생 변수 (순위 그룹, 가격 그룹)
    df['순위그룹'] = pd.cut(df['순위'], bins=[0, 300, 600, 1000], labels=['상위(1~300)', '중위(301~600)', '하위(601~1000)'])
    # 가격 교차표
    crosstab_pub_rank = pd.crosstab(df['출판사'], df['순위그룹']).loc[top_publishers.head(5).index]
    results['crosstab_pub_rank'] = crosstab_pub_rank.to_dict()
    
    pivot_price = df.pivot_table(index='순위그룹', values='판매가', aggfunc=['mean', 'median', 'std'])
    pivot_price.columns = ['_'.join(col).strip() for col in pivot_price.columns.values]
    results['pivot_price'] = pivot_price.to_dict()
    
    # --- 시각화 ---
    plt.rcParams['font.family'] = 'Malgun Gothic' # Windows fallback, koreanize_matplotlib should handle it
    
    # 1. 판매가 분포 (Histogram)
    plt.figure(figsize=(10,6))
    plt.hist(df['판매가'].dropna(), bins=30, color='skyblue', edgecolor='black')
    plt.title('도서 판매가 분포')
    plt.xlabel('판매가(원)')
    plt.ylabel('빈도수')
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'plot1_price_dist.png'))
    plt.close()
    
    # 2. 상위 30개 출판사 빈도수 (Bar)
    plt.figure(figsize=(12,8))
    top_publishers.sort_values().plot(kind='barh', color='coral')
    plt.title('상위 30개 출판사 빈도수')
    plt.xlabel('도서 수')
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'plot2_top30_publishers.png'))
    plt.close()
    
    # 3. 상위 30개 저자 빈도수 (Bar)
    plt.figure(figsize=(12,8))
    top_authors.sort_values().plot(kind='barh', color='lightgreen')
    plt.title('상위 30개 저자 빈도수')
    plt.xlabel('도서 수')
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'plot3_top30_authors.png'))
    plt.close()
    
    # 4. 순위 vs 판매가 산점도 (Scatter)
    plt.figure(figsize=(10,6))
    plt.scatter(df['순위'], df['판매가'], alpha=0.5, color='purple')
    plt.title('순위와 판매가의 관계')
    plt.xlabel('순위')
    plt.ylabel('판매가(원)')
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'plot4_price_vs_rank.png'))
    plt.close()
    
    # 5. 판매가 Boxplot
    plt.figure(figsize=(8,6))
    plt.boxplot(df['판매가'].dropna(), vert=False, patch_artist=True)
    plt.title('도서 판매가 Boxplot')
    plt.xlabel('판매가(원)')
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'plot5_price_boxplot.png'))
    plt.close()
    
    # 6. 상위 10개 출판사별 평균 판매가
    top10_pubs = top_publishers.head(10).index
    avg_price_pub = df[df['출판사'].isin(top10_pubs)].groupby('출판사')['판매가'].mean().sort_values(ascending=False)
    plt.figure(figsize=(10,6))
    avg_price_pub.plot(kind='bar', color='orange')
    plt.title('상위 10개 출판사별 평균 판매가')
    plt.ylabel('평균 판매가(원)')
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'plot6_top10_pub_price_avg.png'))
    plt.close()
    
    # 7. 순위 그룹별 판매가 Boxplot
    plt.figure(figsize=(10,6))
    data_to_plot = [df[df['순위그룹'] == g]['판매가'].dropna() for g in df['순위그룹'].cat.categories]
    plt.boxplot(data_to_plot, labels=df['순위그룹'].cat.categories, patch_artist=True)
    plt.title('순위 그룹별 판매가 분포')
    plt.ylabel('판매가(원)')
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'plot7_rank_group_price_box.png'))
    plt.close()
    
    # 8. 도서명 TF-IDF 키워드 상위 30개 (Bar)
    terms = [item[0] for item in tfidf_scores]
    scores = [item[1] for item in tfidf_scores]
    plt.figure(figsize=(12,8))
    plt.barh(terms[::-1], scores[::-1], color='teal')
    plt.title('도서명 TF-IDF 주요 키워드 Top 30')
    plt.xlabel('TF-IDF Score')
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'plot8_tfidf_top30.png'))
    plt.close()
    
    # 9. 상위 5개 출판사별 순위 그룹 교차표 시각화 (Stacked Bar)
    crosstab_pub_rank.plot(kind='bar', stacked=True, figsize=(10,6), colormap='viridis')
    plt.title('상위 5개 출판사의 순위 그룹별 분포')
    plt.ylabel('도서 수')
    plt.xticks(rotation=0)
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'plot9_pub_vs_rank_group.png'))
    plt.close()
    
    # 10. 상위 10위 내 순위 변동에 따른 가격 변동 (Line chart approximation)
    df_top50 = df[df['순위'] <= 50].sort_values('순위')
    plt.figure(figsize=(12,6))
    plt.plot(df_top50['순위'], df_top50['판매가'], marker='o', linestyle='-', color='magenta')
    plt.title('Top 50 베스트셀러의 순위별 판매가 추이')
    plt.xlabel('순위')
    plt.ylabel('판매가(원)')
    plt.tight_layout()
    plt.savefig(os.path.join(img_dir, 'plot10_top50_price_trend.png'))
    plt.close()

    # Save results to json for reporting
    with open(os.path.join(base_dir, 'data', 'eda_results.json'), 'w', encoding='utf-8') as f:
        json.dump(results, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    run_eda()
