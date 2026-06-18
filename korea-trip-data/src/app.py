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
from datetime import datetime
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

# 메인 헤더 영역
col_title, col_date = st.columns([4, 1])
with col_title:
    st.title("🇰🇷 한국 관광 데이터 대시보드")
    st.caption("공공 데이터를 기반으로 한 국내 관광 트렌드 및 분석 현황 (온/오프라인 행동 융합)")
with col_date:
    today_str = datetime.today().strftime("%Y-%m-%d")
    st.markdown(f"<div style='text-align: right; color: #64748B; padding-top: 2rem; font-size: 0.9rem;'>Data updated: {today_str}</div>", unsafe_allow_html=True)

st.write("---")

# 메인 요약 KPI (방한 외래객 통계 연동)
st.markdown("### 📊 방한 외래객 유입 현황 요약 (API 1 연동)")
df_foreigner = get_foreigner_monthly_data()

if not df_foreigner.empty:
    # 2026년 데이터 추출
    df_2026 = df_foreigner[df_foreigner["기준연월"].str.startswith("2026", na=False)]
    total_foreigner_2026 = df_2026["인원수"].sum()
    
    # 2025년 데이터 추출 및 증감율 계산
    df_2025 = df_foreigner[df_foreigner["기준연월"].str.startswith("2025", na=False)]
    total_foreigner_2025 = df_2025["인원수"].sum()
    
    growth_rate = ((total_foreigner_2026 - total_foreigner_2025) / total_foreigner_2025) * 100 if total_foreigner_2025 > 0 else 0
    
    # 대표 목적지 (가장 많은 목적/성별/연령)
    top_purpose = df_foreigner.groupby("목적별")["인원수"].sum().idxmax()
    top_age = df_foreigner.groupby("연령별")["인원수"].sum().idxmax()
    
    # KPI 3열 구성
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    with kpi_col1:
        st.metric(
            label="2026년 방한 외래객 총수", 
            value=f"{total_foreigner_2026:,.0f} 명"
        )
    with kpi_col2:
        st.metric(label="핵심 입국 목적", value=top_purpose)
    with kpi_col3:
        st.metric(label="주요 방문 연령층", value=top_age)

    # 간단한 라인 차트 시각화
    with st.container():
        st.markdown("#### 월별 외래 관광객 유입 추이")
        df_trend = df_foreigner.groupby("기준연월")["인원수"].sum().reset_index()
        fig = px.line(
            df_trend, x="기준연월", y="인원수", 
            labels={"인원수": "관광객 수(명)", "기준연월": "연월"},
            markers=True,
            color_discrete_sequence=["#1E3A8A"] # Dark Navy
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
            font=dict(family="Pretendard, sans-serif", size=12, color="#4A5568"),
            margin=dict(l=40, r=40, t=20, b=40),
            xaxis=dict(showgrid=False, zeroline=False),
            yaxis=dict(showgrid=True, gridcolor="rgba(0,0,0,0.05)", zeroline=False)
        )
        st.plotly_chart(fig, use_container_width=True)
else:
    st.warning("방한 외래객 데이터를 불러올 수 없습니다.")

st.markdown("---")

