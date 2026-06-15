"""
이 모듈은 YES24 베스트셀러 데이터를 바탕으로 탐색적 데이터 분석(EDA)을 수행합니다.
주요 기능:
- 데이터 전처리 (결측치, 타입 변환 등)
- 기술통계량 산출 (수치형, 범주형)
- 데이터 시각화 10종 생성 및 이미지 파일 저장
- TF-IDF 기반 텍스트 마이닝
- 분석 결과를 통계표 형태의 마크다운으로 임시 저장
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import koreanize_matplotlib
import os
from sklearn.feature_extraction.text import TfidfVectorizer

def preprocess_data(df):
    # 특수문자, 콤마 제거 및 수치형 변환
    num_cols = ['할인가', '정가', '판매지수', '리뷰수']
    for col in num_cols:
        if col in df.columns:
            df[col] = df[col].astype(str).str.replace(',', '').str.replace('원', '').str.replace(' ', '')
            df[col] = pd.to_numeric(df[col], errors='coerce').fillna(0)
            
    if '평점' in df.columns:
        df['평점'] = pd.to_numeric(df['평점'], errors='coerce').fillna(0)
        
    return df

def main():
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'data', 'yes24_bestseller.csv')
    img_dir = os.path.join(base_dir, 'images')
    report_dir = os.path.join(base_dir, 'report')
    
    os.makedirs(img_dir, exist_ok=True)
    os.makedirs(report_dir, exist_ok=True)
    
    df = pd.read_csv(data_path)
    df = preprocess_data(df)
    
    # 보고서 파일 열기
    stats_out = os.path.join(report_dir, 'stats_output.md')
    with open(stats_out, 'w', encoding='utf-8') as f:
        f.write("# EDA 기초 통계 데이터\n\n")
        
        # 1. 상위/하위 5개행
        f.write("## 1. 데이터 상위 5개행\n")
        f.write(df.head(5).to_markdown() + "\n\n")
        f.write("## 2. 데이터 하위 5개행\n")
        f.write(df.tail(5).to_markdown() + "\n\n")
        
        # 2. info, 행/열 수, 중복 데이터
        f.write("## 3. 기본 정보\n")
        f.write(f"- 전체 행 수: {df.shape[0]}, 전체 열 수: {df.shape[1]}\n")
        f.write(f"- 중복 데이터 수: {df.duplicated().sum()}\n\n")
        
        # 3. 기술통계
        f.write("## 4. 수치형 변수 기술통계\n")
        f.write(df.describe().to_markdown() + "\n\n")
        
        f.write("## 5. 범주형 변수 기술통계\n")
        f.write(df.describe(include=['object']).to_markdown() + "\n\n")
        
        # 4. 시각화 (10개)
        # 4-1 정가/할인가 분포 (일변량)
        plt.figure(figsize=(10,5))
        plt.hist(df['정가'], bins=30, alpha=0.5, label='정가')
        plt.hist(df['할인가'], bins=30, alpha=0.5, label='할인가')
        plt.title("정가 및 할인가 분포")
        plt.xlabel("가격")
        plt.ylabel("빈도수")
        plt.legend()
        plt.savefig(os.path.join(img_dir, 'plot1_price_dist.png'))
        plt.close()
        
        # 4-2 판매지수 분포
        plt.figure(figsize=(10,5))
        plt.hist(df['판매지수'], bins=30, color='skyblue')
        plt.title("판매지수 분포")
        plt.xlabel("판매지수")
        plt.ylabel("빈도수")
        plt.savefig(os.path.join(img_dir, 'plot2_sales_dist.png'))
        plt.close()
        
        # 4-3 평점 분포
        plt.figure(figsize=(10,5))
        plt.hist(df[df['평점']>0]['평점'], bins=20, color='orange')
        plt.title("평점 분포 (0점 제외)")
        plt.xlabel("평점")
        plt.ylabel("빈도수")
        plt.savefig(os.path.join(img_dir, 'plot3_rating_dist.png'))
        plt.close()
        
        # 4-4 출판사별 빈도수 (상위 30개)
        pub_counts = df['출판사'].value_counts().head(30)
        plt.figure(figsize=(12,8))
        pub_counts.sort_values().plot(kind='barh', color='teal')
        plt.title("상위 30개 출판사 빈도수")
        plt.xlabel("도서 수")
        plt.tight_layout()
        plt.savefig(os.path.join(img_dir, 'plot4_publisher_bar.png'))
        plt.close()
        f.write("## 6. 상위 30개 출판사 빈도표\n")
        f.write(pub_counts.to_frame().to_markdown() + "\n\n")
        
        # 4-5 정가 vs 판매지수 산점도 (이변량)
        plt.figure(figsize=(10,5))
        plt.scatter(df['정가'], df['판매지수'], alpha=0.5, c='purple')
        plt.title("정가 vs 판매지수")
        plt.xlabel("정가")
        plt.ylabel("판매지수")
        plt.savefig(os.path.join(img_dir, 'plot5_price_vs_sales.png'))
        plt.close()
        
        # 4-6 리뷰 수 vs 판매지수 산점도
        plt.figure(figsize=(10,5))
        plt.scatter(df['리뷰수'], df['판매지수'], alpha=0.5, c='red')
        plt.title("리뷰 수 vs 판매지수")
        plt.xlabel("리뷰수")
        plt.ylabel("판매지수")
        plt.savefig(os.path.join(img_dir, 'plot6_review_vs_sales.png'))
        plt.close()
        
        # 4-7 평점 구간별 평균 판매지수 (교차표 느낌)
        df['평점구간'] = pd.cut(df['평점'], bins=[0,8,9,9.5,10], labels=['8이하', '8-9', '9-9.5', '9.5-10'])
        rating_sales = df.groupby('평점구간')['판매지수'].mean()
        plt.figure(figsize=(10,5))
        rating_sales.plot(kind='bar', color='green')
        plt.title("평점 구간별 평균 판매지수")
        plt.ylabel("평균 판매지수")
        plt.savefig(os.path.join(img_dir, 'plot7_rating_sales_bar.png'))
        plt.close()
        f.write("## 7. 평점 구간별 평균 판매지수 피봇\n")
        f.write(rating_sales.to_frame().to_markdown() + "\n\n")
        
        # 4-8 가격대별 리뷰수 (Boxplot)
        df['가격대'] = pd.qcut(df['정가'], q=4, labels=['저가', '중저가', '중고가', '고가'], duplicates='drop')
        plt.figure(figsize=(10,5))
        data_to_plot = [df[df['가격대']=='저가']['리뷰수'], df[df['가격대']=='중저가']['리뷰수'], 
                        df[df['가격대']=='중고가']['리뷰수'], df[df['가격대']=='고가']['리뷰수']]
        plt.boxplot(data_to_plot, labels=['저가', '중저가', '중고가', '고가'])
        plt.title("가격대별 리뷰수 분포")
        plt.ylabel("리뷰수")
        plt.savefig(os.path.join(img_dir, 'plot8_price_review_box.png'))
        plt.close()
        f.write("## 8. 가격대별 리뷰수 기초통계\n")
        f.write(df.groupby('가격대')['리뷰수'].describe().to_markdown() + "\n\n")
        
        # 4-9 정가 vs 할인가 비율(할인율)에 따른 판매지수 산점도
        df['할인율'] = (df['정가'] - df['할인가']) / df['정가'].replace(0, 1) * 100
        plt.figure(figsize=(10,5))
        plt.scatter(df['할인율'], df['판매지수'], alpha=0.5, c='brown')
        plt.title("할인율 vs 판매지수")
        plt.xlabel("할인율(%)")
        plt.ylabel("판매지수")
        plt.savefig(os.path.join(img_dir, 'plot9_discount_vs_sales.png'))
        plt.close()
        
        # 4-10 평점, 리뷰수, 가격, 판매지수 상관관계 히트맵 대용 (다변량)
        corr = df[['정가', '할인가', '판매지수', '리뷰수', '평점']].corr()
        plt.figure(figsize=(8,6))
        cax = plt.matshow(corr, cmap='coolwarm', vmin=-1, vmax=1, fignum=1)
        plt.colorbar(cax)
        plt.xticks(range(len(corr.columns)), corr.columns, rotation=45)
        plt.yticks(range(len(corr.columns)), corr.columns)
        for (i, j), z in np.ndenumerate(corr.values):
            plt.text(j, i, '{:0.2f}'.format(z), ha='center', va='center')
        plt.title("수치형 변수 상관관계", pad=20)
        plt.savefig(os.path.join(img_dir, 'plot10_correlation.png'))
        plt.close()
        f.write("## 9. 상관관계 매트릭스\n")
        f.write(corr.to_markdown() + "\n\n")
        
        # 5. TF-IDF 키워드 추출 (상품명)
        f.write("## 10. 상품명 TF-IDF 상위 30개 키워드\n")
        texts = df['상품명'].fillna('').tolist()
        vectorizer = TfidfVectorizer(max_features=30, stop_words=['for', 'and', 'with', 'the'])
        tfidf_matrix = vectorizer.fit_transform(texts)
        words = vectorizer.get_feature_names_out()
        sums = tfidf_matrix.sum(axis=0).A1
        word_freq = pd.DataFrame({'키워드': words, 'TF-IDF합계': sums}).sort_values(by='TF-IDF합계', ascending=False)
        
        f.write(word_freq.to_markdown() + "\n\n")
        
        plt.figure(figsize=(12,8))
        plt.barh(word_freq['키워드'][::-1], word_freq['TF-IDF합계'][::-1], color='magenta')
        plt.title("상품명 TF-IDF 상위 30개 키워드")
        plt.xlabel("TF-IDF 중요도 합계")
        plt.tight_layout()
        plt.savefig(os.path.join(img_dir, 'plot11_tfidf_keywords.png'))
        plt.close()
        
    print("EDA 분석 완료! 이미지와 통계 데이터가 저장되었습니다.")

if __name__ == '__main__':
    main()
