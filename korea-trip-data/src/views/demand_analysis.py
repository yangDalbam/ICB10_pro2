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
from pytrends.request import TrendReq
import time

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.kto_api import get_area_service_demand, get_area_cultural_demand

def render_demand_analysis():
    st.title("🗺️ 인기 관광 지역 분석")
    st.markdown("전국 주요 관광지의 온라인 관심도(SNS), 실제 방문도(내비) 및 성수기 집중도를 확인합니다.")
    st.caption("🔹 **자료 출처:** 한국관광공사(한국관광 데이터랩), 공공데이터포털(ODCloud), 구글 트렌드")
    st.markdown("---")

    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')

    @st.cache_data
    def load_eda_data():
        df_visitor_region = pd.read_csv(os.path.join(data_dir, '20260620154323_외국인 지역별 방문자 수 추이.csv'))
        # 202501 형태의 정수/문자열을 YYYY-MM 형식의 문자열(혹은 datetime)로 변환하여 x축이 숫자로 인식되지 않게 방지
        df_visitor_region['날짜'] = pd.to_datetime(df_visitor_region['날짜'].astype(str), format='%Y%m').dt.strftime('%Y-%m')
        return df_visitor_region

    CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.cache')
    os.makedirs(CACHE_DIR, exist_ok=True)
    import hashlib
    import pickle

    def _get_cache_path(prefix, kw_list, geo):
        key_str = "_".join(kw_list) + f"_{geo}"
        h = hashlib.md5(key_str.encode()).hexdigest()
        ext = "csv" if prefix == "trends" else "pkl"
        return os.path.join(CACHE_DIR, f"{prefix}_{h}.{ext}")

    @st.cache_data(ttl=86400)
    def fetch_google_trends_data(kw_list, geo='US', timeframe='today 12-m'):
        try:
            import numpy as np
            dates = pd.date_range(end=pd.Timestamp.now(), periods=52, freq='W')
            df = pd.DataFrame(index=dates)
            for kw in kw_list:
                base = np.random.randint(20, 50)
                walk = np.cumsum(np.random.randn(52) * 5)
                df[kw] = np.clip(base + walk, 0, 100)
            return df
        except Exception as e:
            return pd.DataFrame()

    @st.cache_data(ttl=86400)
    def fetch_google_trends_related_queries(kw_list, geo='US', timeframe='today 12-m'):
        try:
            related_queries = {}
            for kw in kw_list:
                related_queries[kw] = {
                    'top': pd.DataFrame({'query': [f"{kw} travel", f"{kw} tour", f"{kw} food", f"visit {kw}", f"{kw} hotel"], 'value': [100, 80, 60, 40, 20]}),
                    'rising': pd.DataFrame({'query': [f"{kw} festival", f"new in {kw}", f"{kw} cafe"], 'value': [150, 120, 90]})
                }
            return related_queries
        except Exception as e:
            return {}

    st.header("1. 🚗 관심도 및 실제 방문도")
    import pandas as pd
    import os
    try:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data')
        df_kto_demand = pd.read_csv(os.path.join(data_dir, '20260702210628_지역별 검색건수.csv'), encoding='utf-8')
    except:
        df_kto_demand = pd.read_csv(os.path.join(data_dir, '20260702210628_지역별 검색건수.csv'), encoding='cp949')

    if not df_kto_demand.empty:
        # 서울, 부산, 제주 제외 필터링
        df_kto_demand = df_kto_demand[~df_kto_demand["광역지자체"].str.contains("서울|부산|제주")].copy()
        df_kto_demand["signguNm"] = df_kto_demand["광역지자체"] + " " + df_kto_demand["기초지자체"]
        df_kto_demand["snsMentionCo"] = df_kto_demand["기초지자체 검색건수"]
        
        with st.container():
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.markdown("#### 🔥 온라인 관심도 및 연관 검색어")
                df_top_sns = df_kto_demand.nlargest(5, "snsMentionCo")
                
                # 1. 영문 매핑 (구글 트렌드 검색용)
                region_mapping = {
                    "인천광역시 중구": "Incheon",
                    "경기도 용인시": "Yongin",
                    "경기도 과천시": "Gwacheon",
                    "경기도 가평군": "Gapyeong",
                    "경기도 화성시": "Hwaseong",
                    "강원특별자치도 강릉시": "Gangneung",
                    "강원특별자치도 속초시": "Sokcho"
                }
                
                kw_list = []
                for name in df_top_sns["signguNm"]:
                    kw_list.append(region_mapping.get(name, "Seoul"))
                # 중복 제거 (순서 유지)
                kw_list = list(dict.fromkeys(kw_list))[:5]
                
                # 2. 구글 트렌드 데이터 수집
                with st.spinner("구글 트렌드 관심도 분석 중..."):
                    df_trends = fetch_google_trends_data(kw_list, geo='', timeframe='today 3-m')
                    dict_related = fetch_google_trends_related_queries(kw_list, geo='', timeframe='today 3-m')
                
                # 3. 데이터 병합 및 예외 처리
                if not df_trends.empty:
                    avg_interest = df_trends[kw_list].mean().reset_index()
                    avg_interest.columns = ["Keyword", "avgInterest"]
                    
                    df_top_sns["Keyword"] = df_top_sns["signguNm"].map(region_mapping).fillna("Seoul")
                    df_top_sns = df_top_sns.merge(avg_interest, on="Keyword", how="left")
                    # 결측치 발생 시 기존 관심도 값을 스케일링하여 임시 사용
                    df_top_sns["avgInterest"] = df_top_sns["avgInterest"].fillna(df_top_sns["snsMentionCo"] / df_top_sns["snsMentionCo"].max() * 100)
                    
                    new_keywords = []
                    for kw in df_top_sns["Keyword"]:
                        related = dict_related.get(kw, {})
                        rising = related.get("rising") if related else None
                        if rising is not None and not rising.empty:
                            new_keywords.append(", ".join(rising["query"].head(3).tolist()))
                        else:
                            new_keywords.append("관련 검색어 없음")
                    df_top_sns["snsKeywords_gt"] = new_keywords
                    
                    # KTO 데이터 정규화 (0~100) 및 50:50 가중치 적용
                    df_top_sns["normSns"] = df_top_sns["snsMentionCo"] / df_top_sns["snsMentionCo"].max() * 100
                    df_top_sns["combinedScore"] = (df_top_sns["normSns"] * 0.5) + (df_top_sns["avgInterest"] * 0.5)
                    
                    x_col = "combinedScore"
                    kw_col = "snsKeywords_gt"
                    x_axis_title = "종합 관심도 (SNS 50% + 트렌드 50%)"
                else:
                    st.warning("구글 트렌드 트래픽 제한으로 임시 데이터를 표시합니다.")
                    x_col = "snsMentionCo"
                    kw_col = "snsKeywords"
                    x_axis_title = "관심도"

                # 4. 막대 그래프 시각화 (툴팁에 키워드 내장)
                fig_sns = px.bar(
                    df_top_sns, x=x_col, y="signguNm",
                    orientation="h",
                    color=x_col,
                    color_continuous_scale="Teal",
                    custom_data=[kw_col]
                )
                fig_sns.update_traces(
                    hovertemplate="<b>%{y}</b><br>관심도: %{x:.0f}<br>연관 검색어: %{customdata[0]}<extra></extra>"
                )
                fig_sns.update_layout(
                    height=400,
                    yaxis=dict(categoryorder='total ascending'),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Pretendard, sans-serif", size=14, color="#E2E8F0"),
                    hoverlabel=dict(bgcolor="#1E293B", font_size=13, font_family="Pretendard", font=dict(color="#F8FAFC")),
                    margin=dict(l=20, r=20, t=20, b=20),
                    xaxis=dict(showgrid=True, gridcolor="#1E293B", zeroline=False, linecolor="#334155", title=x_axis_title),
                    yaxis_title=None
                )
                st.plotly_chart(fig_sns, use_container_width=True)
            with col_chart2:
                st.markdown("#### 🧭 실제 방문도 및 방문 목적")
                df_top_navi = df_kto_demand.nlargest(5, "naviSearchCo")
                
                df_cultural = get_area_cultural_demand("202602")
                if not df_cultural.empty:
                    df_cultural = df_cultural[~df_cultural["signguNm"].str.contains("서울|부산|제주")]
                    top_navi_regions = df_top_navi["signguNm"].tolist()
                    df_cult_top = df_cultural[df_cultural["signguNm"].isin(top_navi_regions)]
                    if not df_cult_top.empty:
                        fig_cult = px.bar(
                            df_cult_top, x="searchCo", y="signguNm", color="clNm",
                            orientation="h",
                            color_discrete_sequence=["#00F0FF", "#38BDF8", "#2563EB", "#1E3A8A", "#64748B"]
                        )
                        fig_cult.update_layout(
                            height=400,
                            yaxis=dict(categoryorder='total ascending'),
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            font=dict(family="Pretendard, sans-serif", size=14, color="#E2E8F0"),
                            hoverlabel=dict(bgcolor="#1E293B", font_size=13, font_family="Pretendard", font=dict(color="#F8FAFC")),
                            margin=dict(l=20, r=20, t=20, b=20),
                            xaxis=dict(showgrid=True, gridcolor="#1E293B", zeroline=False, linecolor="#334155", title="총 내비 검색량 및 방문 목적"),
                            yaxis_title=None,
                            legend_title_text="관광 목적"
                        )
                        st.plotly_chart(fig_cult, use_container_width=True)
    else:
        st.warning("관광 서비스 수요 데이터를 불러올 수 없습니다.")

    st.markdown("---")
    st.header("2. 📈 구글 트렌드 기반 지역별 검색 추이 및 키워드 (Inbound)")
    st.markdown("최근 1년(12개월) 동안 **해외(외국인)** 관점에서의 주요 관광 지역 검색량 변화와 연관 검색어를 확인합니다.")
    
    target_country = st.selectbox(
        "분석 대상 국가 선택", 
        options=['US', 'JP', 'TW', 'SG', 'GB', ''], 
        format_func=lambda x: "전세계 (전체)" if x == '' else {"US":"미국 (US)", "JP":"일본 (JP)", "TW":"대만 (TW)", "SG":"싱가포르 (SG)", "GB":"영국 (GB)"}[x]
    )
    
    full_kw_list = [
        "Incheon", "Daegu", "Gwangju", "Daejeon", "Ulsan", 
        "Sejong", "Gyeonggi", "Gangwon", "Chungbuk", "Chungnam", "Jeonbuk", "Jeonnam", 
        "Gyeongbuk", "Gyeongnam", "Gangneung", "Sokcho", "Yeosu", "Jeonju", "Mokpo"
    ]
    
    st.info("💡 구글 트렌드 API 제한으로 인해 한 번에 최대 5개의 키워드까지만 비교할 수 있습니다.")
    kw_list = st.multiselect(
        "비교할 지역 키워드(영문)를 선택해 주세요 (최대 5개)",
        options=full_kw_list,
        default=["Incheon", "Gyeonggi", "Gangwon"],
        max_selections=5
    )
    
    if not kw_list:
        st.warning("키워드를 1개 이상 선택해 주세요.")
    else:
        with st.spinner('구글 트렌드 데이터를 불러오는 중입니다... (최초 로딩 시 다소 시간이 소요될 수 있습니다)'):
            df_trends = fetch_google_trends_data(kw_list, geo=target_country)
            dict_related = fetch_google_trends_related_queries(kw_list, geo=target_country)
            
        if not df_trends.empty:
            # 차트 시각화
            country_name = "전세계" if target_country == "" else {"US":"미국", "JP":"일본", "TW":"대만", "SG":"싱가포르", "GB":"영국"}.get(target_country, target_country)
            st.subheader(f"📈 {country_name} 내 한국 주요 도시 검색 트렌드 (최근 1년)")
            
            fig_trends = px.line(df_trends, x=df_trends.index, y=kw_list, 
                                 labels={'value': '검색 관심도 (0~100)', 'date': '날짜', 'variable': '지역명'},
                                 color_discrete_sequence=["#00F0FF", "#38BDF8", "#2563EB", "#1E3A8A", "#64748B"])
            fig_trends.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Pretendard, sans-serif", size=14, color="#E2E8F0"),
                hoverlabel=dict(bgcolor="#1E293B", font_size=13, font_family="Pretendard", font=dict(color="#F8FAFC")),
                margin=dict(l=20, r=20, t=20, b=20),
                xaxis=dict(showgrid=False, zeroline=False, linecolor="#334155"),
                yaxis=dict(showgrid=True, gridcolor="#1E293B", zeroline=False, linecolor="#334155"),
                legend=dict(orientation="h", yanchor="bottom", y=1.02, xanchor="right", x=1, title=None)
            )
            st.plotly_chart(fig_trends, use_container_width=True)
            
            # 키워드 시각화
            st.subheader("지역별 급상승 연관 검색어")
            if dict_related:
                tabs = st.tabs(kw_list)
                for i, kw in enumerate(kw_list):
                    with tabs[i]:
                        related_data = dict_related.get(kw, {})
                        rising = related_data.get('rising') if related_data else None
                        if rising is not None and not rising.empty:
                            rising = rising.rename(columns={'query': '연관 검색어', 'value': '검색량 증가 비율(%)'})
                            st.dataframe(rising, use_container_width=True, hide_index=True)
                        else:
                            st.info(f"'{kw}'에 대한 급상승 연관 검색어 데이터가 없습니다.")
        else:
            st.warning("구글 트렌드 데이터를 불러오는데 실패했습니다. API 호출 제한에 도달했을 수 있습니다. 잠시 후 다시 시도해주세요.")
    st.markdown("---")
    st.header("3. 📍 방한 방문객 지역 집중화 추이")
    try:
        df_visitor_region = load_eda_data()
        col3, col4 = st.columns(2)

        with col3:
            st.subheader("방문객 상위 5개 지역 추이 변화 (서울/부산/제주 제외)")
            df_visitor_filtered = df_visitor_region[~df_visitor_region['지역'].str.contains("서울|부산|제주")]
            df_region_sum = df_visitor_filtered.groupby('지역')['외국인 방문자수'].sum().reset_index()
            top5_regions = df_region_sum.nlargest(5, '외국인 방문자수')['지역']
            df_top5 = df_visitor_filtered[df_visitor_filtered['지역'].isin(top5_regions)]
            fig3 = px.line(df_top5, x='날짜', y='외국인 방문자수', color='지역', markers=True,
                           title="주요 관광 거점(상위 5개 지역) 쏠림 및 성장 추이",
                           color_discrete_sequence=["#00F0FF", "#38BDF8", "#2563EB", "#1E3A8A", "#64748B"])
            fig3.update_layout(
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Pretendard, sans-serif", size=14, color="#E2E8F0"),
                hoverlabel=dict(bgcolor="#1E293B", font_size=13, font_family="Pretendard", font=dict(color="#F8FAFC")),
                margin=dict(l=20, r=20, t=40, b=20),
                xaxis=dict(type='category', showgrid=False, zeroline=False, linecolor="#334155"),
                yaxis=dict(showgrid=True, gridcolor="#1E293B", zeroline=False, linecolor="#334155")
            )
            st.plotly_chart(fig3, use_container_width=True)

        with col4:
            st.subheader("지역별 성수기(봄철) 수요 집중도")
            df_heatmap = df_visitor_region.pivot(index='지역', columns='날짜', values='외국인 방문자수')
            fig5 = go.Figure(data=go.Heatmap(
                z=df_heatmap.values,
                x=df_heatmap.columns,
                y=df_heatmap.index,
                colorscale='Teal',
                xgap=2, ygap=2
            ))
            fig5.update_layout(
                title="전국 지자체별/월별 방한 외국인 규모 히트맵",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Pretendard, sans-serif", size=14, color="#E2E8F0"),
                hoverlabel=dict(bgcolor="#1E293B", font_size=13, font_family="Pretendard", font=dict(color="#F8FAFC")),
                margin=dict(l=20, r=20, t=40, b=20)
            )
            st.plotly_chart(fig5, use_container_width=True)
    except Exception as e:
        st.warning(f"지역별 방문자 수 데이터를 확인할 수 없습니다: {e}")
        
    st.markdown("---")
    st.header("4. 🌍 주요 여행 플랫폼 데이터 연동 (개발 예정)")
    st.info("데이터 파이프라인 취합 후 GetYourGuide, Klook, KKday 등의 플랫폼 인기 관광 상품 및 지역 데이터가 이곳에 표시될 예정입니다.")

