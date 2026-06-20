"""
이 모듈은 탐색적 데이터 분석(EDA) 과정에서 도출된 핵심 인사이트를
Streamlit 대시보드 상에서 인터랙티브 Plotly 시각화와 함께 제공하는 서브 페이지입니다.
주요 기능:
- 관광 소비 데이터 2종 로드 및 시각화 (업종별 추이, 국가별 비중)
- 외국인 방문자 데이터 3종 로드 및 시각화 (방문자 추이, 거주지 및 입국 국적 비중)
- 마크다운을 활용한 데이터 분석 결과 요약 리포팅
"""

import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

try:
    from src.styles import apply_custom_style
except ModuleNotFoundError:
    from styles import apply_custom_style

st.set_page_config(page_title="EDA 분석 인사이트", page_icon="💡", layout="wide")
apply_custom_style()

st.title("💡 탐색적 데이터 분석(EDA) 통합 인사이트")
st.markdown("본 페이지는 2025년 6월 ~ 2026년 5월까지의 **관광 소비 트렌드** 및 **방한 외국인 세부 현황**에 대한 빅데이터 기반 EDA 분석 결과를 요약하여 제공합니다.")
st.markdown("---")

# 데이터 경로 설정
data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')

@st.cache_data
def load_data():
    df_consume_trend = pd.read_csv(os.path.join(data_dir, '20260620155141_업종별 관광소비 추이 CSV 다운로드.csv'))
    df_consume_country = pd.read_csv(os.path.join(data_dir, '20260620155314_국가별 관광소비 유형 CSV 다운로드.csv'))
    df_visitor_region = pd.read_csv(os.path.join(data_dir, '20260620154323_외국인 지역별 방문자 수 추이.csv'))
    df_visitor_residence = pd.read_csv(os.path.join(data_dir, '20260620154411_외국인 방문자 거주지(국가).csv'))
    df_entry = pd.read_csv(os.path.join(data_dir, '20260620155533_입국자 국적별 입국현황.csv'))
    
    # 전처리
    df_consume_trend['기준년월일'] = df_consume_trend['기준년월일'].astype(str)
    df_visitor_region['날짜'] = df_visitor_region['날짜'].astype(str)
    
    return df_consume_trend, df_consume_country, df_visitor_region, df_visitor_residence, df_entry

try:
    df_consume_trend, df_consume_country, df_visitor_region, df_visitor_residence, df_entry = load_data()
except Exception as e:
    st.error(f"데이터를 불러오는 중 오류가 발생했습니다: {e}")
    st.stop()


# =========================================================
# 섹션 1: 관광 소비 부문
# =========================================================
st.header("1. 💳 업종별 및 국가별 관광 소비 쏠림 현상")

st.markdown("""
<div style='background-color:#F8FAFC; border-left: 4px solid #3B82F6; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>
<strong>핵심 요약</strong>: 전체 관광 소비액에서 <b>'쇼핑업'</b>이 독보적인 비중을 차지하며 산업 성장을 견인하고 있습니다.
특히 2026년 봄(3~5월) 시즌에 쇼핑업, 숙박업, 의료/웰니스업 등 핵심 부문의 소비가 급상승하는 뚜렷한 <b>성수기(계절성) 효과</b>가 나타납니다.
소비의 주체 역시 <b>미국, 중국, 일본</b> 등 상위 3개국이 전체 수요의 절반 이상을 독식하고 있는 롱테일(양극화) 구조입니다.
</div>
""", unsafe_allow_html=True)

col1, col2 = st.columns(2)

with col1:
    st.subheader("업종별 월간 관광 소비 추이")
    df_trend_pivot = df_consume_trend[df_consume_trend['업종별 구분'] != '전체']
    fig1 = px.line(df_trend_pivot, x='기준년월일', y='소비액(천원)', color='업종별 구분',
                   markers=True, title="월별 주요 관광 소비 업종 매출 동향")
    fig1.update_layout(xaxis_title="연월", yaxis_title="소비액(천원)", legend_title="업종")
    st.plotly_chart(fig1, use_container_width=True)

