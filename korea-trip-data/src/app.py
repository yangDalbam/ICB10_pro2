"""
외래 관광객 트렌드 및 지역 관광 활성화를 위한 Streamlit 대시보드의 메인 진입점(App)입니다.

주요 기능:
- 프로젝트의 기획 의도 및 5단계 분석 프레임워크 소개
- 방한 외래객 주요 통계 요약 (KPI 카드) 및 유입 추이 시각화 (API 1 연동)
- 전국 지역별 관광 관심도 및 방문도 현황 시각화 (API 3 연동)
- 전국 관광 소비 다양성 및 업종별 카드 소비 비중 시각화 (API 2 연동)
- 다중 페이지(Multi-page) 내비게이션 지원 및 공통 레이아웃 설정
"""

import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.odcloud_api import get_foreigner_monthly_data
from api.kto_api import (
    get_area_service_demand,
    get_area_spend_diversity
)
try:
    from src.styles import apply_custom_style
except ModuleNotFoundError:
    from styles import apply_custom_style

# 페이지 환경설정 (고급 에스테틱 테마 적용)
st.set_page_config(
    page_title="Korea Trip Data랩 - 관광 대시보드",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="expanded"
)

# 커스텀 CSS 스타일 적용
apply_custom_style()

# 메인 헤더
st.title("🗺️ Korea Trip Data랩")
st.subheader("인바운드 관광 트렌드 및 지역 관광 활성화 분석 대시보드")
st.markdown("---")

# 기획 의도 소개 (Rich UI 카드 형태)
st.markdown("""
<div style="background: linear-gradient(135deg, #EFF6FF 0%, #DBEAFE 100%); border-left: 5px solid #2563EB; border-radius: 12px; padding: 1.5rem; margin-bottom: 2rem; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.05);">
    <h3 style="margin-top:0; color:#1E3A8A; font-size:1.3rem; font-weight:700; display:flex; align-items:center; gap:8px;">🎯 프로젝트 기획 의도</h3>
    <p style="margin:0; color:#1E40AF; font-size:1.05rem; line-height:1.7;">
        방한 외국인 관광객들의 <strong>특정 대도시(서울, 제주 등) 편중 현상</strong>을 해결하고, 잠재력 있는 지역 도시들의 관광 활성화를 모색합니다.<br>
        본 대시보드는 온라인 상의 <strong>관심도(SNS/검색)</strong>와 오프라인의 <strong>실제 행동(내비게이션 행선지/신용카드 소비)</strong> 데이터를 융합하여 분석을 전개합니다.
    </p>
</div>
""", unsafe_allow_html=True)

# 5단계 분석 프레임워크 요약 안내
st.markdown("### 🧭 5단계 분석 프레임워크 요약")
col_step1, col_step2, col_step3, col_step4, col_step5 = st.columns(5)

step_card_style = """
<div style="background-color: #FFFFFF; border: 1px solid #E2E8F0; border-radius: 12px; padding: 1rem; height: 160px; box-shadow: 0 4px 6px -1px rgba(0,0,0,0.02); display: flex; flex-direction: column; justify-content: flex-start; transition: transform 0.2s;">
    <span style="background-color: {color}; color: #FFFFFF; font-size: 0.75rem; font-weight: 700; padding: 2px 8px; border-radius: 9999px; width: fit-content; margin-bottom: 8px;">{step}</span>
    <h4 style="margin: 0 0 6px 0; color: #1E293B; font-size: 0.95rem; font-weight: 700;">{title}</h4>
    <p style="margin: 0; color: #64748B; font-size: 0.82rem; line-height: 1.5;">{desc}</p>
</div>
"""

with col_step1:
    st.markdown(step_card_style.format(step="1단계", color="#3B82F6", title="🔍 관심도 분석", desc="외국인이 주목하는 인기 관심 도시 랭킹 파악"), unsafe_allow_html=True)
