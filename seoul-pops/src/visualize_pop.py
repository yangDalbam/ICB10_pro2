"""
이 모듈은 연남동과 성수동의 데이터를 추출하여 시간대별/연령대별/행정동별 생활인구수 선그래프를 시각화합니다.
주요 기능:
- 행정동 매핑 엑셀 파일에서 '연남동'과 '성수동' 관련 행정동코드 추출
- Parquet 데이터에서 해당 행정동코드 데이터 필터링
- 시간대별, 연령대별, 행정동별 생활인구수 집계
- Seaborn을 사용한 시각화 (x축: 시간대, y축: 생활인구수, 패싯: 연령대, 색상: 행정동)
- koreanize_matplotlib를 적용하여 한글 폰트 처리
"""
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib

def plot_data():
    print("Reading mapping data...")
    df_map = pd.read_excel('seoul-pops/data/행정동코드_매핑정보_20241218.xlsx')
    
    # Extract rows with '연남' or '성수'
    # The exact columns from previous inspection: '통계청행정동코드', '행자부행정동코드', '시도명', '시군구명', '행정동명'
    target_mask = df_map['행정동명'].str.contains('연남|성수', na=False)
    target_dongs = df_map[target_mask]
    dong_dict = dict(zip(target_dongs['행자부행정동코드'].astype(int), target_dongs['행정동명']))
    
    print(f"Target dongs found: {dong_dict}")
    
    print("Reading parquet data...")
    df_pop = pd.read_parquet('seoul-pops/data/LOCAL_PEOPLE_DONG_202606_optimized_final.parquet')
    
    print("Filtering data...")
    df_filtered = df_pop[df_pop['행정동코드'].astype(int).isin(dong_dict.keys())].copy()
    df_filtered['행정동명'] = df_filtered['행정동코드'].astype(int).map(dong_dict)
    
    if df_filtered.empty:
        print("Error: Filtered dataframe is empty. Check dong code types.")
        return
    
    # Aggregate data: mean of population by (시간대, 행정동명, 연령대)
    # First sum by 기준일ID to combine male/female if any, wait, we want total by age?
    # Actually, grouping by ['기준일ID', '시간대구분', '행정동명', '연령대'] and summing combines genders.
    print("Aggregating data...")
    df_daily = df_filtered.groupby(['기준일ID', '시간대구분', '행정동명', '연령대'], observed=True)['생활인구수'].sum().reset_index()
    # Then take the mean across the 30 days
    df_agg = df_daily.groupby(['시간대구분', '행정동명', '연령대'], observed=True)['생활인구수'].mean().reset_index()
    
    print("Plotting data...")
    # 템플릿 기본 스타일 사용 안함 (eda-basic 규칙: seaborn의 스타일 설정 사용 안함)
    # plt.style.use('default') # Ensure clean style
    
    # To satisfy "y축에는 연령대, x축에는 시간대", we will map age groups to subplots (columns/rows),
    # x-axis to time, and y-axis to population, coloring by dong.
    g = sns.relplot(
        data=df_agg,
        x='시간대구분',
        y='생활인구수',
        hue='행정동명',
        col='연령대',
        col_wrap=4,
        kind='line',
        marker='o',
        height=3,
        aspect=1.2
    )
    
    g.set_axis_labels('시간대 (0~23시)', '평균 생활인구수 (명)')
    g.fig.suptitle('연남동 및 성수동 시간대별/연령대별 생활인구수 추이', y=1.02, fontsize=16)
    
    # Customize x-ticks to show specific hours clearly
    for ax in g.axes.flat:
        ax.set_xticks(range(0, 24, 4))
        ax.grid(True, linestyle='--', alpha=0.6)
    
    image_path = 'seoul-pops/images/pop_trend_seongsu_yeonnam.png'
    g.savefig(image_path, dpi=300, bbox_inches='tight')
    print(f"Plot saved to {image_path}")
    
    # Save a markdown artifact with the image
    report_content = f"""# 연남동 및 성수동 생활인구수 분석

- 분석 대상 행정동: {', '.join(dong_dict.values())}
- 시각화 내용: 연령대별로 각각 시간대(x축)에 따른 생활인구수(y축) 변화를 나타내는 선그래프입니다. 행정동마다 선의 색상을 다르게 지정하여 비교했습니다.

![생활인구수 추이 그래프](/c:/Users/user1/Downloads/ICB10_proj2/seoul-pops/images/pop_trend_seongsu_yeonnam.png)
"""
    with open('seoul-pops/report/pop_trend_report.md', 'w', encoding='utf-8') as f:
        f.write(report_content)

if __name__ == '__main__':
    plot_data()