with col2:
    st.subheader("외국인 방문객 주요 소비국 비율")
    df_country_top10 = df_consume_country[df_consume_country['국가'] != '기타'].nlargest(10, '소비 비율')
    fig2 = px.pie(df_country_top10, names='국가', values='소비 비율', hole=0.4,
                  title="한국 관광 소비 주도 상위 10개국 비율",
                  color_discrete_sequence=px.colors.sequential.Tealgrn)
    fig2.update_traces(textposition='inside', textinfo='percent+label')
    st.plotly_chart(fig2, use_container_width=True)


st.markdown("---")

# =========================================================
# 섹션 2: 외국인 방문자 부문
# =========================================================
st.header("2. 🗺️ 방문자 및 입국자 지역/국적 집중화 현상")

st.markdown("""
<div style='background-color:#F8FAFC; border-left: 4px solid #10B981; padding: 15px; border-radius: 5px; margin-bottom: 20px;'>
<strong>핵심 요약</strong>: 한국을 찾는 외국인 관광 시장은 철저히 <b>'소수 거점 지역 중심'</b> 및 <b>'소수 인접 국가 중심'</b>이라는 이중적 집중화 현상을 겪고 있습니다.
방문 지역은 <b>서울, 인천, 경기</b> 등 수도권과 <b>부산, 제주</b> 같은 주요 거점에 심하게 쏠려 있으며, 그 외 지방 도시들의 방문객 수는 매우 저조한 박스플롯 분포를 보입니다.
출신 국가 또한 중국(26%), 일본, 미국, 대만에 집중되어 있어, 관광 수입원 및 타겟의 전략적 다변화가 시급합니다.
</div>
""", unsafe_allow_html=True)

col3, col4 = st.columns(2)

with col3:
    st.subheader("방문객 상위 5개 지역 추이 변화")
    df_region_sum = df_visitor_region.groupby('지역')['외국인 방문자수'].sum().reset_index()
    top5_regions = df_region_sum.nlargest(5, '외국인 방문자수')['지역']
    df_top5 = df_visitor_region[df_visitor_region['지역'].isin(top5_regions)]
    
    fig3 = px.line(df_top5, x='날짜', y='외국인 방문자수', color='지역', markers=True,
                   title="주요 관광 거점(상위 5개 지역) 쏠림 및 성장 추이")
    fig3.update_layout(xaxis_title="연월", yaxis_title="외국인 방문자수")
    st.plotly_chart(fig3, use_container_width=True)

with col4:
    st.subheader("방한 주요 국적별 입국자 총량")
    df_entry_top10 = df_entry.nlargest(10, '입국자 수(명)')
    fig4 = px.bar(df_entry_top10, x='입국자 수(명)', y='입국자 국적', orientation='h',
                  title="국적별 입국자 수 압도적 1위 중국 및 동아시아 강세",
                  color='입국자 수(명)', color_continuous_scale='Purples')
    fig4.update_layout(yaxis={'categoryorder': 'total ascending'})
    st.plotly_chart(fig4, use_container_width=True)


# 추가 히트맵 섹션 (방문 집중도)
st.subheader("지역별 성수기(봄철) 수요 집중도")
df_heatmap = df_visitor_region.pivot(index='지역', columns='날짜', values='외국인 방문자수')
fig5 = go.Figure(data=go.Heatmap(
    z=df_heatmap.values,
    x=df_heatmap.columns,
    y=df_heatmap.index,
    colorscale='Oranges'
))
fig5.update_layout(title="전국 지자체별/월별 방한 외국인 규모 히트맵", xaxis_title="연월", yaxis_title="지역")
st.plotly_chart(fig5, use_container_width=True)

st.info("📊 **결론 및 시사점**: K-콘텐츠 융합을 통해 인프라를 지방으로 확장하여, 특정 국가에 편중된 의존도를 낮추고 로컬 체류형 관광 상품을 육성하는 것이 필수적입니다.")
