"""
방한 외래관광객의 상세 통계를 다각도로 분석하여 시각화하는 Streamlit 서브 페이지입니다.

주요 기능:
- 기간별(연도/월) 외래 관광객 필터링 기능
- 입국 목적별, 성별, 연령대별 점유율 및 복합 상관관계 시각화 (Plotly 인터랙티브 차트 사용)
- 인구통계학적 특성 요약 교차표 제시
"""

import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.odcloud_api import get_foreigner_monthly_data
try:
    from src.styles import apply_custom_style
except ModuleNotFoundError:
    from styles import apply_custom_style

st.set_page_config(page_title="방한 외래객 트렌드 분석", page_icon="📈", layout="wide")

# 커스텀 CSS 스타일 적용
apply_custom_style()

st.title("📈 방한 외래관광객 트렌드 분석")
st.markdown("글로벌 외래 관광객의 입국 트렌드와 인구통계학적 세그먼트 분석을 제공합니다.")
st.markdown("---")

# 데이터 불러오기
df_foreigner = get_foreigner_monthly_data()

if not df_foreigner.empty:
    # 연도 분리 필터 생성
    df_foreigner["연도"] = df_foreigner["기준연월"].str.split("-").str[0]
    df_foreigner["월"] = df_foreigner["기준연월"].str.split("-").str[1]
    
    # 사이드바 필터
    st.sidebar.header("📊 데이터 필터")
    selected_year = st.sidebar.selectbox("연도 선택", sorted(df_foreigner["연도"].unique()), index=len(df_foreigner["연도"].unique())-1)
    
    # 필터링된 데이터
    df_filtered = df_foreigner[df_foreigner["연도"] == selected_year]
    
    # 레이아웃 분할
    col1, col2 = st.columns(2)
    
    with col1:
        st.markdown(f"#### 1. {selected_year}년 성별/연령대별 교차 분포")
        df_gender_age = df_filtered.groupby(["연령별", "성별"])["인원수"].sum().reset_index()
        fig_gender_age = px.bar(
            df_gender_age, x="연령별", y="인원수", color="성별",
            labels={"인원수": "관광객 수(명)", "연령별": "연령대"},
            barmode="group",
            color_discrete_map={"여성": "#EF4444", "남성": "#3B82F6"}
        )
        fig_gender_age.update_traces(
            hovertemplate="<b>연령대</b>: %{x}<br><b>성별</b>: %{legendgroup}<br><b>관광객 수</b>: %{y:,.0f}명<extra></extra>"
        )
        fig_gender_age.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Pretendard, sans-serif", size=12),
            margin=dict(l=40, r=40, t=20, b=40),
            xaxis=dict(showgrid=False),
            yaxis=dict(showgrid=True, gridcolor="#F1F5F9")
        )
        st.plotly_chart(fig_gender_age, use_container_width=True)
        
        # 교차 피봇테이블 출력
        st.markdown("<br><br>", unsafe_allow_html=True)
        pivot_gender_age = df_filtered.pivot_table(index="연령별", columns="성별", values="인원수", aggfunc="sum")
        st.markdown("**[성별/연령별 관광객 히트맵 테이블]**")
        st.dataframe(pivot_gender_age.style.format("{:,.0f}").background_gradient(cmap="Blues", axis=None))
        
    with col2:
        # 국적 또는 목적별 동적 컬럼 선택
        target_col = "국적" if "국적" in df_filtered.columns else "목적별"
        st.markdown(f"#### 2. {selected_year}년 {target_col} 점유율")
        df_share = df_filtered.groupby(target_col)["인원수"].sum().reset_index()
        fig_share = px.pie(
            df_share, values="인원수", names=target_col,
            hole=0.4,
            color_discrete_sequence=["#3182CE", "#319795", "#ED8936", "#ECC94B", "#48BB78", "#9F7AEA"]
        )
        fig_share.update_traces(
            textposition='outside',
            hovertemplate="<b>%{label}</b><br>관광객 수: %{value:,.0f}명<br>비율: %{percent}<extra></extra>"
        )
        fig_share.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Pretendard, sans-serif", size=12),
            margin=dict(l=40, r=40, t=20, b=40)
        )
        st.plotly_chart(fig_share, use_container_width=True)
        
        # 통계표 출력
        st.markdown("<br><br>", unsafe_allow_html=True)
        st.markdown(f"**[{target_col}별 관광객 통계]**")
        st.dataframe(df_share.sort_values(by="인원수", ascending=False).style.format({"인원수": "{:,.0f}"}))

    st.markdown("---")
    
    # 다변량 시계열 분석 (월별 유입 패턴)
    st.markdown(f"#### 3. {selected_year}년 월별 입국 목적별 추이")
    df_monthly_purpose = df_filtered.groupby(["월", "목적별"])["인원수"].sum().reset_index()
    fig_monthly = px.line(
        df_monthly_purpose, x="월", y="인원수", color="목적별",
        labels={"인원수": "관광객 수(명)"},
        markers=True,
        color_discrete_sequence=["#3182CE", "#319795", "#ED8936", "#ECC94B", "#48BB78", "#9F7AEA"]
    )
    fig_monthly.update_traces(
        line=dict(width=3),  # [개선 12] 선 두께 증가
        marker=dict(size=8, line=dict(width=1, color="white")),
        hovertemplate="<b>목적별</b>: %{legendgroup}<br><b>관광객 수</b>: %{y:,.0f}명<extra></extra>"
    )
    fig_monthly.update_layout(
        hovermode="x unified",
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Pretendard, sans-serif", size=12),
        margin=dict(l=40, r=40, t=20, b=40),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9")
    )
    st.plotly_chart(fig_monthly, use_container_width=True)
    
else:
    st.error("분석할 데이터를 불러오지 못했습니다.")
