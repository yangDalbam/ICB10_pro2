"""
홈 화면 뷰 모듈입니다.
주요 기능: 
- 방한 외래객 KPI 요약 제공
- 월별 유입 추이 차트 시각화
"""
import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime
from api.odcloud_api import get_foreigner_monthly_data

def render_home():
    # 메인 헤더 영역
    col_title, col_date = st.columns([4, 1])
    with col_title:
        st.title("🇰🇷 한국 관광 데이터 대시보드")
        st.caption("공공 데이터를 기반으로 한 국내 관광 트렌드 및 분석 현황 (온/오프라인 행동 융합)")
        st.caption("🔹 **자료 출처:** 한국관광공사(한국관광 데이터랩), 공공데이터포털(ODCloud)")
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
                font=dict(family="Pretendard, sans-serif", size=14, color="#334155"),
                hoverlabel=dict(bgcolor="white", font_size=13, font_family="Pretendard"),
                margin=dict(l=20, r=20, t=30, b=20),
                xaxis=dict(showgrid=False, zeroline=False, linecolor="#E2E8F0"),
                yaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False, linecolor="#E2E8F0")
            )
            st.plotly_chart(fig, use_container_width=True)
    else:
        st.warning("방한 외래객 데이터를 불러올 수 없습니다.")
