"""
이 스크립트는 시도시군구별 교차표 데이터의 '총계' 행을 활용하여,
각 버거 브랜드별 전체 매장 빈도수를 막대그래프(Barplot)로 시각화합니다.
주요 기능:
- sigungu_crosstab.csv에서 '총계' 데이터 추출
- 각 브랜드(KFC, 롯데리아, 맥도날드, 버거킹) 총 매장 수 막대그래프 생성
- 막대 위에 실제 매장 수치(텍스트) 추가
- 결과를 images/brand_barplot.png 경로에 저장
"""
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def main():
    file_path = r"c:\Users\user1\Downloads\ICB10_proj2\burger_index\report\sigungu_crosstab.csv"
    output_path = r"c:\Users\user1\Downloads\ICB10_proj2\burger_index\images\brand_barplot.png"
    
    # 윈도우 맑은 고딕 한글 폰트 설정
    plt.rc('font', family='Malgun Gothic')
    plt.rcParams['axes.unicode_minus'] = False
    
    # 데이터 로드
    df = pd.read_csv(file_path)
    
    # '총계' 행만 추출
    totals_row = df[df['시도시군구명'] == '총계']
    
    # 브랜드 리스트 및 값 추출
    brands = ['KFC', '롯데리아', '맥도날드', '버거킹']
    values = totals_row[brands].values[0]
    
    # 시각화를 위한 데이터프레임 변환
    plot_df = pd.DataFrame({'브랜드명': brands, '매장 수': values})
    
    # 매장 수 기준 내림차순 정렬 (가장 많은 곳이 좌측으로 오도록)
    plot_df = plot_df.sort_values(by='매장 수', ascending=False)
    
    # 시각화 설정
    plt.figure(figsize=(8, 6))
    
    # 막대그래프 그리기
    ax = sns.barplot(x='브랜드명', y='매장 수', data=plot_df, palette='Set2')
    
    # 막대 위에 수치 텍스트 표시
    for p in ax.patches:
        ax.annotate(format(p.get_height(), '.0f'), 
                    (p.get_x() + p.get_width() / 2., p.get_height()), 
                    ha = 'center', va = 'center', 
                    xytext = (0, 9), 
                    textcoords = 'offset points',
                    fontsize=12, fontweight='bold', color='black')
    
    plt.title('국내 주요 버거 브랜드 매장 수 현황', fontsize=16, pad=15)
    plt.ylabel('총 매장 수 (개)', fontsize=12)
    plt.xlabel('브랜드명', fontsize=12)
    
    # 상단 여백 추가 (텍스트가 잘리지 않게)
    plt.ylim(0, plot_df['매장 수'].max() * 1.15)
    
    # 저장
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"막대그래프가 정상적으로 저장되었습니다: {output_path}")

if __name__ == "__main__":
    main()
