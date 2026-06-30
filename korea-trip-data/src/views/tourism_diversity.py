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
    st.caption("🔹 **자료 출처:** 한국관광공사(한국관광 데이터랩), 공공데이터포털(ODCloud)")
    st.markdown("---")
    
    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')

    @st.cache_data
    def load_eda_data():
        df_consume_trend = pd.read_csv(os.path.join(data_dir, '20260620155141_업종별 관광소비 추이 CSV 다운로드.csv'))
        df_consume_country = pd.read_csv(os.path.join(data_dir, '20260620155314_국가별 관광소비 유형 CSV 다운로드.csv'))
        df_consume_trend['기준년월일'] = pd.to_datetime(df_consume_trend['기준년월일'].astype(str), format='%Y%m').dt.strftime('%Y-%m')
        return df_consume_trend, df_consume_country

    st.header("1. 🛍️ 업종별 및 국가별 관광 소비 트렌드")
    try:
        df_consume_trend, df_consume_country = load_eda_data()
        col1, col2 = st.columns(2)
        with col1:
            st.subheader("업종별 월간 관광 소비 추이")
            df_trend_pivot = df_consume_trend[df_consume_trend['업종별 구분'] != '전체']
            fig1 = px.line(df_trend_pivot, x='기준년월일', y='소비액(천원)', color='업종별 구분',
                           markers=True, title="월별 주요 관광 소비 업종 매출 동향",
                           color_discrete_sequence=["#00F0FF", "#38BDF8", "#2563EB", "#1E3A8A", "#64748B"])
            fig1.update_layout(
                xaxis_title="연월", yaxis_title="소비액(천원, Log Scale)", legend_title="업종",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Pretendard, sans-serif", size=14, color="#E2E8F0"),
                hoverlabel=dict(bgcolor="#1E293B", font_size=13, font_family="Pretendard", font=dict(color="#F8FAFC")),
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(showgrid=False, zeroline=False, linecolor="#334155", type="category"),
                yaxis=dict(showgrid=True, gridcolor="#1E293B", zeroline=False, linecolor="#334155", type="log")
            )
            st.plotly_chart(fig1, use_container_width=True)
            with st.expander("ℹ️ 데이터 산출 공식 및 출처 보기"):
                st.markdown("출처: 신한카드 및 BC카드 빅데이터. 지역별, 가구형태별, 업종별 외국인 관광객의 실제 카드 소비 결제 금액 및 건수를 바탕으로 산출된 인덱스입니다.")

        with col2:
            st.subheader("외국인 방문객 주요 소비국 비율")
            df_country_top10 = df_consume_country[df_consume_country['국가'] != '기타'].nlargest(10, '소비 비율')
            fig2 = px.treemap(df_country_top10, path=[px.Constant("전체"), '국가'], values='소비 비율',
                              title="한국 관광 소비 주도 상위 10개국 비율",
                              color='소비 비율',
                              color_continuous_scale="Teal")
            fig2.update_traces(textinfo='label+percent entry', textfont_size=14, marker=dict(line=dict(color='#121824', width=2)))
            fig2.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Pretendard, sans-serif", size=14, color="#E2E8F0"),
                hoverlabel=dict(bgcolor="#1E293B", font_size=13, font_family="Pretendard", font=dict(color="#F8FAFC")),
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig2, use_container_width=True)
            with st.expander("ℹ️ 데이터 산출 공식 및 출처 보기"):
                st.markdown("출처: 신한카드 및 BC카드 빅데이터. 지역별, 가구형태별, 업종별 외국인 관광객의 실제 카드 소비 결제 금액 및 건수를 바탕으로 산출된 인덱스입니다.")
    except Exception as e:
        st.warning(f"소비 트렌드 CSV 데이터를 불러올 수 없습니다: {e}")

    st.markdown("---")
    st.header("2. 💰 전국 관광 카드 소비 규모 현황 (API 2 연동)")
    df_kto_spend = get_area_spend_diversity("202601")

    if not df_kto_spend.empty:
        # 내국인 데이터 제외 (외국인 touDivCd == '3' 추출)
        if "touDivCd" in df_kto_spend.columns:
            df_kto_spend = df_kto_spend[df_kto_spend["touDivCd"] == "3"]

        # 서울, 부산, 제주 제외 필터링
        df_kto_spend = df_kto_spend[~df_kto_spend["signguNm"].str.contains("서울|부산|제주")]
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
                    color_discrete_sequence=["#00F0FF", "#38BDF8", "#2563EB", "#1E3A8A", "#64748B", "#94A3B8"]
                )
                fig_pie_spend.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#121824', width=2)))
                fig_pie_spend.update_layout(
                    showlegend=False,
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Pretendard, sans-serif", size=14, color="#E2E8F0"),
                    hoverlabel=dict(bgcolor="#1E293B", font_size=13, font_family="Pretendard", font=dict(color="#F8FAFC")),
                    margin=dict(l=20, r=20, t=20, b=20)
                )
                st.plotly_chart(fig_pie_spend, use_container_width=True)
                with st.expander("ℹ️ 데이터 산출 공식 및 출처 보기"):
                    st.markdown("출처: 신한카드 및 BC카드 빅데이터. 지역별, 가구형태별, 업종별 외국인 관광객의 실제 카드 소비 결제 금액 및 건수를 바탕으로 산출된 인덱스입니다.")
                
            with col_sp2:
                st.markdown("#### 전국 관광 총 소비 규모 Top 5")
                df_city_spend = df_kto_spend.groupby("signguNm")["cardUseAmt"].sum().reset_index()
                df_top_city_spend = df_city_spend.nlargest(5, "cardUseAmt")
                fig_city_spend = px.bar(
                    df_top_city_spend, x="cardUseAmt", y="signguNm",
                    orientation="h",
                    color="cardUseAmt",
                    color_continuous_scale="Teal"
                )
                fig_city_spend.update_layout(
                    yaxis=dict(categoryorder='total ascending'),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Pretendard, sans-serif", size=14, color="#E2E8F0"),
                    hoverlabel=dict(bgcolor="#1E293B", font_size=13, font_family="Pretendard", font=dict(color="#F8FAFC")),
                    margin=dict(l=20, r=20, t=20, b=20),
                    xaxis=dict(showgrid=True, gridcolor="#1E293B", zeroline=False, linecolor="#334155"),
                    yaxis_title=None
                )
                st.plotly_chart(fig_city_spend, use_container_width=True)
                with st.expander("ℹ️ 데이터 산출 공식 및 출처 보기"):
                    st.markdown("출처: 신한카드 및 BC카드 빅데이터. 지역별, 가구형태별, 업종별 외국인 관광객의 실제 카드 소비 결제 금액 및 건수를 바탕으로 산출된 인덱스입니다.")
    else:
        st.warning("관광 소비 다양성 데이터를 불러올 수 없습니다.")
