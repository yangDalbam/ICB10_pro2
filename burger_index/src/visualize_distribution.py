"""
이 스크립트는 시도시군구별 브랜드 매장 수 분포 데이터를 활용하여,
각 버거 브랜드의 지역별 매장 수 분포를 박스플롯(Boxplot)과 바이올린 플롯(Violin Plot)으로 시각화합니다.
주요 기능:
- sigungu_crosstab.csv에서 '총계' 행 제외
- 데이터를 Long format으로 변환 (melt)
- 1행 2열의 서브플롯을 이용해 박스플롯과 바이올린 플롯 동시 시각화
- 결과를 images/brand_distribution.png 경로에 저장
"""
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def main():
    file_path = r"c:\Users\user1\Downloads\ICB10_proj2\burger_index\report\sigungu_crosstab.csv"
    output_path = r"c:\Users\user1\Downloads\ICB10_proj2\burger_index\images\brand_distribution.png"
    
    # 윈도우 맑은 고딕 한글 폰트 설정
    plt.rc('font', family='Malgun Gothic')
    plt.rcParams['axes.unicode_minus'] = False
    
    # 데이터 로드
    df = pd.read_csv(file_path)
    
    # '총계' 행 제외
    df = df[df['시도시군구명'] != '총계']
    
    brands = ['롯데리아', '맥도날드', '버거킹', 'KFC']
    
    # 데이터를 Long format으로 변환 (그래프 그리기에 적합한 형태)
    df_melt = df.melt(id_vars=['시도시군구명'], value_vars=brands, var_name='브랜드', value_name='매장 수')
    
    # 시각화 설정 (1행 2열 서브플롯)
    fig, axes = plt.subplots(1, 2, figsize=(14, 6))
    
    # 1. 박스플롯
    sns.boxplot(x='브랜드', y='매장 수', data=df_melt, ax=axes[0], palette='pastel')
    axes[0].set_title('지역(시군구)별 매장 수 박스플롯 (Boxplot)', fontsize=14)
    axes[0].set_ylabel('매장 수 (개)', fontsize=12)
    axes[0].set_xlabel('브랜드', fontsize=12)
    
    # 2. 바이올린 플롯
    sns.violinplot(x='브랜드', y='매장 수', data=df_melt, ax=axes[1], palette='pastel', inner='quartile')
    axes[1].set_title('지역(시군구)별 매장 수 바이올린 플롯 (Violin Plot)', fontsize=14)
    axes[1].set_ylabel('매장 수 (개)', fontsize=12)
    axes[1].set_xlabel('브랜드', fontsize=12)
    
    # 전체 타이틀 설정
    plt.suptitle('국내 주요 버거 브랜드의 시군구 단위 매장 수 분포 비교', fontsize=16, y=1.02)
    
    # 레이아웃 조정 및 저장
    plt.tight_layout()
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"분포 시각화가 정상적으로 저장되었습니다: {output_path}")

if __name__ == "__main__":
    main()
