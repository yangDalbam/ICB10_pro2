"""
이 스크립트는 시도시군구별 버거 브랜드 매장 수 데이터를 활용하여,
브랜드 간의 상관관계를 히트맵(Heatmap)으로 시각화합니다.
주요 기능:
- 마스킹 없이 전체 상관계수 행렬(Full Matrix)을 시각화
- 텍스트 값(annot) 표시를 통해 상관계수 직관성 확보
- 결과를 images/brand_heatmap.png 경로에 저장
"""
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
import os

def main():
    file_path = r"c:\Users\user1\Downloads\ICB10_proj2\burger_index\report\sigungu_crosstab.csv"
    output_path = r"c:\Users\user1\Downloads\ICB10_proj2\burger_index\images\brand_heatmap.png"
    
    # 윈도우 맑은 고딕 한글 폰트 설정
    plt.rc('font', family='Malgun Gothic')
    plt.rcParams['axes.unicode_minus'] = False
    
    # 데이터 로드 및 '총계' 행 제외
    df = pd.read_csv(file_path)
    df = df[df['시도시군구명'] != '총계']
    
    brands = ['KFC', '롯데리아', '맥도날드', '버거킹']
    
    # 상관계수 계산 (피어슨 상관계수 기본값)
    corr_matrix = df[brands].corr()
    
    # 시각화 설정
    plt.figure(figsize=(7, 6))
    
    # 히트맵 그리기 (마스크 없이 전체 매트릭스 표시)
    sns.heatmap(corr_matrix, 
                annot=True,          # 상관계수 수치 표시
                fmt='.3f',           # 소수점 3자리까지
                cmap='coolwarm',     # 파란색-빨간색 컬러맵
                vmin=0.5, vmax=1.0,  # 상관계수가 대체로 높으므로 스케일 조정 (필요에 따라 변경)
                linewidths=0.5,      # 셀 사이 경계선
                annot_kws={"size": 12})
    
    plt.title('시군구별 버거 브랜드 매장 빈도 상관계수 히트맵', fontsize=16, pad=15)
    
    # 저장
    plt.savefig(output_path, dpi=300, bbox_inches='tight')
    plt.close()
    
    print(f"히트맵이 정상적으로 저장되었습니다: {output_path}")

if __name__ == "__main__":
    main()
