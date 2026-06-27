"""
인기 관광 지역 수요 분석 뷰 모듈입니다.
주요 기능:
- 온라인 관심도 및 실제 방문도 시각화
- 상위 지역 추이 변화 및 성수기 집중도 히트맵
- 여행 플랫폼 연동 Placeholder
"""
import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.kto_api import get_area_service_demand

def render_demand_analysis():
    st.title("🗺️ 인기 관광 지역 분석")
    st.markdown("전국 주요 관광지의 온라인 관심도(SNS), 실제 방문도(내비) 및 성수기 집중도를 확인합니다.")
    st.markdown("---")

    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')

    @st.cache_data
    def load_eda_data():
        df_visitor_region = pd.read_csv(os.path.join(data_dir, '20260620154323_외국인 지역별 방문자 수 추이.csv'))
        df_visitor_region['날짜'] = df_visitor_region['날짜'].astype(str)
        return df_visitor_region

    st.header("1. 🚗 관심도 및 실제 방문도 (API 3 연동)")
    df_kto_demand = get_area_service_demand("202601")

    if not df_kto_demand.empty:
        with st.container():
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.markdown("#### 🔥 온라인 관심도 (SNS)")
                df_top_sns = df_kto_demand.nlargest(5, "snsMentionCo")
                fig_sns = px.bar(
                    df_top_sns, x="snsMentionCo", y="signguNm",
                    orientation="h",
                    color="snsMentionCo",
                    color_continuous_scale="Blues"
                )
                fig_sns.update_layout(
                    yaxis=dict(categoryorder='total ascending'),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Pretendard, sans-serif", size=14, color="#334155"),
                    hoverlabel=dict(bgcolor="white", font_size=13, font_family="Pretendard"),
                    margin=dict(l=20, r=20, t=20, b=20),
                    xaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False, linecolor="#E2E8F0"),
                    yaxis_title=None
                )
                st.plotly_chart(fig_sns, use_container_width=True)
                
            with col_chart2:
                st.markdown("#### 실제 방문도 (내비)")
                df_top_navi = df_kto_demand.nlargest(5, "naviSearchCo")
                fig_navi = px.bar(
                    df_top_navi, x="naviSearchCo", y="signguNm",
                    orientation="h",
                    color="naviSearchCo",
                    color_continuous_scale="Teal"
                )
                fig_navi.update_layout(
                    yaxis=dict(categoryorder='total ascending'),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Pretendard, sans-serif", size=14, color="#334155"),
                    hoverlabel=dict(bgcolor="white", font_size=13, font_family="Pretendard"),
                    margin=dict(l=20, r=20, t=20, b=20),
                    xaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False, linecolor="#E2E8F0"),
                    yaxis_title=None
                )
                st.plotly_chart(fig_navi, use_container_width=True)
    else:
        st.warning("관광 서비스 수요 데이터를 불러올 수 없습니다.")

    st.markdown("---")
    st.header("2. 📍 방한 방문객 지역 집중화 추이")
    try:
        df_visitor_region = load_eda_data()
        col3, col4 = st.columns(2)

        with col3:
            st.subheader("방문객 상위 5개 지역 추이 변화")
            df_region_sum = df_visitor_region.groupby('지역')['외국인 방문자수'].sum().reset_index()
            top5_regions = df_region_sum.nlargest(5, '외국인 방문자수')['지역']
            df_top5 = df_visitor_region[df_visitor_region['지역'].isin(top5_regions)]
            fig3 = px.line(df_top5, x='날짜', y='외국인 방문자수', color='지역', markers=True,
                           title="주요 관광 거점(상위 5개 지역) 쏠림 및 성장 추이",
                           color_discrete_sequence=["#2563EB", "#0D9488", "#F97316", "#8B5CF6", "#64748B"])
            fig3.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Pretendard, sans-serif", size=14, color="#334155"),
                hoverlabel=dict(bgcolor="white", font_size=13, font_family="Pretendard"),
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(showgrid=False, zeroline=False, linecolor="#E2E8F0"),
                yaxis=dict(showgrid=True, gridcolor="#F1F5F9", zeroline=False, linecolor="#E2E8F0")
            )
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            st.subheader("지역별 성수기(봄철) 수요 집중도")
            df_heatmap = df_visitor_region.pivot(index='지역', columns='날짜', values='외국인 방문자수')
            fig5 = go.Figure(data=go.Heatmap(
                z=df_heatmap.values,
                x=df_heatmap.columns,
                y=df_heatmap.index,
                colorscale='Oranges',
                xgap=2, ygap=2
            ))
            fig5.update_layout(
                title="전국 지자체별/월별 방한 외국인 규모 히트맵",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Pretendard, sans-serif", size=14, color="#334155"),
                hoverlabel=dict(bgcolor="white", font_size=13, font_family="Pretendard"),
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig5, use_container_width=True)
    except Exception as e:
        st.warning(f"지역별 방문자 수 데이터를 확인할 수 없습니다: {e}")
        
    st.markdown("---")
    st.header("3. 🌍 주요 여행 플랫폼 데이터 연동 (개발 예정)")
    st.info("데이터 파이프라인 취합 후 GetYourGuide, Klook, KKday 등의 플랫폼 인기 관광 상품 및 지역 데이터가 이곳에 표시될 예정입니다.")