# 한국관광공사 API 추가 연동 섹션 1: 관심도 vs 실제 방문도
st.markdown("### 🗺️ 전국 지역별 관광 관심도 및 방문도 현황 (API 3 - AreaTarResDemService 연동)")
df_kto_demand = get_area_service_demand("202601")

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
        
    with st.container():
        col_chart1, col_chart2 = st.columns(2)
        with col_chart1:
            st.markdown("#### 🔥 온라인 관심도 (SNS)")
            df_top_sns = df_kto_demand.nlargest(5, "snsMentionCo")
            fig_sns = px.bar(
                df_top_sns, x="snsMentionCo", y="signguNm",
                orientation="h",
                labels={"snsMentionCo": "SNS 언급량 (건)", "signguNm": "시군구"},
                color="snsMentionCo",
                color_continuous_scale=["#93C5FD", "#3B82F6", "#2563EB"] # Vibrant Blue
            )
            fig_sns.update_traces(
                hovertemplate="<b>시군구</b>: %{y}<br><b>SNS 언급량</b>: %{x:,.0f}건<extra></extra>",
                texttemplate='%{x:,.0f}', textposition='outside'
            )
            fig_sns.update_layout(
                showlegend=False, 
                coloraxis_showscale=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Pretendard, sans-serif", size=12, color="#4A5568"),
                margin=dict(l=40, r=40, t=10, b=40),
                xaxis=dict(showgrid=False, zeroline=False, visible=False),
                yaxis=dict(categoryorder='total ascending', showgrid=False)
            )
            st.plotly_chart(fig_sns, use_container_width=True)
            
        with col_chart2:
            st.markdown("#### 🚗 실제 방문도 (내비)")
            df_top_navi = df_kto_demand.nlargest(5, "naviSearchCo")
            fig_navi = px.bar(
                df_top_navi, x="naviSearchCo", y="signguNm",
                orientation="h",
                labels={"naviSearchCo": "내비게이션 검색수 (건)", "signguNm": "시군구"},
                color="naviSearchCo",
                color_continuous_scale=["#A7F3D0", "#10B981", "#059669"] # Vibrant Emerald
            )
            fig_navi.update_traces(
                hovertemplate="<b>시군구</b>: %{y}<br><b>내비 검색수</b>: %{x:,.0f}건<extra></extra>",
                texttemplate='%{x:,.0f}', textposition='outside'
            )
            fig_navi.update_layout(
                showlegend=False, 
                coloraxis_showscale=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Pretendard, sans-serif", size=12, color="#4A5568"),
                margin=dict(l=40, r=40, t=10, b=40),
                xaxis=dict(showgrid=False, zeroline=False, visible=False),
                yaxis=dict(categoryorder='total ascending', showgrid=False)
            )
            st.plotly_chart(fig_navi, use_container_width=True)
else:
    st.warning("관광 서비스 수요 데이터를 불러올 수 없습니다.")

st.markdown("---")

# 한국관광공사 API 추가 연동 섹션 2: 카드 소비 다양성
st.markdown("### 💳 전국 관광 카드 소비 다양성 및 업종별 비중 (API 2 - AreaTarDivService 연동)")
df_kto_spend = get_area_spend_diversity("202601")

if not df_kto_spend.empty:
    df_ind_spend = df_kto_spend.groupby("indutyNm")["cardUseAmt"].sum().reset_index()
    total_amt = df_ind_spend["cardUseAmt"].sum()
    df_ind_spend["비율"] = (df_ind_spend["cardUseAmt"] / total_amt) * 100
    
    with st.container():
        col_sp1, col_sp2 = st.columns([1, 2])
        
        with col_sp1:
            st.markdown("#### 🛍️ 전국 관광 소비 비중")
            fig_pie_spend = px.pie(
                df_ind_spend, values="cardUseAmt", names="indutyNm",
                hole=0.4,
                color_discrete_sequence=["#2563EB", "#0EA5E9", "#10B981", "#F59E0B", "#8B5CF6", "#64748B"] # Vibrant palette
            )
            fig_pie_spend.update_traces(
                textposition='inside', 
                textinfo='percent+label',
                hovertemplate="<b>업종</b>: %{label}<br><b>소비액</b>: %{value:,.0f}원 (%{percent})<extra></extra>"
            )
            fig_pie_spend.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Pretendard, sans-serif", size=12, color="#4A5568"),
                margin=dict(l=40, r=40, t=10, b=40),
                showlegend=False # 깔끔하게 숨기고 inside label로 처리
            )
            st.plotly_chart(fig_pie_spend, use_container_width=True)
            
        with col_sp2:
            st.markdown("#### 💰 전국 관광 총 소비 규모 Top 5")
            df_city_spend = df_kto_spend.groupby("signguNm")["cardUseAmt"].sum().reset_index()
            df_top_city_spend = df_city_spend.nlargest(5, "cardUseAmt")
            fig_city_spend = px.bar(
                df_top_city_spend, x="cardUseAmt", y="signguNm",
                orientation="h",
                labels={"cardUseAmt": "카드 소비액 (원)", "signguNm": "시군구"},
                color="cardUseAmt",
                color_continuous_scale=["#93C5FD", "#3B82F6", "#2563EB"] # Vibrant Blue
            )
            fig_city_spend.update_traces(
                hovertemplate="<b>시군구</b>: %{y}<br><b>카드 소비액</b>: %{x:,.0f}원<extra></extra>",
                texttemplate='%{x:,.0f}', textposition='outside'
            )
            fig_city_spend.update_layout(
                coloraxis_showscale=False,
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Pretendard, sans-serif", size=12, color="#4A5568"),
                margin=dict(l=40, r=40, t=10, b=40),
                xaxis=dict(showgrid=False, zeroline=False, visible=False),
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
