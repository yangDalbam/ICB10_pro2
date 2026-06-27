"""
관광 소비 현황 분석 뷰 모듈입니다.
주요 기능:
- 카드 소비 다양성 및 업종별 비중 분석
- 관광 소비 추이 및 소비 주요국 비율 시각화
"""
import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.kto_api import get_area_spend_diversity

def render_tourism_diversity():
    st.title("💳 관광 소비 현황 분석")
    st.markdown("업종별 월간 관광 소비 트렌드 및 전국 주요 관광지 소비 비중을 확인합니다.")
    st.markdown("---")
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')

    @st.cache_data
    def load_eda_data():
        df_consume_trend = pd.read_csv(os.path.join(data_dir, '20260620155141_업종별 관광소비 추이 CSV 다운로드.csv'))
        df_consume_country = pd.read_csv(os.path.join(data_dir, '20260620155314_국가별 관광소비 유형 CSV 다운로드.csv'))
        df_consume_trend['기준년월일'] = df_consume_trend['기준년월일'].astype(str)
        return df_consume_trend, df_consume_country

    st.header("1. 🛍️ 업종별 및 국가별 관광 소비 트렌드")
    try:
        df_consume_trend, df_consume_country = load_eda_data()
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
    except Exception as e:
        st.warning(f"소비 트렌드 CSV 데이터를 불러올 수 없습니다: {e}")

    st.markdown("---")
    st.header("2. 💰 전국 관광 카드 소비 규모 현황 (API 2 연동)")
    df_kto_spend = get_area_spend_diversity("202601")

    if not df_kto_spend.empty:
        df_ind_spend = df_kto_spend.groupby("indutyNm")["cardUseAmt"].sum().reset_index()
        total_amt = df_ind_spend["cardUseAmt"].sum()
        df_ind_spend["비율"] = (df_ind_spend["cardUseAmt"] / total_amt) * 100
        
        with st.container():
            col_sp1, col_sp2 = st.columns([1, 2])
            
            with col_sp1:
                st.markdown("#### 전국 관광 소비 비중")
                fig_pie_spend = px.pie(
                    df_ind_spend, values="cardUseAmt", names="indutyNm",
                    hole=0.4,
                    color_discrete_sequence=["#2563EB", "#0EA5E9", "#10B981", "#F59E0B", "#8B5CF6", "#64748B"]
                )
                fig_pie_spend.update_traces(textposition='inside', textinfo='percent+label')
                fig_pie_spend.update_layout(showlegend=False)
                st.plotly_chart(fig_pie_spend, use_container_width=True)
                
            with col_sp2:
                st.markdown("#### 전국 관광 총 소비 규모 Top 5")
                df_city_spend = df_kto_spend.groupby("signguNm")["cardUseAmt"].sum().reset_index()
                df_top_city_spend = df_city_spend.nlargest(5, "cardUseAmt")
                fig_city_spend = px.bar(
                    df_top_city_spend, x="cardUseAmt", y="signguNm",
                    orientation="h",
                    color="cardUseAmt",
                    color_continuous_scale=["#93C5FD", "#3B82F6", "#2563EB"]
                )
                fig_city_spend.update_layout(yaxis=dict(categoryorder='total ascending'))
                st.plotly_chart(fig_city_spend, use_container_width=True)
    else:
        st.warning("관광 소비 다양성 데이터를 불러올 수 없습니다.")
