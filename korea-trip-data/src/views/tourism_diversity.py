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

        with col2:
            st.subheader("외국인 방문객 주요 소비국 비율")
            df_country_top10 = df_consume_country[df_consume_country['국가'] != '기타'].nlargest(10, '소비 비율')
            fig2 = px.treemap(df_country_top10, path=[px.Constant("전체"), '국가'], values='소비 비율',
                              title="한국 관광 소비 주도 상위 10개국 비율",
                              color='소비 비율',
                              color_continuous_scale="Blues")
            fig2.update_traces(textinfo='label+percent entry', textfont_size=14, marker=dict(line=dict(color='#121824', width=2)))
            fig2.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Pretendard, sans-serif", size=14, color="#E2E8F0"),
                hoverlabel=dict(bgcolor="#1E293B", font_size=13, font_family="Pretendard", font=dict(color="#F8FAFC")),
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig2, use_container_width=True)
    except Exception as e:
        st.warning(f"소비 트렌드 CSV 데이터를 불러올 수 없습니다: {e}")

    st.markdown("---")
    st.header("2. 💰 전국 관광 카드 소비 규모 현황")
    @st.cache_data
    def load_spend_data():
        try:
            df_easy = pd.read_csv(os.path.join(data_dir, '20260702202154_관광객 간편결제 업종별 관광소비 추이.csv'), encoding='utf-8')
        except:
            df_easy = pd.read_csv(os.path.join(data_dir, '20260702202154_관광객 간편결제 업종별 관광소비 추이.csv'), encoding='cp949')
        
        try:
            df_spend = pd.read_csv(os.path.join(data_dir, '20260702202516_관광지출액.csv'), encoding='utf-8')
        except:
            df_spend = pd.read_csv(os.path.join(data_dir, '20260702202516_관광지출액.csv'), encoding='cp949')
            
        try:
            df_region = pd.read_csv(os.path.join(data_dir, '20260702202616_지역 방문자수_관광지출액 추세.csv'), encoding='utf-8')
        except:
            df_region = pd.read_csv(os.path.join(data_dir, '20260702202616_지역 방문자수_관광지출액 추세.csv'), encoding='cp949')
            
        return df_easy, df_spend, df_region

    try:
        df_easy, df_spend, df_region = load_spend_data()
        
        # 1. 전국 관광 소비 비중 (간편결제 업종별)
        df_easy_filtered = df_easy[df_easy['업종'] != '전체']
        df_ind_spend = df_easy_filtered.groupby('업종')['소비금액(천원)'].sum().reset_index()
        
        # 2. 전국 관광 총 소비 규모 Top 5 (서울, 부산, 제주 제외)
        excludes = ['서울', '부산', '제주']
        df_spend_filtered = df_spend[~df_spend['시도명'].str.contains('|'.join(excludes))]
        df_top_city_spend = df_spend_filtered.sort_values('관광지출액', ascending=False).head(5)
        
        with st.container():
            col_sp1, col_sp2 = st.columns([1, 2])
            
            with col_sp1:
                st.markdown("#### 업종별 관광 소비 비중 (간편결제 기준)")
                fig_pie_spend = px.pie(
                    df_ind_spend, values="소비금액(천원)", names="업종",
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
                
            with col_sp2:
                st.markdown("#### 핵심 거점 관광지출액 Top 5")
                fig_city_spend = px.bar(
                    df_top_city_spend, x="관광지출액", y="시도명",
                    orientation="h",
                    color="관광지출액",
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
                
        # 3. 신규 추가 그래프: 방문자수 대비 관광지출액 산점도
        st.markdown("---")
        st.header("3. 방문자수와 관광지출액의 상관관계")
        
        corr_coef = df_region["방문자수"].corr(df_region["관광지출액"])
        
        fig_scatter = px.scatter(
            df_region, x="방문자수", y="관광지출액",
            color="관광지출액", size="방문자수",
            trendline="ols", trendline_color_override="#00F0FF",
            color_continuous_scale="Teal",
            labels={"방문자수": "방문자 수(명)", "관광지출액": "관광지출액(단위: 천원)"}
        )
        
        fig_scatter.add_annotation(
            x=1.0, y=1.05, xref="paper", yref="paper",
            text=f"상관계수: {corr_coef:.2f}",
            showarrow=False,
            font=dict(size=13, color="#38BDF8", family="Pretendard, sans-serif"),
            align="right"
        )
        
        fig_scatter.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Pretendard, sans-serif", size=14, color="#E2E8F0"),
            hoverlabel=dict(bgcolor="#1E293B", font_size=13, font_family="Pretendard", font=dict(color="#F8FAFC")),
            margin=dict(l=20, r=20, t=40, b=20),
            xaxis=dict(tickformat=",.0f", showgrid=True, gridcolor="#1E293B", zeroline=False, linecolor="#334155"),
            yaxis=dict(tickformat=",.0f", showgrid=True, gridcolor="#1E293B", zeroline=False, linecolor="#334155"),
            coloraxis_colorbar=dict(tickformat=",.0f")
        )
        st.plotly_chart(fig_scatter, use_container_width=True)
                
    except Exception as e:
        st.warning(f"관광 소비 데이터를 불러올 수 없습니다: {e}")
