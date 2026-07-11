"""
이 모듈은 서울 생활인구 데이터 탐색적 데이터 분석(EDA)을 위한 동적 Streamlit 대시보드 애플리케이션입니다.
주요 기능:
- 대용량 데이터 로드 및 사이드바를 통한 사용자 지정 다중 필터링 지원
- 데이터 요약, 결측치 및 동적으로 업데이트되는 기술 통계 확인
- 범주형 데이터 빈도 분석
- 일변량, 이변량, 다변량 데이터를 아우르는 15개 이상의 Plotly 기반 인터랙티브 차트 제공
- 각 차트에 대한 교차표, 피벗 테이블 및 50자 이상의 해석 제공
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import utils
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="서울 생활인구 동적 EDA", layout="wide")

@st.cache_data
def get_agg_data():
    return utils.load_data()

df = get_agg_data()
pop_col = '총생활인구수' if '총생활인구수' in df.columns else '생활인구수' if '생활인구수' in df.columns else df.columns[3]

fig1 = fig2 = fig3 = fig4 = fig5 = fig6 = fig7 = fig8 = fig9 = fig10 = fig11 = fig12 = fig13 = fig14 = fig15 = None
st.title("📊 서울 생활인구 데이터 동적 EDA 대시보드 (Plotly 버젼)")
st.markdown("본 대시보드는 서울 생활인구 데이터를 바탕으로 다양한 탐색적 데이터 분석(EDA)을 수행하며, 좌측 사이드바 필터를 통해 실시간으로 조건을 변경할 수 있습니다. 15개의 모든 차트는 Plotly를 기반으로 동작하여 확대/축소 및 마우스 오버를 지원합니다.")

# ---------------------------------------------------------
# Sidebar Filter Section
# ---------------------------------------------------------
st.sidebar.header("🔍 데이터 필터링 옵션")
st.sidebar.info("조건을 선택하지 않으면 전체 데이터가 조회됩니다. 성능 최적화를 위해 조건을 모두 선택한 후 '필터 적용' 버튼을 눌러주세요.")

unique_gus = sorted(df['CT_NM'].unique())
unique_genders = sorted([x for x in df['성별'].unique() if pd.notna(x)])
unique_ages = sorted([x for x in df['연령대'].unique() if pd.notna(x)])
unique_times = sorted(df['시간대구분'].unique())

with st.sidebar.form("filter_form"):
    selected_gus = st.multiselect("🏢 자치구 선택", options=unique_gus, default=[])
    selected_genders = st.multiselect("🚻 성별 선택", options=unique_genders, default=[])
    selected_ages = st.multiselect("🎂 연령대 선택", options=unique_ages, default=[])
    selected_times = st.multiselect("⏰ 시간대 선택 (0~23시)", options=unique_times, default=[])
    
    submitted = st.form_submit_button("🚀 필터 적용하기")

# 초기 상태 혹은 폼 제출 시 필터링 적용
filtered_df = df.copy()

if selected_gus:
    filtered_df = filtered_df[filtered_df['CT_NM'].isin(selected_gus)]
if selected_genders:
    filtered_df = filtered_df[filtered_df['성별'].isin(selected_genders)]
if selected_ages:
    filtered_df = filtered_df[filtered_df['연령대'].isin(selected_ages)]
if selected_times:
    filtered_df = filtered_df[filtered_df['시간대구분'].isin(selected_times)]

if len(filtered_df) == 0:
    st.error("선택하신 조건에 일치하는 데이터가 없습니다. 필터 조건을 다시 설정해 주세요.")
    st.stop()

st.sidebar.markdown("---")
st.sidebar.success(f"현재 필터링된 데이터: **{len(filtered_df):,}** 건 / 전체: {len(df):,} 건")

# ---------------------------------------------------------
# KPI Cards Section
# ---------------------------------------------------------
st.markdown("### 💡 핵심 지표 요약 (KPI)")
kpi1, kpi2, kpi3, kpi4 = st.columns(4)

total_pop_sum = filtered_df[pop_col].sum()
avg_pop = filtered_df[pop_col].mean()
max_pop = filtered_df[pop_col].max()
total_rows = len(filtered_df)

kpi1.metric(label="총 관측 데이터 수 (건)", value=f"{total_rows:,}")
kpi2.metric(label="누적 생활인구수 합계 (명)", value=f"{total_pop_sum:,.0f}")
kpi3.metric(label="평균 생활인구수 (명)", value=f"{avg_pop:,.1f}")
kpi4.metric(label="최대 생활인구수 (명)", value=f"{max_pop:,.0f}")
st.markdown("---")

# ---------------------------------------------------------
# Dashboard Main Tabs
# ---------------------------------------------------------
tab1, tab2, tab3, tab4 = st.tabs(["📝 데이터 개요 및 통계", "📊 Plotly 다차원 동적 차트 (15+)", "📄 분석 리포트 확인", "🗺️ 지도 시각화 (Folium)"])

with tab1:
    st.header("1. 필터링된 데이터 기본 정보")
    
    col1, col2 = st.columns(2)
    with col1:
        st.subheader("상위 5개 행")
        st.dataframe(filtered_df.head())
    with col2:
        st.subheader("하위 5개 행")
        st.dataframe(filtered_df.tail())
        
    st.subheader("데이터 구조 및 정보")
    import io
    buffer = io.StringIO()
    filtered_df.info(buf=buffer)
    st.text(buffer.getvalue())
    
    st.write(f"**필터링된 행 수:** {filtered_df.shape[0]:,} | **열 수:** {filtered_df.shape[1]}")
    
    st.subheader("중복 데이터 확인")
    dup_count = filtered_df.duplicated().sum()
    st.write(f"**중복된 행의 수:** {dup_count:,}건")
    
    st.header("2. 기술 통계 요약 (필터 기준)")
    st.dataframe(filtered_df.describe())
    
    st.header("3. 자동 생성 분석 보고서")
    report_text = utils.generate_descriptive_stats_report(filtered_df)
    st.markdown(report_text)

with tab2:
    st.header("Plotly 다변량 데이터 시각화 (15+ Charts)")
    st.info(f"현재 총 {len(filtered_df):,}건의 데이터를 기반으로 한 Plotly 대화형 차트가 렌더링되었습니다. 이미지 저장을 병행하므로 필터 적용 시 렌더링에 소폭의 시간이 소요될 수 있습니다.")
    
    charts_info = []
    
    # ---------------------------------------------------------
    # Chart 1: 성별 빈도수
    # ---------------------------------------------------------
    st.subheader("1. 성별 데이터 빈도 분석")
    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        gender_counts = filtered_df['성별'].value_counts().reset_index()
        gender_counts.columns = ['성별', '데이터수']
        fig1 = px.bar(gender_counts, x='성별', y='데이터수', title="성별 데이터 빈도수", text_auto=True, color='성별', color_discrete_sequence=px.colors.qualitative.Set2)
        st.plotly_chart(fig1, use_container_width=True)
        # utils.save_plot(fig1, "chart1_gender_freq.png")
    
    desc1 = "사용자가 지정한 조건 내에서 각 성별이 차지하는 관측치 건수를 나타냅니다. 마우스 호버를 통해 정확한 데이터 수치를 확인할 수 있으며, 성별 간의 균형 및 활동성 편중 여부를 직관적으로 판단할 수 있습니다."
    with col_table:
        st.dataframe(filtered_df['성별'].value_counts())
        st.write(f"**해석**: {desc1}")
    charts_info.append({'fig': fig1, 'title': '성별 데이터 빈도 분석', 'filename': 'chart1_gender_freq.png', 'description': desc1, 'table_md': filtered_df['성별'].value_counts().to_frame().to_markdown()})
    st.markdown("---")
    
    # ---------------------------------------------------------
    # Chart 2: 연령대 빈도수
    # ---------------------------------------------------------
    st.subheader("2. 연령대별 데이터 빈도 분석")
    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        age_counts = filtered_df['연령대'].value_counts().head(30).reset_index()
        age_counts.columns = ['연령대', '데이터수']
        fig2 = px.bar(age_counts, x='연령대', y='데이터수', title="연령대별 데이터 빈도수 (상위 30개)", text_auto=True, color='연령대', color_discrete_sequence=px.colors.qualitative.Pastel)
        st.plotly_chart(fig2, use_container_width=True)
        # utils.save_plot(fig2, "chart2_age_freq.png")
    
    desc2 = "필터링된 연령대 그룹의 총 건수를 시각화했습니다. Plotly의 줌 기능을 활용하여 세부 연령층을 확대해서 보거나, 툴팁을 통해 정확한 값을 확인할 수 있어 타겟 마케팅 대상 설정에 매우 유용합니다."
    with col_table:
        st.dataframe(filtered_df['연령대'].value_counts().head(30))
        st.write(f"**해석**: {desc2}")
    charts_info.append({'fig': fig2, 'title': '연령대별 데이터 빈도 분석', 'filename': 'chart2_age_freq.png', 'description': desc2, 'table_md': age_counts.set_index('연령대').to_markdown()})
    st.markdown("---")

    # ---------------------------------------------------------
    # Chart 3: 시간대별 관측 빈도
    # ---------------------------------------------------------
    st.subheader("3. 시간대별 데이터 수집 빈도")
    col_chart, col_table = st.columns([2, 1])
    time_counts = filtered_df['시간대구분'].value_counts().sort_index().reset_index()
    time_counts.columns = ['시간대', '데이터수']
    with col_chart:
        fig3 = px.line(time_counts, x='시간대', y='데이터수', title="시간대별 관측 데이터 건수 추이", markers=True)
        fig3.update_xaxes(tickmode='linear', dtick=1)
        st.plotly_chart(fig3, use_container_width=True)
        # utils.save_plot(fig3, "chart3_time_freq.png")
        
    desc3 = "하루 24시간 중 어느 시간대에 데이터가 집중적으로 기록되었는지 꺾은선으로 보여줍니다. 대화형 인터랙션을 통해 야간과 주간 시간대를 드래그하여 부분적으로 확대 관찰할 수 있습니다."
    with col_table:
        st.dataframe(time_counts.set_index('시간대').T)
        st.write(f"**해석**: {desc3}")
    charts_info.append({'fig': fig3, 'title': '시간대별 관측 빈도', 'filename': 'chart3_time_freq.png', 'description': desc3, 'table_md': time_counts.set_index('시간대').T.to_markdown()})
    st.markdown("---")

    # ---------------------------------------------------------
    # Chart 4: 성별 총생활인구수 평균
    # ---------------------------------------------------------
    st.subheader("4. 성별 평균 총생활인구수")
    gender_mean = filtered_df.groupby('성별')[pop_col].mean().reset_index()
    gender_mean.columns = ['성별', '평균인구수']
    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        fig4 = px.bar(gender_mean, x='성별', y='평균인구수', title="성별 평균 생활인구", color='성별', text_auto='.2f')
        st.plotly_chart(fig4, use_container_width=True)
        # utils.save_plot(fig4, "chart4_gender_pop.png")
        
    desc4 = "필터링된 범위 내에서 남성과 여성의 평균 생활인구 차이를 보여줍니다. 특정 조건에 따라 남녀 중 어느 쪽의 밀집도가 더 높은지 신속하게 대조할 수 있는 지표입니다."
    with col_table:
        st.dataframe(gender_mean.set_index('성별'))
        st.write(f"**해석**: {desc4}")
    charts_info.append({'fig': fig4, 'title': '성별 평균 생활인구수', 'filename': 'chart4_gender_pop.png', 'description': desc4, 'table_md': gender_mean.set_index('성별').to_markdown()})
    st.markdown("---")

    # ---------------------------------------------------------
    # Chart 5: 연령대별 총생활인구수 평균
    # ---------------------------------------------------------
    st.subheader("5. 연령대별 평균 총생활인구수")
    age_mean = filtered_df.groupby('연령대')[pop_col].mean().reset_index()
    age_mean.columns = ['연령대', '평균인구수']
    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        fig5 = px.line(age_mean, x='연령대', y='평균인구수', title="연령대별 평균 생활인구", markers=True, text='평균인구수')
        fig5.update_traces(textposition="top center")
        st.plotly_chart(fig5, use_container_width=True)
        # utils.save_plot(fig5, "chart5_age_pop.png")
        
    desc5 = "각 연령대별로 평균적으로 도심 내 얼마나 많은 인구가 생활하는지 파악할 수 있는 선형 차트입니다. 실시간 연령대별 상권 수요를 예측하고 주요 이동 층을 파악하는 데 유용합니다."
    with col_table:
        st.dataframe(age_mean.set_index('연령대'))
        st.write(f"**해석**: {desc5}")
    charts_info.append({'fig': fig5, 'title': '연령대별 평균 생활인구', 'filename': 'chart5_age_pop.png', 'description': desc5, 'table_md': age_mean.set_index('연령대').to_markdown()})
    st.markdown("---")

    # ---------------------------------------------------------
    # Chart 6: 시간대별 총생활인구수 추이
    # ---------------------------------------------------------
    st.subheader("6. 시간대별 평균 총생활인구수 추이")
    time_mean = filtered_df.groupby('시간대구분')[pop_col].mean().reset_index()
    time_mean.columns = ['시간대', '평균인구수']
    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        fig6 = px.area(time_mean, x='시간대', y='평균인구수', title="하루 시간대별 평균 생활인구수 변화 추이 (Area)", markers=True)
        fig6.update_xaxes(tickmode='linear', dtick=1)
        st.plotly_chart(fig6, use_container_width=True)
        # utils.save_plot(fig6, "chart6_time_pop.png")
        
    desc6 = "선택된 변수 조합 내에서 24시간 동안의 평균 인구 증감 추이를 도식화한 면적(Area) 차트입니다. 출퇴근 시간대 또는 야간 활동의 피크타임을 정교하게 필터링하여 모니터링할 수 있습니다."
    with col_table:
        st.dataframe(time_mean.set_index('시간대').T)
        st.write(f"**해석**: {desc6}")
    charts_info.append({'fig': fig6, 'title': '시간대별 평균 생활인구수 추이', 'filename': 'chart6_time_pop.png', 'description': desc6, 'table_md': time_mean.set_index('시간대').T.to_markdown()})
    st.markdown("---")

    # ---------------------------------------------------------
    # Chart 7: 성별 x 시간대별 평균 인구 추이
    # ---------------------------------------------------------
    st.subheader("7. 성별 및 시간대별 평균 인구 추이 (교차 분석)")
    time_gender_pivot = filtered_df.pivot_table(index='시간대구분', columns='성별', values=pop_col, aggfunc='mean').reset_index()
    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        if len(time_gender_pivot.columns) > 1:
            fig7 = px.line(time_gender_pivot, x='시간대구분', y=time_gender_pivot.columns[1:], title="시간대별 남/여 평균 생활인구 추이 비교", markers=True)
            fig7.update_xaxes(tickmode='linear', dtick=1)
            fig7.update_layout(yaxis_title="평균인구수", legend_title_text="성별")
            st.plotly_chart(fig7, use_container_width=True)
            # utils.save_plot(fig7, "chart7_time_gender.png")
        else:
            st.warning("비교할 성별 데이터가 부족합니다.")
        
    desc7 = "시간 및 성별을 동시에 고려한 다변량 차트로, Plotly의 범례(Legend) 클릭 기능을 통해 특정 성별만 껐다 켜며 시계열 행동 패턴의 미세한 차이를 비교 분석할 수 있습니다."
    with col_table:
        st.dataframe(time_gender_pivot.set_index('시간대구분').head(10))
        st.write(f"**해석**: {desc7}")
    charts_info.append({'fig': fig7, 'title': '성별 및 시간대별 인구 추이', 'filename': 'chart7_time_gender.png', 'description': desc7, 'table_md': time_gender_pivot.set_index('시간대구분').to_markdown()})
    st.markdown("---")

    # ---------------------------------------------------------
    # Chart 8: 상위 10개 행정동 총생활인구수 평균
    # ---------------------------------------------------------
    st.subheader("8. 평균 생활인구 상위 10개 행정동")
    dong_mean = filtered_df.groupby('행정동코드')[pop_col].mean().sort_values(ascending=False).head(10).reset_index()
    dong_mean.columns = ['행정동코드', '평균인구수']
    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        dong_mean['행정동코드'] = dong_mean['행정동코드'].astype(str)
        fig8 = px.bar(dong_mean, x='행정동코드', y='평균인구수', title="상위 10개 행정동 평균 생활인구", color='행정동코드', text_auto='.0f')
        st.plotly_chart(fig8, use_container_width=True)
        # utils.save_plot(fig8, "chart8_top10_dong.png")
        
    desc8 = "필터링된 영역 내에서 가장 생활인구가 많은 상위 10개 행정동을 시각화합니다. 툴팁에 표시되는 정확한 값으로 특정 연령층이나 시간대에 집중된 지역이 어디인지 신속히 파악할 수 있습니다."
    with col_table:
        st.dataframe(dong_mean.set_index('행정동코드'))
        st.write(f"**해석**: {desc8}")
    charts_info.append({'fig': fig8, 'title': '상위 10개 행정동', 'filename': 'chart8_top10_dong.png', 'description': desc8, 'table_md': dong_mean.set_index('행정동코드').to_markdown()})
    st.markdown("---")

    # ---------------------------------------------------------
    # Chart 9: 시간대별 주요 5개 행정동 추이
    # ---------------------------------------------------------
    st.subheader("9. 최상위 5개 행정동의 시간대별 인구 변화 (다변량)")
    top5_dongs = dong_mean['행정동코드'][:5].astype(int) if not dong_mean.empty else []
    top5_df = filtered_df[filtered_df['행정동코드'].isin(top5_dongs)]
    time_dong_pivot = top5_df.pivot_table(index='시간대구분', columns='행정동코드', values=pop_col, aggfunc='mean').reset_index()
    
    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        if len(time_dong_pivot.columns) > 1:
            time_dong_pivot.columns = [str(c) for c in time_dong_pivot.columns]
            fig9 = px.line(time_dong_pivot, x='시간대구분', y=time_dong_pivot.columns[1:], title="최상위 5개 행정동의 시간대별 인구 변화", markers=True)
            fig9.update_xaxes(tickmode='linear', dtick=1)
            fig9.update_layout(yaxis_title="평균인구수", legend_title_text="행정동코드")
            st.plotly_chart(fig9, use_container_width=True)
            # utils.save_plot(fig9, "chart9_time_top5dong.png")
        else:
            st.warning("표시할 행정동 데이터가 없습니다.")
        
    desc9 = "가장 혼잡도가 높은 상위 5개 행정동을 추출하여 시간대별 인구 변동을 비교합니다. 범례를 사용해 특정 동만 분리해서 살펴보며 각 지역의 고유한 피크타임을 개별적으로 대조할 수 있습니다."
    with col_table:
        st.dataframe(time_dong_pivot.set_index('시간대구분').head(5))
        st.write(f"**해석**: {desc9}")
    charts_info.append({'fig': fig9, 'title': '최상위 5개 행정동 시간대별 추이', 'filename': 'chart9_time_top5dong.png', 'description': desc9, 'table_md': time_dong_pivot.set_index('시간대구분').head().to_markdown()})
    st.markdown("---")

    # ---------------------------------------------------------
    # Chart 10: 성별 x 연령대별 인구 피벗 (그룹바 차트)
    # ---------------------------------------------------------
    st.subheader("10. 성별 및 연령대 교차 분석 (그룹바 차트)")
    gender_age_pivot = filtered_df.pivot_table(index='연령대', columns='성별', values=pop_col, aggfunc='mean').reset_index()
    
    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        if len(gender_age_pivot.columns) > 1:
            fig10 = px.bar(gender_age_pivot, x='연령대', y=gender_age_pivot.columns[1:], title="연령대별 성별 생활인구 차이 비교", barmode='group')
            fig10.update_layout(yaxis_title="평균인구수", legend_title_text="성별")
            st.plotly_chart(fig10, use_container_width=True)
            # utils.save_plot(fig10, "chart10_gender_age.png")
        else:
            st.warning("교차 분석할 데이터가 부족합니다.")
            
    desc10 = "연령대 내부에서 성별 간의 인구 밀집도 차이를 비교 분석한 그룹바 차트입니다. 서로 나란히 배치된 막대를 통해 두 성별 그룹의 격차를 인터랙티브하게 마우스 오버하여 즉시 확인할 수 있습니다."
    with col_table:
        st.dataframe(gender_age_pivot.set_index('연령대'))
        st.write(f"**해석**: {desc10}")
    charts_info.append({'fig': fig10, 'title': '성별 및 연령대 교차 분석', 'filename': 'chart10_gender_age.png', 'description': desc10, 'table_md': gender_age_pivot.set_index('연령대').to_markdown()})
    st.markdown("---")

    # ---------------------------------------------------------
    # Chart 11: 주야간 인구 비중 (파이 차트)
    # ---------------------------------------------------------
    st.subheader("11. 오전/오후(주야간) 생활인구 비교")
    df_temp = filtered_df[['시간대구분', pop_col]].copy()
    df_temp['주야간'] = df_temp['시간대구분'].apply(lambda x: '오전(0-11시)' if x < 12 else '오후(12-23시)')
    ampm_mean = df_temp.groupby('주야간')[pop_col].mean().reset_index()
    ampm_mean.columns = ['주야간', '평균인구수']
    
    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        fig11 = px.pie(ampm_mean, values='평균인구수', names='주야간', title="주야간 생활인구 비중 (도넛 차트)", hole=0.4, color_discrete_sequence=['#ff9999','#66b3ff'])
        st.plotly_chart(fig11, use_container_width=True)
        # utils.save_plot(fig11, "chart11_ampm.png")
        
    desc11 = "하루 24시간을 주/야간 두 축으로 나누어 전체 활동 비중을 보여주는 도넛 형태의 파이 차트입니다. 각 영역을 클릭하거나 호버하여 정확한 퍼센테이지와 값을 유연하게 탐색할 수 있습니다."
    with col_table:
        st.dataframe(ampm_mean.set_index('주야간'))
        st.write(f"**해석**: {desc11}")
    charts_info.append({'fig': fig11, 'title': '주야간 생활인구 비교', 'filename': 'chart11_ampm.png', 'description': desc11, 'table_md': ampm_mean.set_index('주야간').to_markdown()})
    st.markdown("---")

    # ---------------------------------------------------------
    # Chart 12: 연령대별 생활인구 박스플롯 (샘플링)
    # ---------------------------------------------------------
    st.subheader("12. 연령대별 인구 분포 범위 (박스플롯)")
    sample_size = min(50000, len(filtered_df)) # Plotly 렌더링 성능을 위해 5만건으로 조정
    if sample_size > 0:
        sample_df = filtered_df.sample(n=sample_size, random_state=42)
    else:
        sample_df = filtered_df.copy()
        
    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        if not sample_df.empty:
            fig12 = px.box(sample_df, x='연령대', y=pop_col, title="연령대별 인구 밀집도 분포 및 이상치 파악", color='연령대')
            st.plotly_chart(fig12, use_container_width=True)
            # utils.save_plot(fig12, "chart12_age_boxplot.png")
        
    desc12 = "각 연령대의 평균 뿐만 아니라 1~3사분위 범위, 이상치(Outlier) 점들을 모두 렌더링한 인터랙티브 박스플롯입니다. 극단값 점에 마우스를 올려 정확한 수치 정보를 탐색할 수 있어 이상치 분석에 탁월합니다."
    with col_table:
        if not sample_df.empty:
            st.dataframe(sample_df.groupby('연령대')[pop_col].describe()[['mean', 'std', 'min', 'max']])
        st.write(f"**해석**: {desc12}")
    if not sample_df.empty:
        charts_info.append({'fig': fig12, 'title': '연령대별 분포 범위', 'filename': 'chart12_age_boxplot.png', 'description': desc12, 'table_md': sample_df.groupby('연령대')[pop_col].describe().to_markdown()})
    st.markdown("---")

    # ---------------------------------------------------------
    # Chart 13: 전체 생활인구 히스토그램
    # ---------------------------------------------------------
    st.subheader("13. 전체 생활인구 빈도 분포도 (히스토그램)")
    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        if not sample_df.empty:
            fig13 = px.histogram(sample_df, x=pop_col, nbins=50, title="전체 생활인구 빈도 분포도", marginal="box", opacity=0.7, color_discrete_sequence=['teal'])
            st.plotly_chart(fig13, use_container_width=True)
            # utils.save_plot(fig13, "chart13_pop_hist.png")
        
    desc13 = "생활인구수 데이터가 어떤 분포를 가지는지 50개의 구간(Bin)으로 나눈 히스토그램입니다. 상단에 첨부된 미니 박스플롯을 통해 분포의 치우침을 다각도로 확인할 수 있는 심층 분석 차트입니다."
    with col_table:
        if not sample_df.empty:
            st.write(sample_df[pop_col].describe())
        st.write(f"**해석**: {desc13}")
    charts_info.append({'fig': fig13, 'title': '전체 인구 분포 빈도도', 'filename': 'chart13_pop_hist.png', 'description': desc13, 'table_md': ""})
    st.markdown("---")

    # ---------------------------------------------------------
    # Chart 14: 시간대 x 연령대 히트맵
    # ---------------------------------------------------------
    st.subheader("14. 시간대 및 연령대 집중도 매트릭스 (Heatmap)")
    time_age_pivot = filtered_df.pivot_table(index='시간대구분', columns='연령대', values=pop_col, aggfunc='mean')
    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        if not time_age_pivot.empty:
            fig14 = px.imshow(time_age_pivot, labels=dict(x="연령대", y="시간대구분", color="평균인구수"),
                              x=time_age_pivot.columns, y=time_age_pivot.index,
                              title="시간대 x 연령대 집중도 히트맵", color_continuous_scale='YlOrRd', aspect='auto')
            st.plotly_chart(fig14, use_container_width=True)
            # utils.save_plot(fig14, "chart14_time_age_heatmap.png")
        
    desc14 = "24개 시간대와 모든 연령대 간의 조합을 2차원 히트맵으로 그려냅니다. 마우스를 블록 위로 올리면 해당 조합의 정확한 평균 인구수를 알려주어 시각적으로 두드러진 핫스팟의 규모를 즉각 파악 가능합니다."
    with col_table:
        st.dataframe(time_age_pivot.iloc[:10, :5])
        st.write(f"**해석**: {desc14}")
    charts_info.append({'fig': fig14, 'title': '시간대 x 연령대 매트릭스', 'filename': 'chart14_time_age_heatmap.png', 'description': desc14, 'table_md': time_age_pivot.head().to_markdown()})
    st.markdown("---")

    # ---------------------------------------------------------
    # Chart 15: 성별 x 주야간 인구 스택 비교
    # ---------------------------------------------------------
    st.subheader("15. 성별에 따른 주/야간 활동 인구 비교 (누적 막대)")
    df_temp['성별'] = filtered_df['성별']
    gender_ampm_pivot = df_temp.pivot_table(index='주야간', columns='성별', values=pop_col, aggfunc='mean').reset_index()
    
    col_chart, col_table = st.columns([2, 1])
    with col_chart:
        if len(gender_ampm_pivot.columns) > 1:
            fig15 = px.bar(gender_ampm_pivot, x='주야간', y=gender_ampm_pivot.columns[1:], title="주/야간 성별 인구 구성비율 시각화", barmode='stack')
            fig15.update_layout(yaxis_title="평균인구수", legend_title_text="성별")
            st.plotly_chart(fig15, use_container_width=True)
            # utils.save_plot(fig15, "chart15_gender_ampm_stack.png")
        
    desc15 = "오전/오후라는 거시적 시간대 내에서 성별의 절대적 규모와 구성비를 누적 막대 형태로 보여줍니다. 마우스 호버로 각 블록의 실제 값과 비중을 정밀하게 탐색할 수 있는 직관적인 스택 차트입니다."
    with col_table:
        st.dataframe(gender_ampm_pivot.set_index('주야간'))
        st.write(f"**해석**: {desc15}")
    charts_info.append({'fig': fig15, 'title': '성별 x 주야간 스택 비교', 'filename': 'chart15_gender_ampm_stack.png', 'description': desc15, 'table_md': gender_ampm_pivot.set_index('주야간').to_markdown()})
    st.markdown("---")
    
    st.success("✅ Plotly 기반 15개 인터랙티브 시각화 생성 완료!")

with tab3:
    st.header("📄 분석 리포트 생성 및 확인")
    st.write("위 탭들에서 생성된 모든 Plotly 차트 이미지와 필터 조건이 반영된 통계 보고서를 하나의 마크다운 리포트로 자동 생성합니다.")
    
    if st.button("현재 필터 상태로 EDA 리포트 생성하기 (report/eda_report.md)"):
        with st.spinner("리포트에 포함할 시각화 차트 이미지를 추출하고 리포트를 생성 중입니다. (약 5~10초 소요)..."):
            for info in charts_info:
                if 'fig' in info and info['fig'] is not None:
                    utils.save_plot(info['fig'], info['filename'])
            report_path = utils.generate_report_markdown(charts_info)
        st.success(f"리포트 생성 완료! 워크스페이스 내 '{report_path}' 경로에서 확인하실 수 있습니다.")
        
        with open(report_path, "r", encoding='utf-8') as f:
            st.markdown(f.read())

with tab4:
    st.header("🗺️ 서울시 생활인구 코로플리스 지도 (Folium)")
    st.markdown("좌측 사이드바 필터(시간대 등)에 따라 실시간으로 변동되는 서울시의 생활인구 밀집도를 지도로 확인합니다.")
    
    map_view_type = st.radio("지도 집계 기준 선택:", options=["구별 보기", "행정동별 보기"], horizontal=True)
    
    with st.spinner("지도 데이터를 집계하고 그리는 중입니다..."):
        # 기본 지도 객체 생성 (서울 중심)
        m = folium.Map(location=[37.5665, 126.9780], zoom_start=11, tiles="CartoDB positron")
        
        if map_view_type == "구별 보기":
            map_df = utils.load_map_gu()
            if selected_times:
                map_df = map_df[map_df['시간대구분'].isin(selected_times)]
            gu_pop = map_df.groupby(['GU_CD', 'CT_NM'])[pop_col].mean().reset_index()
            
            geo_data = utils.get_geojson('gu')
            gu_pop_dict = gu_pop.set_index('GU_CD')[pop_col].to_dict()
            for f in geo_data['features']:
                code = f['properties']['code']
                f['properties']['pop'] = f"{gu_pop_dict.get(code, 0):,.1f}"
            
            choropleth = folium.Choropleth(
                geo_data=geo_data,
                data=gu_pop,
                columns=['GU_CD', pop_col],
                key_on='feature.properties.code',
                fill_color='YlOrRd',
                fill_opacity=0.7,
                line_opacity=0.2,
                legend_name='평균 생활인구수'
            )
            choropleth.add_to(m)
            
            choropleth.geojson.add_child(
                folium.features.GeoJsonTooltip(
                    fields=['name', 'pop'],
                    aliases=['시군구명:', '평균 생활인구수:'],
                    labels=True
                )
            )
            
            st_folium(m, width=1000, height=600, returned_objects=[])
            
            st.write("### 구별 인구 데이터 표")
            st.dataframe(gu_pop.sort_values(by=pop_col, ascending=False).set_index('CT_NM'))
            
        else:
            map_df = utils.load_map_dong()
            if selected_times:
                map_df = map_df[map_df['시간대구분'].isin(selected_times)]
            dong_pop = map_df.groupby(['H_SDNG_CD', 'H_DNG_NM'])[pop_col].mean().reset_index()
            dong_pop['H_SDNG_CD'] = dong_pop['H_SDNG_CD'].astype(str)
            
            geo_data = utils.get_geojson('dong')
            dong_pop_dict = dong_pop.set_index('H_SDNG_CD')[pop_col].to_dict()
            for f in geo_data['features']:
                code = f['properties']['code']
                f['properties']['pop'] = f"{dong_pop_dict.get(code, 0):,.1f}"
            
            choropleth = folium.Choropleth(
                geo_data=geo_data,
                data=dong_pop,
                columns=['H_SDNG_CD', pop_col],
                key_on='feature.properties.code',
                fill_color='YlOrRd',
                fill_opacity=0.7,
                line_opacity=0.2,
                legend_name='평균 생활인구수'
            )
            choropleth.add_to(m)
            
            choropleth.geojson.add_child(
                folium.features.GeoJsonTooltip(
                    fields=['name', 'pop'],
                    aliases=['행정동명:', '평균 생활인구수:'],
                    labels=True
                )
            )
            
            st_folium(m, width=1000, height=600, returned_objects=[])
            
            st.write("### 동별 인구 데이터 표")
            st.dataframe(dong_pop.sort_values(by=pop_col, ascending=False).set_index('H_DNG_NM'))
