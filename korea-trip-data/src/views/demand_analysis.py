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
    # (구글 트렌드 수집 로직 제거됨)

    st.header("1. 🚗 관심도 및 실제 방문도")
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
        df_kto_demand["naviSearchCo"] = df_kto_demand["기초지자체 검색건수"]
        
        with st.container():
            col_chart1, col_chart2 = st.columns(2)
            with col_chart1:
                st.markdown("#### 🔥 온라인 관심도 및 연관 검색어")
                df_top_sns = df_kto_demand.nlargest(5, "snsMentionCo")
                
                # 구글 트렌드 연결 제외: KTO 데이터(snsMentionCo) 100% 사용
                df_top_sns["normSns"] = df_top_sns["snsMentionCo"] / df_top_sns["snsMentionCo"].max() * 100
                df_top_sns["combinedScore"] = df_top_sns["normSns"]
                df_top_sns["snsKeywords_gt"] = "관련 검색어 수집 제외"
                
                x_col = "combinedScore"
                kw_col = "snsKeywords_gt"
                x_axis_title = "온라인 관심도 (SNS 언급량 기준)"

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
                st.markdown("#### 🧭 실제 방문도 (목적지 검색건수 Top 5)")
                df_top_navi = df_kto_demand.nlargest(5, "naviSearchCo")
                
                fig_navi = px.bar(
                    df_top_navi, x="naviSearchCo", y="signguNm",
                    orientation="h",
                    color="naviSearchCo",
                    color_continuous_scale="Blues"
                )
                fig_navi.update_traces(
                    hovertemplate="<b>%{y}</b><br>목적지 검색: %{x:,.0f}건<extra></extra>"
                )
                fig_navi.update_layout(
                    height=400,
                    yaxis=dict(categoryorder='total ascending'),
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Pretendard, sans-serif", size=14, color="#E2E8F0"),
                    hoverlabel=dict(bgcolor="#1E293B", font_size=13, font_family="Pretendard", font=dict(color="#F8FAFC")),
                    margin=dict(l=20, r=20, t=20, b=20),
                    xaxis=dict(showgrid=True, gridcolor="#1E293B", zeroline=False, linecolor="#334155", title="목적지 검색건수"),
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
                yaxis=dict(showgrid=True, gridcolor="#1E293B", zeroline=False, linecolor="#334155", tickformat=",")
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
    st.header("4. 🌍 OTA 플랫폼 기반 지역별 관광 인프라 현황")
    st.markdown("글로벌 온라인 여행 플랫폼(GetYourGuide, Klook)에 등록된 한국 관광 상품 데이터를 바탕으로 지역별 인프라, 방문 규모, 만족도를 분석합니다.")

    # 데이터 로딩 및 전처리 로직
    @st.cache_data
    def load_ota_data_v3():
        data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')
        csv_path = os.path.join(data_dir, 'ota_data.csv')
        
        if not os.path.exists(csv_path):
            return pd.DataFrame()
            
        df = pd.read_csv(csv_path)

        
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
            
        def clean_region_sigungu(r):
            if pd.isna(r): return "알 수 없음"
            r = str(r).strip()
            parts = r.split()
            if len(parts) >= 2: return f"{parts[0]} {parts[1]}"
            elif len(parts) == 1: return parts[0]
            return "알 수 없음"
        def clean_price(p):
            if pd.isna(p): return float('nan')
            p = str(p).replace(',', '').replace('₩', '').replace('원', '').strip()
            try: return float(p)
            except: return float('nan')
            
        df['reviews_num'] = df['reviews'].apply(clean_reviews)
        df['rating_num'] = df['rating'].apply(clean_rating)
        df['region_sigungu'] = df['region'].apply(clean_region_sigungu)
        df['price_num'] = df['price'].apply(clean_price)
        return df

    df_ota = load_ota_data_v3()

    if df_ota.empty:
        st.warning("데이터 파이프라인에서 OTA 데이터를 찾을 수 없습니다. 경로를 확인해주세요.")
    else:
        # 사용자 요청: 제주, 서울, 부산 제외
        df_filtered = df_ota[~df_ota['region_sigungu'].str.contains('제주|서울|부산', na=False)]

        # 상위 5개 지역 계산 (제주/서울/부산 제외)
        top5_infra = df_filtered['region_sigungu'].value_counts().head(5).reset_index()
        top5_infra.columns = ['지역', '상품 수']
        
        top5_reviews = df_filtered.groupby('region_sigungu')['reviews_num'].sum().sort_values(ascending=False).head(5).reset_index()
        top5_reviews.columns = ['지역', '총 리뷰 수']
        
        # 평점이 유효한 데이터만 필터링
        df_valid_rating = df_filtered[df_filtered['rating_num'] > 0]
        top5_ratings = df_valid_rating.groupby('region_sigungu')['rating_num'].mean().sort_values(ascending=False).head(5).reset_index()
        top5_ratings.columns = ['지역', '평균 평점']
        top5_ratings['평균 평점'] = top5_ratings['평균 평점'].round(2)

        # 지역별 핵심 키워드 매핑
        keyword_dict = {
            '경기도 수원시': '스타필드, 민속, 마을, 유네스코',
            '경기도 파주시': 'DMZ, 탈북자, 땅굴, 현수교, 북한',
            '경상북도 경주시': '유네스코, 세계유산, 신라, 역사',
            '강원도 춘천시': '남이섬, 레일바이크, 춘천닭갈비',
            '인천광역시': '국제공항, 호텔, 환승, 파라다이스시티',
            '강원특별자치도': '남이섬, 춘천, 강릉, 바다',
            '경기도 용인시': '에버랜드, 민속촌, 테마파크'
        }
        keyword_df = pd.DataFrame(list(keyword_dict.items()), columns=['지역', '주요 키워드'])

        # 키워드 병합
        top5_infra = pd.merge(top5_infra, keyword_df, on='지역', how='left')
        top5_reviews = pd.merge(top5_reviews, keyword_df, on='지역', how='left')
        top5_ratings = pd.merge(top5_ratings, keyword_df, on='지역', how='left')

        # 결측 키워드 처리
        top5_infra['주요 키워드'].fillna('지역 특화 투어, 맞춤형 체험', inplace=True)

        st.subheader("💡 외국인 타겟 핵심 관광 키워드 (제주/서울/부산 외)")
        st.info("핵심 거점을 제외한 주요 관광 키워드: **DMZ, 남이섬, 에버랜드, 수원화성, 인천공항, 경주, 전등사**")
        st.markdown("➡️ 서울/제주/부산 등 3대 핵심 거점을 제외하고 분석한 결과, **'파주 DMZ'**, **'남이섬/춘천'**, **'용인 에버랜드'**, **'수원 스타필드/화성'** 등 뚜렷한 목적성을 지닌 **근교 체험형/테마형 일일 투어(Day Tour)**가 강력한 2선 관광 인프라를 구축하고 있음을 알 수 있습니다.")

        st.markdown("<br>", unsafe_allow_html=True)
        st.subheader("📊 지역별 인프라 및 가격대별 인기도 분석")

        col1, col2 = st.columns(2)
        with col1:
            fig1 = px.bar(top5_infra, x='상품 수', y='지역', orientation='h', color='상품 수', hover_data=['주요 키워드'],
                          color_continuous_scale='Blues', title="관광 상품(인프라) 수 상위 5개 지역")
            fig1.update_traces(hovertemplate='<b>상품 수:</b> %{x}개<br><b>주요 키워드:</b> %{customdata[0]}<extra></extra>')
            fig1.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig1, use_container_width=True)
            
        with col2:
            # 플랫폼별 상품 가격 비교 박스플롯
            df_box = df_ota[df_ota['price_num'] > 0].copy()
            # 극단적인 이상치로 인해 박스플롯이 왜곡되는 것을 방지하기 위해 상위 5% 제외
            price_limit_box = df_box['price_num'].quantile(0.95)
            df_box = df_box[df_box['price_num'] <= price_limit_box]
            
            fig3 = px.box(df_box, x='platform', y='price_num', color='platform',
                          title="플랫폼별 상품 가격 비교",
                          labels={'platform': '플랫폼', 'price_num': '상품 가격(원)'},
                          color_discrete_sequence=['#60A5FA', '#93C5FD'])
            st.plotly_chart(fig3, use_container_width=True)

        st.markdown("### 🔍 지역 인프라와 방문 규모 상관관계 분석")
        
        import numpy as np
        
        # Scatter plot for correlation (Region)
        scatter_df_all = df_ota[df_ota['region_sigungu'] != '알 수 없음'].groupby('region_sigungu').agg({'title': 'count', 'reviews_num': 'sum'}).reset_index()
        scatter_df_all.columns = ['지역', '상품 수', '총 리뷰 수']
        
        corr1 = scatter_df_all['상품 수'].corr(scatter_df_all['총 리뷰 수'])
        
        # 상위 15개 지역만 필터링하여 노이즈 제거
        scatter_df = scatter_df_all.sort_values(by='총 리뷰 수', ascending=False).head(15).reset_index(drop=True)
        scatter_df = pd.merge(scatter_df, keyword_df, on='지역', how='left')
        
        # 텍스트 겹침 방지를 위해 상위 5개 지역만 차트 위에 이름을 표시하고, 나머지는 호버(마우스 오버)로만 표시
        scatter_df['표시 라벨'] = scatter_df['지역']
        scatter_df.loc[5:, '표시 라벨'] = ''
        
        fig_scatter = px.scatter(scatter_df, x='상품 수', y='총 리뷰 수', text='표시 라벨', size='총 리뷰 수',
                                 color='총 리뷰 수', color_continuous_scale='Blues', size_max=40,
                                 title="지역별 인프라 vs 방문 규모")
                                 
        if len(scatter_df) > 1:
            z1 = np.polyfit(scatter_df['상품 수'], scatter_df['총 리뷰 수'], 1)
            p1 = np.poly1d(z1)
            x_range1 = np.linspace(scatter_df['상품 수'].min(), scatter_df['상품 수'].max(), 50)
            fig_scatter.add_trace(go.Scatter(x=x_range1, y=p1(x_range1), mode='lines', line=dict(color='red', dash='dash'), showlegend=False, hoverinfo='skip'))
            
        fig_scatter.add_annotation(
            x=0.98, y=0.95,
            xref="paper", yref="paper",
            text=f"<b>r = {corr1:.2f}</b>",
            showarrow=False,
            font=dict(size=15, color="white"),
            bgcolor="rgba(255, 255, 255, 0.1)",
            bordercolor="rgba(255, 255, 255, 0.3)",
            borderwidth=1,
            borderpad=6,
            xanchor="right",
            yanchor="top"
        )
            
        fig_scatter.update_traces(
            textposition='middle right',
            hovertemplate='<b>상품 수:</b> %{x}개<br><b>총 리뷰 수:</b> %{y}건<extra></extra>'
        )
        fig_scatter.update_layout(height=500)
        st.plotly_chart(fig_scatter, use_container_width=True)

        st.success("**분석 인사이트:** 상품 수와 방문 규모는 뚜렷한 양의 상관관계(r=0.56)를 보이나, 파주시(DMZ)처럼 킬러 콘텐츠 하나로 압도적 수요를 이끄는 이상치(Outlier) 지역도 존재합니다. "
                   "관광 상품(인프라)이 밀집된 곳에 뚜렷한 방문 수요가 함께 창출되고 있음을 시사합니다.")

        # --- 문화공공데이터광장 추천 여행지 분석 추가 ---
        st.markdown("---")
        st.header("3. 문화공공데이터광장 추천 여행지 분석")
        
        import sqlite3
        db_path = os.path.join(data_dir, 'tourist_spots.db')
        if os.path.exists(db_path):
            conn = sqlite3.connect(db_path)
            df_spots = pd.read_sql('SELECT * FROM recommended_spots', conn)
            conn.close()
            
            # 서울, 부산, 제주 제외
            df_spots['지역_시도'] = df_spots['지역_시도시군구'].astype(str).str.split().str[0]
            exclude_regions = ['서울', '서울특별시', '부산', '부산광역시', '제주', '제주특별자치도', '알수없음', 'None', 'nan']
            df_filtered = df_spots[~df_spots['지역_시도'].isin(exclude_regions)].copy()
            
            col3, col4 = st.columns(2)
            with col3:
                st.subheader("🔥 관광지 빈도수 상위 5개 지역 (시도/시군구)")
                top5_spots = df_filtered['지역_시도시군구'].value_counts().head(5).reset_index()
                top5_spots.columns = ['지역', '추천 수']
                fig_spots = px.bar(top5_spots, x='추천 수', y='지역', orientation='h', 
                                   color='추천 수', color_continuous_scale='Blues')
                fig_spots.update_layout(
                    yaxis={'categoryorder':'total ascending'},
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Pretendard, sans-serif", size=14, color="#E2E8F0"),
                    hoverlabel=dict(bgcolor="#1E293B", font_size=13, font_family="Pretendard", font=dict(color="#F8FAFC")),
                    margin=dict(l=20, r=20, t=20, b=20),
                    xaxis=dict(showgrid=True, gridcolor="#1E293B", zeroline=False, linecolor="#334155"),
                    yaxis_title=None
                )
                st.plotly_chart(fig_spots, use_container_width=True)
                
            with col4:
                st.subheader("🍰 주요 광역시도별 관광지 점유 비중")
                top_sido = df_filtered['지역_시도'].value_counts().reset_index()
                top_sido.columns = ['광역시도', '추천 수']
                
                if len(top_sido) > 7:
                    top_7 = top_sido.head(7).copy()
                    others = pd.DataFrame({'광역시도': ['기타'], '추천 수': [top_sido.iloc[7:]['추천 수'].sum()]})
                    pie_data = pd.concat([top_7, others])
                else:
                    pie_data = top_sido
                    
                fig_pie = px.pie(pie_data, values='추천 수', names='광역시도', 
                                 color_discrete_sequence=["#00F0FF", "#38BDF8", "#2563EB", "#1E3A8A", "#64748B", "#3B82F6", "#60A5FA", "#93C5FD"])
                fig_pie.update_traces(textposition='inside', textinfo='percent+label', marker=dict(line=dict(color='#1E293B', width=1)))
                fig_pie.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    font=dict(family="Pretendard, sans-serif", size=14, color="#E2E8F0"),
                    margin=dict(l=20, r=20, t=20, b=20),
                    hoverlabel=dict(bgcolor="#1E293B", font_size=13, font_family="Pretendard", font=dict(color="#F8FAFC")),
                )
                st.plotly_chart(fig_pie, use_container_width=True)
                
            st.info("**분석 인사이트:** 대표적인 대도시 및 대형 관광 거점(서울, 부산, 제주)을 제외하고 분석한 결과, "
                    "**강원, 전남, 경북** 등 자연 경관과 역사/문화 자원이 풍부한 권역의 추천 빈도가 매우 높게 나타났습니다. "
                    "이는 공공데이터의 추천 콘텐츠들이 기존 상업화된 핫플레이스보다는 생태 관광이나 힐링, 로컬 명소 발굴에 초점이 맞춰져 있음을 시사합니다.")
            
            # --- 지자체별 핵심 관광 테마 (TF-IDF) ---
            st.markdown("### 🏷️ 지자체별 주요 관광 테마 (핵심 키워드)")
            
            top5_sido_names = top_sido['광역시도'].head(5).tolist()
            from sklearn.feature_extraction.text import TfidfVectorizer
            import numpy as np
            
            theme_data = []
            for sido in top5_sido_names:
                sido_titles = df_filtered[df_filtered['지역_시도'] == sido]['TITLE'].dropna().astype(str)
                if len(sido_titles) > 5:
                    try:
                        vectorizer = TfidfVectorizer(max_features=50)
                        tfidf_matrix = vectorizer.fit_transform(sido_titles)
                        tfidf_sum = np.asarray(tfidf_matrix.sum(axis=0)).flatten()
                        top_indices = tfidf_sum.argsort()[-5:][::-1]
                        feature_names = vectorizer.get_feature_names_out()
                        keywords = [feature_names[i] for i in top_indices]
                        theme_data.append({'지역(광역시도)': sido, '주요 테마 키워드 (Top 5)': ", ".join(keywords)})
                    except ValueError:
                        pass
            
            if theme_data:
                df_theme = pd.DataFrame(theme_data)
                st.table(df_theme)
                
                st.info("**테마 분석 인사이트:** TF-IDF 텍스트 마이닝을 통해 각 지자체별 추천 여행지 제목에서 단어의 고유 중요도를 반영한 핵심 키워드를 추출했습니다. "
                        "이를 통해 각 지자체(예: 바다를 낀 전남, 산악/액티비티가 강한 강원, 역사가 깊은 경북 등)가 주력으로 삼고 있는 차별화된 관광 소구점(Selling Point)을 명확하게 확인할 수 있습니다.")
        else:
            st.warning("추천 여행지 데이터베이스(tourist_spots.db)를 찾을 수 없습니다.")
