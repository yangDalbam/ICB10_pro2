"""
이 스크립트는 시도시군구별 브랜드 교차표 데이터를 바탕으로 
브랜드 간의 상관관계를 시각화하는 페어플롯(Pairplot)을 생성합니다.
요청에 따라:
- 하삼각행렬은 숨기고(마스킹) 상삼각행렬만 표시
- 각 산점도에 회귀선(regplot) 추가
- 각 그래프 우측 상단에 피어슨 상관계수 표기
"""
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import scipy.stats as stats
import os

def main():
    file_path = r"c:\Users\user1\Downloads\ICB10_proj2\burger_index\report\sigungu_crosstab.csv"
    output_path = r"c:\Users\user1\Downloads\ICB10_proj2\burger_index\images\brand_pairplot.png"
    
    plt.rc('font', family='Malgun Gothic')
    plt.rcParams['axes.unicode_minus'] = False
    
    df = pd.read_csv(file_path)
    df = df[df['시도시군구명'] != '총계']
    
    brands = ['KFC', '롯데리아', '맥도날드', '버거킹']
    
    # 1. PairGrid 생성
    g = sns.PairGrid(df[brands], diag_sharey=False)
    
    # 상관계수 계산 및 텍스트 표시를 위한 함수
    def corrfunc(x, y, **kws):
        r, p = stats.pearsonr(x, y)
        ax = plt.gca()
        # 우측 상단에 상관계수 텍스트 표기
        ax.annotate(f'r = {r:.2f}', xy=(0.95, 0.95), xycoords=ax.transAxes,
                    ha='right', va='top', fontsize=12,
                    bbox=dict(boxstyle="round,pad=0.3", fc="white", ec="gray", alpha=0.8))
        
    # 2. 상삼각행렬(Upper triangle): 회귀선 추가 및 상관계수 표시
    g.map_upper(sns.regplot, scatter_kws={'alpha':0.6, 'marker':'+'}, line_kws={'color':'red'})
    g.map_upper(corrfunc)
    
    # 3. 대각행렬(Diagonal): 밀도 추정(KDE) 그래프 표시
    g.map_diag(sns.kdeplot, fill=True)
    
    # 4. 하삼각행렬(Lower triangle) 마스킹(숨김 처리)
    for i in range(len(brands)):
        for j in range(len(brands)):
            if i > j:  # lower triangle 위치
                g.axes[i, j].set_visible(False)
                
    # 타이틀
    g.fig.suptitle('시군구별 버거 브랜드 매장 빈도 페어플롯 (상관관계)', y=1.02, fontsize=16)
    
    # 결과 저장
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"페어플롯이 정상적으로 업데이트 되었습니다: {output_path}")

if __name__ == "__main__":
    main()
