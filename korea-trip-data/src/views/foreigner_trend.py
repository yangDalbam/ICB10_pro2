"""
방한 외래객 추이 분석 모듈입니다.
주요 기능:
- 성별/연령대별 교차 분포, 국적 점유율
- 방문자/입국자 국적 집중화 현상 분석
"""
import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.odcloud_api import get_foreigner_monthly_data

def render_foreigner_trend():
    st.title("📈 방한 외래관광객 트렌드 분석")
    st.markdown("글로벌 외래 관광객의 입국 트렌드와 인구통계학적 세그먼트 분석을 제공합니다.")
    st.caption("🔹 **자료 출처:** 한국관광공사(한국관광 데이터랩), 공공데이터포털(ODCloud)")
    st.markdown("---")

    df_foreigner = get_foreigner_monthly_data()
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')
    
    @st.cache_data
    def load_eda_data():
        return pd.read_csv(os.path.join(data_dir, '20260620155533_입국자 국적별 입국현황.csv'))
    
    df_entry = None
    try:
        df_entry = load_eda_data()
    except Exception as e:
        st.warning(f"로컬 입국자 데이터를 불러올 수 없습니다: {e}")

    if not df_foreigner.empty:
        df_foreigner["연도"] = df_foreigner["기준연월"].str.split("-").str[0]
        df_foreigner["월"] = df_foreigner["기준연월"].str.split("-").str[1]

        st.header("📊 데이터 필터")
        selected_year = st.selectbox("연도 선택", sorted(df_foreigner["연도"].unique()), index=len(df_foreigner["연도"].unique())-1)
        df_filtered = df_foreigner[df_foreigner["연도"] == selected_year]

        col1, col2 = st.columns(2)
        with col1:
            st.markdown(f"#### 1. {selected_year}년 성별/연령대별 교차 분포")
            df_gender_age = df_filtered.groupby(["연령별", "성별"])["인원수"].sum().reset_index()
            fig_gender_age = px.bar(
                df_gender_age, x="연령별", y="인원수", color="성별",
                labels={"인원수": "관광객 수(명)", "연령별": "연령대"},
                barmode="group",
                color_discrete_map={"여성": "#F97316", "남성": "#2563EB"}
            )
            fig_gender_age.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Pretendard, sans-serif", size=14, color="#334155"),
                hoverlabel=dict(bgcolor="white", font_size=13, font_family="Pretendard"),
                margin=dict(l=20, r=20, t=30, b=20),
                xaxis=dict(showgrid=False, zeroline=False, linecolor="#E2E8F0"),
                yaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False, linecolor="#E2E8F0")
            )
            st.plotly_chart(fig_gender_age, use_container_width=True)

        with col2:
            st.markdown(f"#### 2. {selected_year}년 방한 외래객 속성별 점유율")
            target_col_label = st.radio("점유율 분석 기준", ["목적별", "교통수단별"], horizontal=True)
            
            df_share = df_filtered.groupby(target_col_label)["인원수"].sum().reset_index()
            df_share = df_share.nlargest(7, "인원수")
            fig_share = px.pie(
                df_share, names=target_col_label, values="인원수", hole=0.4,
                color_discrete_sequence=["#2563EB", "#0D9488", "#F97316", "#8B5CF6", "#64748B", "#38BDF8", "#FCD34D"]
            )
            fig_share.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Pretendard, sans-serif", size=14, color="#334155"),
                hoverlabel=dict(bgcolor="white", font_size=13, font_family="Pretendard"),
                margin=dict(l=20, r=20, t=20, b=20)
            )
            st.plotly_chart(fig_share, use_container_width=True)
            
        st.markdown("---")
        
        st.header("🗺️ 국적 집중화 현상")
        st.markdown("특정 국가에 편중된 의존도를 분석합니다.")
        
        if df_entry is not None and not df_entry.empty:
            st.subheader("방한 주요 국적별 입국자 총량")
            df_entry_top10 = df_entry.nlargest(10, '입국자 수(명)')
            fig4 = px.bar(df_entry_top10, x='입국자 수(명)', y='입국자 국적', orientation='h',
                          title="국적별 입국자 수 압도적 1위 중국 및 동아시아 강세",
                          color='입국자 수(명)', color_continuous_scale='Blues')
            fig4.update_layout(
                yaxis={'categoryorder': 'total ascending'},
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Pretendard, sans-serif", size=14, color="#334155"),
                hoverlabel=dict(bgcolor="white", font_size=13, font_family="Pretendard"),
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False, linecolor="#E2E8F0"),
                yaxis_title=None
            )
            st.plotly_chart(fig4, use_container_width=True)
        else:
            st.warning("입국자 국적 데이터를 확인할 수 없습니다.")
    else:
        st.warning("데이터를 불러올 수 없습니다.")