with col_step2:
    st.markdown(step_card_style.format(step="2단계", color="#10B981", title="🚗 실제 방문 대조", desc="온라인의 관심이 오프라인 방문으로 연결되는지 분석"), unsafe_allow_html=True)
with col_step3:
    st.markdown(step_card_style.format(step="3단계", color="#F59E0B", title="🧩 도시 매트릭스", desc="성공 도시(도시1) vs 잠재 도시(도시2) 분류"), unsafe_allow_html=True)
with col_step4:
    st.markdown(step_card_style.format(step="4단계", color="#EF4444", title="💳 인프라 분석", desc="소비 패턴 및 연령/국적별 다양성 격차 규명"), unsafe_allow_html=True)
with col_step5:
    st.markdown(step_card_style.format(step="5단계", color="#8B5CF6", title="💡 벤치마킹", desc="성공 요소를 바탕으로 한 활성화 솔루션 도출"), unsafe_allow_html=True)

st.markdown("---")

# 메인 요약 KPI (방한 외래객 통계 연동)
st.markdown("### 📊 방한 외래객 유입 현황 요약 (API 1 연동)")
df_foreigner = get_foreigner_monthly_data()

if not df_foreigner.empty:
    # 2024년 데이터 추출
    df_2024 = df_foreigner[df_foreigner["기준연월"].str.startswith("2024", na=False)]
    total_foreigner_2024 = df_2024["인원수"].sum()
    
    # 2023년 데이터 추출 및 증감율 계산
    df_2023 = df_foreigner[df_foreigner["기준연월"].str.startswith("2023", na=False)]
    total_foreigner_2023 = df_2023["인원수"].sum()
    
    growth_rate = ((total_foreigner_2024 - total_foreigner_2023) / total_foreigner_2023) * 100 if total_foreigner_2023 > 0 else 0
    
    # 대표 목적지 (가장 많은 목적/성별/연령)
    top_purpose = df_foreigner.groupby("목적별")["인원수"].sum().idxmax()
    top_age = df_foreigner.groupby("연령별")["인원수"].sum().idxmax()
    
    # KPI 3열 구성
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    with kpi_col1:
        st.metric(
            label="2024년 방한 외래객 총수", 
            value=f"{total_foreigner_2024:,.0f} 명", 
            delta=f"전년 대비 {growth_rate:.1f}% 증가" if growth_rate > 0 else f"{growth_rate:.1f}%"
        )
    with kpi_col2:
        st.metric(label="핵심 입국 목적", value=top_purpose)
    with kpi_col3:
        st.metric(label="주요 방문 연령층", value=top_age)

    # 간단한 라인 차트 시각화
    st.markdown("#### 월별 외래 관광객 유입 추이")
    df_trend = df_foreigner.groupby("기준연월")["인원수"].sum().reset_index()
    fig = px.line(
        df_trend, x="기준연월", y="인원수", 
        labels={"인원수": "관광객 수(명)", "기준연월": "연월"},
        markers=True,
        color_discrete_sequence=["#3182CE"]
    )
    fig.update_traces(
        line=dict(width=3),
        marker=dict(size=8, symbol="circle", line=dict(width=2, color="white")),
        hovertemplate="<b>기준연월</b>: %{x}<br><b>관광객 수</b>: %{y:,.0f}명<extra></extra>"
    )
    fig.update_layout(
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Pretendard, sans-serif", size=12),
        margin=dict(l=40, r=40, t=20, b=40),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9")
    )
    st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("방한 외래객 데이터를 불러올 수 없습니다.")

st.markdown("---")

# 한국관광공사 API 추가 연동 섹션 1: 관심도 vs 실제 방문도
st.markdown("### 🗺️ 전국 지역별 관광 관심도 및 방문도 현황 (API 3 - AreaTarResDemService 연동)")
df_kto_demand = get_area_service_demand("202401")

