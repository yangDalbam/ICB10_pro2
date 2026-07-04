"""
관광 인사이트 및 벤치마킹 제언 모듈입니다.
주요 기능:
- 시군구별 온-오프라인 매트릭스 2x2 분포 확인 및 대상 선정
- 선정된 대상의 1:1 심층 비교 및 활성화 제언 분석
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
from api.kto_api import (
    get_area_service_demand, get_area_visitor_diversity,
    get_area_spend_diversity, get_area_intl_diversity, get_area_cultural_demand
)

def render_eda_insights():
    st.title("💡 관광 인사이트 및 지역 활성화 제언")
    st.markdown("전국 관광지의 특성을 매트릭스 형태로 진단하고 벤치마킹을 위한 심층 비교를 진행합니다.")
    st.caption("🔹 **자료 출처:** 한국관광공사(한국관광 데이터랩), 공공데이터포털(ODCloud)")
    st.markdown("---")

    # 세션 상태 설정
    if "city_1" not in st.session_state:
        st.session_state.city_1 = "용인시"
    if "city_2" not in st.session_state:
        st.session_state.city_2 = "강릉시"

    try:
        data_dir = os.path.join(os.path.dirname(os.path.abspath(__file__)), '..', '..', 'data')
        df_demand = pd.read_csv(os.path.join(data_dir, '20260702210628_지역별 검색건수.csv'), encoding='utf-8')
    except:
        df_demand = pd.read_csv(os.path.join(data_dir, '20260702210628_지역별 검색건수.csv'), encoding='cp949')

    if not df_demand.empty:
        # 서울, 부산, 제주 제외 필터링
        df_demand = df_demand[~df_demand["광역지자체"].str.contains("서울|부산|제주")].copy()
        def format_region(row):
            sido = row["광역지자체"]
            sigungu = row["기초지자체"]
            if sigungu.endswith('시'):
                return sigungu
            else:
                return f"{sido[:2]} {sigungu}"
        df_demand["signguNm"] = df_demand.apply(format_region, axis=1)
        
        df_demand["snsMentionCo"] = df_demand["기초지자체 검색건수"]
        df_demand["naviSearchCo"] = df_demand["기초지자체 검색건수"]
        
        # 사용자의 요청에 따라 가독성을 위해 상위 15개 지역만 추출
        df_demand = df_demand.nlargest(15, "snsMentionCo")

    if not df_demand.empty:
        st.header("1. 🧩 시군구별 온-오프라인 매트릭스 2x2 진단")

        CACHE_DIR = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), '.cache')
        os.makedirs(CACHE_DIR, exist_ok=True)
        import hashlib

        @st.cache_data(ttl=86400)
        def fetch_google_trends_data_all(kw_list):
            try:
                from pytrends.request import TrendReq
                import time
                import pandas as pd
                pytrends = TrendReq(hl='en-US', tz=360, retries=3, backoff_factor=1)
                
                all_dfs = []
                # 구글 트렌드는 한 번에 최대 5개의 키워드만 허용하므로 5개 단위로 분할(청크) 처리
                for i in range(0, len(kw_list), 5):
                    chunk = kw_list[i:i+5]
                    pytrends.build_payload(chunk, cat=0, timeframe='today 3-m', geo='')
                    df = pytrends.interest_over_time()
                    if not df.empty and 'isPartial' in df.columns:
                        df = df.drop(columns=['isPartial'])
                    all_dfs.append(df)
                    time.sleep(1.5) # rate limit mitigation
                
                if all_dfs:
                    # 열 기준으로 병합 (동일한 날짜 인덱스를 공유)
                    merged_df = pd.concat(all_dfs, axis=1)
                    # 혹시 모를 중복 컬럼 제거
                    return merged_df.loc[:, ~merged_df.columns.duplicated()]
                return pd.DataFrame()
            except Exception as e:
                import streamlit as st
                st.toast(f"구글 트렌드 API 오류: {str(e)}")
                return pd.DataFrame()

        region_mapping = {
            "인천 중구": "Incheon",
            "용인시": "Yongin",
            "과천시": "Gwacheon",
            "경기 가평군": "Gapyeong",
            "화성시": "Hwaseong",
            "강릉시": "Gangneung",
            "속초시": "Sokcho"
        }

        # 구글 트렌드 연동을 위한 키워드 매핑
        df_demand["Keyword"] = df_demand["signguNm"].map(region_mapping).fillna("Seoul")
        unique_kws = list(df_demand["Keyword"].unique())

        with st.spinner("구글 트렌드 관심도 분석 중..."):
            df_trends = fetch_google_trends_data_all(unique_kws)

        if not df_trends.empty:
            df_trends = df_trends.loc[:, ~df_trends.columns.duplicated()]
            avg_interest = df_trends[unique_kws].mean().reset_index()
            avg_interest.columns = ["Keyword", "avgInterest"]
            
            df_demand = df_demand.merge(avg_interest, on="Keyword", how="left")
            df_demand["avgInterest"] = df_demand["avgInterest"].fillna(df_demand["snsMentionCo"] / df_demand["snsMentionCo"].max() * 100)
            
            df_demand["normSns"] = df_demand["snsMentionCo"] / df_demand["snsMentionCo"].max() * 100
            df_demand["combinedScore"] = (df_demand["normSns"] * 0.5) + (df_demand["avgInterest"] * 0.5)
            x_col = "combinedScore"
            x_axis_title = "종합 관심도 (SNS 50% + 트렌드 50%)"
        else:
            st.warning("구글 트렌드 트래픽 제한으로 임시 데이터를 표시합니다.")
            df_demand["combinedScore"] = df_demand["snsMentionCo"]
            x_col = "combinedScore"
            x_axis_title = "SNS 언급량(관심도)"

        median_sns = df_demand[x_col].median()
        median_navi = df_demand["naviSearchCo"].median()

        def get_quadrant(row):
            if row[x_col] >= median_sns and row["naviSearchCo"] >= median_navi:
                return "스타 (고관심·고방문)"
            elif row[x_col] >= median_sns and row["naviSearchCo"] < median_navi:
                return "잠재 (고관심·저방문)"
            elif row[x_col] < median_sns and row["naviSearchCo"] >= median_navi:
                return "안정 (저관심·고방문)"
            else:
                return "일반 (저관심·저방문)"

        df_demand["cityType"] = df_demand.apply(get_quadrant, axis=1)

        fig = px.scatter(
            df_demand, x=x_col, y="naviSearchCo",
            color="cityType", hover_name="signguNm", text="signguNm",
            color_discrete_map={
                "스타 (고관심·고방문)": "#00F0FF", # 밝은 시안
                "잠재 (고관심·저방문)": "#A78BFA", # 연보라
                "안정 (저관심·고방문)": "#38BDF8", # 스카이블루
                "일반 (저관심·저방문)": "#94A3B8"  # 슬레이트(회색)
            }
        )
        
        # 텍스트 겹침 방지를 위해 사분면별로 텍스트 방향을 밀어내고, 지터링(배열 순환) 적용
        for trace in fig.data:
            trace_len = len(trace.x) if trace.x is not None else 0
            if "스타" in trace.name:
                pos_array = ['top right', 'top center', 'middle right'] * (trace_len // 3 + 1)
            elif "잠재" in trace.name:
                pos_array = ['bottom right', 'bottom center', 'middle right'] * (trace_len // 3 + 1)
            elif "안정" in trace.name:
                pos_array = ['top left', 'top center', 'middle left'] * (trace_len // 3 + 1)
            else:
                pos_array = ['bottom left', 'bottom center', 'middle left'] * (trace_len // 3 + 1)
            
            trace.textposition = pos_array[:trace_len]
            trace.textfont = dict(size=12, color="#F8FAFC")
            trace.marker = dict(size=14, opacity=0.85, line=dict(width=1, color='#121824'))
        fig.add_vline(x=median_sns, line_width=1.5, line_dash="dash", line_color="#475569")
        fig.add_hline(y=median_navi, line_width=1.5, line_dash="dash", line_color="#475569")
        fig.update_layout(
            xaxis_title=x_axis_title, yaxis_title="내비게이션 검색(방문도)",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Pretendard, sans-serif", size=14, color="#E2E8F0"),
            hoverlabel=dict(bgcolor="#1E293B", font_size=13, font_family="Pretendard", font=dict(color="#F8FAFC")),
            margin=dict(l=20, r=20, t=20, b=20),
            xaxis=dict(showgrid=True, gridcolor="#1E293B", zeroline=False, linecolor="#334155"),
            yaxis=dict(showgrid=True, gridcolor="#1E293B", zeroline=False, linecolor="#334155")
        )
        st.plotly_chart(fig, use_container_width=True)

        st.markdown("#### 벤치마킹 대상 도시 선택")
        
        # 도시와 카테고리 매핑 딕셔너리 생성
        city_to_quadrant = dict(zip(df_demand["signguNm"], df_demand["cityType"]))
        
        def format_city(city):
            quadrant = city_to_quadrant.get(city, "")
            short_quadrant = quadrant.split(" ")[0] if quadrant else ""
            return f"[{short_quadrant}] {city}"

        # 스타/안정 등 상위 카테고리 순으로 정렬하기 위해, 카테고리 우선순위 부여
        quadrant_order = {"스타": 1, "잠재": 2, "안정": 3, "일반": 4}
        city_list = sorted(df_demand["signguNm"].unique().tolist(), 
                           key=lambda x: (quadrant_order.get(city_to_quadrant.get(x, "").split(" ")[0], 99), x))
        
        col_select1, col_select2 = st.columns(2)

        with col_select1:
            default_idx1 = city_list.index(st.session_state.city_1) if st.session_state.city_1 in city_list else 0
            st.session_state.city_1 = st.selectbox(
                "📍 벤치마킹 기준 (성공 도시)", 
                city_list, 
                index=default_idx1,
                format_func=format_city
            )
            
        with col_select2:
            # 첫 번째 선택지에서 선택된 도시를 제외한 리스트 생성
            city_list2 = [city for city in city_list if city != st.session_state.city_1]
            if st.session_state.city_2 not in city_list2:
                st.session_state.city_2 = city_list2[0] if city_list2 else ""
                
            default_idx2 = city_list2.index(st.session_state.city_2) if st.session_state.city_2 in city_list2 else 0
            st.session_state.city_2 = st.selectbox(
                "📍 개선 대상 (잠재 도시)", 
                city_list2, 
                index=default_idx2,
                format_func=format_city
            )

        st.markdown("---")
        st.header(f"2. ⚖️ 심층 1:1 비교 분석: {st.session_state.city_1} vs {st.session_state.city_2}")

        city_1 = st.session_state.city_1
        city_2 = st.session_state.city_2

        # 1:1 비교용 데이터 로드 (OTA 실제 인프라 데이터 연동)
        csv_path = os.path.join(data_dir, 'ota_data.csv')
        if os.path.exists(csv_path):
            df_ota = pd.read_csv(csv_path)
            
            def clean_reviews(r):
                if pd.isna(r): return 0
                r = str(r).replace(',', '').replace('건', '').strip()
                if not r: return 0
                try: return int(float(r))
                except: return 0
                
            def clean_rating(r):
                if pd.isna(r): return 0.0
                try: return float(str(r).strip())
                except: return 0.0

            df_ota['reviews_num'] = df_ota['reviews'].apply(clean_reviews)
            df_ota['rating_num'] = df_ota['rating'].apply(clean_rating)
            
            df_ota_agg = df_ota.groupby('region_sigungu').agg({'title': 'count', 'reviews_num': 'sum', 'rating_num': 'mean'}).reset_index()
            df_ota_agg.columns = ['지역', '상품 수', '총 리뷰 수', '평균 평점']
            
            # 지역명 정규화 (경기도 수원시 -> 경기 수원시)
            mapping_dict = {
                "서울특별시": "서울", "부산광역시": "부산", "대구광역시": "대구", "인천광역시": "인천",
                "광주광역시": "광주", "대전광역시": "대전", "울산광역시": "울산", "세종특별자치시": "세종",
                "경기도": "경기", "강원특별자치도": "강원", "강원도": "강원", "충청북도": "충북", "충청남도": "충남",
                "전북특별자치도": "전북", "전라북도": "전북", "전라남도": "전남", "경상북도": "경북",
                "경상남도": "경남", "제주특별자치도": "제주"
            }
            def normalize_region(name):
                for k, v in mapping_dict.items():
                    name = str(name).replace(k, v)
                return name
            
            df_ota_agg['signguNm'] = df_ota_agg['지역'].apply(normalize_region)
            
            # df_demand 와 병합
            df_merged = pd.merge(df_demand, df_ota_agg, on='signguNm', how='left').fillna(0)
        else:
            df_merged = df_demand.copy()
            df_merged['상품 수'] = 0
            df_merged['총 리뷰 수'] = 0
            df_merged['평균 평점'] = 0

        # 최대값 기준으로 정규화 (0~1)
        max_sns = df_merged["snsMentionCo"].max() or 1
        max_navi = df_merged["naviSearchCo"].max() or 1
        max_infra = df_merged["상품 수"].max() or 1
        max_review = df_merged["총 리뷰 수"].max() or 1
        
        m_c1 = df_merged[df_merged["signguNm"] == city_1]
        m_c2 = df_merged[df_merged["signguNm"] == city_2]

        if not m_c1.empty and not m_c2.empty:
            labels = ["SNS 관심도", "내비 방문도", "관광 상품 수", "글로벌 리뷰 수", "평균 평점(5점 만점)"]
            
            val_c1 = [
                float(m_c1.iloc[0]["snsMentionCo"]) / max_sns,
                float(m_c1.iloc[0]["naviSearchCo"]) / max_navi,
                float(m_c1.iloc[0]["상품 수"]) / max_infra,
                float(m_c1.iloc[0]["총 리뷰 수"]) / max_review,
                float(m_c1.iloc[0]["평균 평점"]) / 5.0
            ]
            
            val_c2 = [
                float(m_c2.iloc[0]["snsMentionCo"]) / max_sns,
                float(m_c2.iloc[0]["naviSearchCo"]) / max_navi,
                float(m_c2.iloc[0]["상품 수"]) / max_infra,
                float(m_c2.iloc[0]["총 리뷰 수"]) / max_review,
                float(m_c2.iloc[0]["평균 평점"]) / 5.0
            ]

            val_c1 = [min(x, 1.0) for x in val_c1]
            val_c2 = [min(x, 1.0) for x in val_c2]

            fig_radar = go.Figure()
            fig_radar.add_trace(go.Scatterpolar(r=val_c1, theta=labels, fill='toself', name=city_1, line_color='#00F0FF', fillcolor='rgba(0, 240, 255, 0.4)'))
            fig_radar.add_trace(go.Scatterpolar(r=val_c2, theta=labels, fill='toself', name=city_2, line_color='#38BDF8', fillcolor='rgba(56, 189, 248, 0.4)'))
            fig_radar.update_layout(
                polar=dict(
                    radialaxis=dict(visible=True, range=[0, 1], gridcolor="#334155", linecolor="#334155"),
                    angularaxis=dict(gridcolor="#334155", linecolor="#334155"),
                    bgcolor="rgba(0,0,0,0)"
                ),
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                font=dict(family="Pretendard, sans-serif", size=14, color="#E2E8F0"),
                hoverlabel=dict(bgcolor="#1E293B", font_size=13, font_family="Pretendard", font=dict(color="#F8FAFC")),
                margin=dict(l=40, r=40, t=40, b=40)
            )
            st.plotly_chart(fig_radar, use_container_width=True)

            c1_infra = int(m_c1.iloc[0]["상품 수"])
            c2_infra = int(m_c2.iloc[0]["상품 수"])
            c1_review = int(m_c1.iloc[0]["총 리뷰 수"])
            c2_review = int(m_c2.iloc[0]["총 리뷰 수"])
            
            infra_diff = "우수" if c1_infra > c2_infra else "부족"
            review_diff = "활발" if c1_review > c2_review else "부족"

            st.markdown("#### 활성화 벤치마킹 인사이트")
            st.info(f"""
            💡 **{city_2} 관광 발전을 위한 데이터 제언**:
            - **{city_1}**의 경우 관광 상품 수({c1_infra}개)와 글로벌 리뷰 수({c1_review}건) 등 실질적인 인프라와 피드백이 강력하게 구축되어 있습니다.
            - 매트릭스 지표 상 **{city_2}**는 상대적으로 인프라(상품 수 {c2_infra}개) 및 해외 리뷰({c2_review}건)가 {infra_diff}하고 매력도가 다를 수 있습니다.
            - {city_1}의 관광 상품 구성(OTA 벤치마킹)과 방문객 후기 패턴을 분석하여, 글로벌 플랫폼에 매력적인 체험형 인프라 패키지를 전략적으로 유통할 것을 권장합니다.
            """)
    else:
        st.warning("분석을 위한 API 데이터를 불러올 수 없습니다.")