if not df_kto_demand.empty:
    avg_sns = df_kto_demand["snsMentionCo"].mean()
    avg_navi = df_kto_demand["naviSearchCo"].mean()
    max_sns_city = df_kto_demand.loc[df_kto_demand["snsMentionCo"].idxmax(), "signguNm"]
    max_navi_city = df_kto_demand.loc[df_kto_demand["naviSearchCo"].idxmax(), "signguNm"]
    
    col_dem1, col_dem2, col_dem3, col_dem4 = st.columns(4)
    with col_dem1:
        st.metric(label="평균 SNS 언급량 (관심도)", value=f"{avg_sns:,.0f} 건")
    with col_dem2:
        st.metric(label="최고 관심 도시 (SNS)", value=max_sns_city)
    with col_dem3:
        st.metric(label="평균 내비게이션 검색수 (방문도)", value=f"{avg_navi:,.0f} 건")
    with col_dem4:
        st.metric(label="최고 방문 도시 (내비)", value=max_navi_city)
        
    col_chart1, col_chart2 = st.columns(2)
    with col_chart1:
        st.markdown("#### 🔥 온라인 관심도 (SNS 언급량) Top 5")
        df_top_sns = df_kto_demand.nlargest(5, "snsMentionCo")
        fig_sns = px.bar(
            df_top_sns, x="snsMentionCo", y="signguNm",
            orientation="h",
            labels={"snsMentionCo": "SNS 언급량 (건)", "signguNm": "시군구"},
            color="snsMentionCo",
            color_continuous_scale=["#FCA5A5", "#EF4444", "#991B1B"]
        )
        fig_sns.update_traces(
            hovertemplate="<b>시군구</b>: %{y}<br><b>SNS 언급량</b>: %{x:,.0f}건<extra></extra>"
        )
        fig_sns.update_layout(
            showlegend=False, 
            coloraxis_showscale=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Pretendard, sans-serif", size=12),
            margin=dict(l=40, r=40, t=10, b=40),
            xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
            yaxis=dict(categoryorder='total ascending', showgrid=False)
        )
        st.plotly_chart(fig_sns, use_container_width=True)
        
    with col_chart2:
        st.markdown("#### 🚗 실제 방문도 (내비게이션 검색수) Top 5")
        df_top_navi = df_kto_demand.nlargest(5, "naviSearchCo")
        fig_navi = px.bar(
            df_top_navi, x="naviSearchCo", y="signguNm",
            orientation="h",
            labels={"naviSearchCo": "내비게이션 검색수 (건)", "signguNm": "시군구"},
            color="naviSearchCo",
            color_continuous_scale=["#93C5FD", "#3B82F6", "#1E3A8A"]
        )
        fig_navi.update_traces(
            hovertemplate="<b>시군구</b>: %{y}<br><b>내비 검색수</b>: %{x:,.0f}건<extra></extra>"
        )
        fig_navi.update_layout(
            showlegend=False, 
            coloraxis_showscale=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Pretendard, sans-serif", size=12),
            margin=dict(l=40, r=40, t=10, b=40),
            xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
            yaxis=dict(categoryorder='total ascending', showgrid=False)
        )
        st.plotly_chart(fig_navi, use_container_width=True)
else:
    st.warning("관광 서비스 수요 데이터를 불러올 수 없습니다.")

st.markdown("---")

# 한국관광공사 API 추가 연동 섹션 2: 카드 소비 다양성
st.markdown("### 💳 전국 관광 카드 소비 다양성 및 업종별 비중 (API 2 - AreaTarDivService 연동)")
df_kto_spend = get_area_spend_diversity("202401")

if not df_kto_spend.empty:
    df_ind_spend = df_kto_spend.groupby("indutyNm")["cardUseAmt"].sum().reset_index()
    total_amt = df_ind_spend["cardUseAmt"].sum()
    df_ind_spend["비율"] = (df_ind_spend["cardUseAmt"] / total_amt) * 100
    
    col_sp1, col_sp2 = st.columns([1, 2])
    
    with col_sp1:
        st.markdown("#### 🛍️ 전국 관광 카드 소비 업종별 비중")
        fig_pie_spend = px.pie(
            df_ind_spend, values="cardUseAmt", names="indutyNm",
            hole=0.4,
            color_discrete_sequence=["#3182CE", "#319795", "#ED8936", "#ECC94B", "#48BB78", "#9F7AEA"]
        )
        fig_pie_spend.update_traces(
            textposition='inside', 
            textinfo='percent+label',
            hovertemplate="<b>업종</b>: %{label}<br><b>소비액</b>: %{value:,.0f}원 (%{percent})<extra></extra>"
        )
        fig_pie_spend.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Pretendard, sans-serif", size=12),
            margin=dict(l=40, r=40, t=10, b=40)
        )
        st.plotly_chart(fig_pie_spend, use_container_width=True)
        
    with col_sp2:
        st.markdown("#### 💰 전국 시군구별 관광 카드 총 소비 규모 Top 5")
        df_city_spend = df_kto_spend.groupby("signguNm")["cardUseAmt"].sum().reset_index()
        df_top_city_spend = df_city_spend.nlargest(5, "cardUseAmt")
        fig_city_spend = px.bar(
            df_top_city_spend, x="cardUseAmt", y="signguNm",
            orientation="h",
            labels={"cardUseAmt": "카드 소비액 (원)", "signguNm": "시군구"},
            color="cardUseAmt",
            color_continuous_scale=["#C7D2FE", "#6366F1", "#3730A3"]
        )
        fig_city_spend.update_traces(
            hovertemplate="<b>시군구</b>: %{y}<br><b>카드 소비액</b>: %{x:,.0f}원<extra></extra>"
        )
        fig_city_spend.update_layout(
            coloraxis_showscale=False,
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Pretendard, sans-serif", size=12),
            margin=dict(l=40, r=40, t=10, b=40),
            xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
            yaxis=dict(categoryorder='total ascending', showgrid=False)
        )
        st.plotly_chart(fig_city_spend, use_container_width=True)
        
    food_ratio = df_ind_spend.loc[df_ind_spend["indutyNm"] == "식음료", "비율"].values[0] if "식음료" in df_ind_spend["indutyNm"].values else 0
    shopping_ratio = df_ind_spend.loc[df_ind_spend["indutyNm"] == "쇼핑", "비율"].values[0] if "쇼핑" in df_ind_spend["indutyNm"].values else 0
    stay_ratio = df_ind_spend.loc[df_ind_spend["indutyNm"] == "숙박", "비율"].values[0] if "숙박" in df_ind_spend["indutyNm"].values else 0
    
    st.info(f"""
    💡 **관광 소비 인사이트 요약**:
    - 전국 관광 카드 소비액 중 **식음료** 업종이 **{food_ratio:.1f}%**로 가장 높은 비중을 차지하고 있으며, 이어서 **쇼핑({shopping_ratio:.1f}%)**, **숙박({stay_ratio:.1f}%)** 순입니다.
    - 대시보드의 **'2_Tourism_Diversity'** 및 **'3_Demand_Analysis'** 서브 페이지에서 특정 시군구의 소비 편중도를 이 전국 평균 수치와 대조하여, 체류 인프라(숙박)나 연계 쇼핑 시설의 확충이 필요한 잠재 도시를 상세히 분석할 수 있습니다.
    """)
else:
    st.warning("관광 소비 다양성 데이터를 불러올 수 없습니다.")

st.markdown("---")
st.markdown("👈 왼쪽 사이드바 메뉴를 통해 **방한 트렌드**, **도시 분류 매트릭스**, **도시 1:1 심층 비교** 페이지로 이동하여 상세 분석을 시작해 보세요!")
