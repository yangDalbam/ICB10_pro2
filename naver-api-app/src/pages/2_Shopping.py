"""
이 모듈은 네이버 쇼핑 검색 API를 활용하여 상품 검색 결과를 수집하고 분석합니다.
주요 기능:
- 다중 검색어 입력 및 조회 (추천 템플릿 지원)
- 상품 목록 조회 및 링크 아웃(st.column_config.LinkColumn 적용)
- 검색어별 가격 통계 요약 (평균/최고/최저가 메트릭 카드)
- Plotly 최저가 분포 박스 플롯 및 가격대별 히스토그램 시각화
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.search_api import search_shopping
from api.naver_client import inject_custom_css

# 프리미엄 CSS 테마 적용
inject_custom_css()

st.set_page_config(page_title="쇼핑 검색 분석", page_icon="🛍️", layout="wide")

# 그라디언트 타이틀
st.markdown('<h1 class="gradient-text">쇼핑 검색 분석 🛍️</h1>', unsafe_allow_html=True)
st.markdown("""
네이버 쇼핑 API를 사용하여 특정 카테고리나 브랜드 제품들의 최저가 정보를 조회하고 분포를 비교 분석합니다.  
상품 목록의 **상품 링크**를 클릭하시면 실제 쇼핑몰 페이지로 즉시 이동할 수 있습니다.
""")

client_id = st.session_state.get("client_id")
client_secret = st.session_state.get("client_secret")

if not client_id or not client_secret:
    st.warning("👈 왼쪽 사이드바에서 API Key를 먼저 설정해주세요.")
    st.stop()

# 추천 검색어 세션 관리
if "shopping_keywords_input" not in st.session_state:
    st.session_state["shopping_keywords_input"] = "아이패드,갤럭시탭"

# 추천 템플릿 버튼 이벤트
col_temp1, col_temp2, col_temp3, col_temp4 = st.columns(4)
with col_temp1:
    if st.button("📱 태블릿 비교 (아이패드/갤럭시탭)"):
        st.session_state["shopping_keywords_input"] = "아이패드,갤럭시탭"
        st.rerun()
with col_temp2:
    if st.button("🎧 헤드폰 비교 (소니 헤드폰/에어팟 맥스)"):
        st.session_state["shopping_keywords_input"] = "소니 헤드폰,에어팟 맥스"
        st.rerun()
with col_temp3:
    if st.button("👟 인기 운동화 (에어포스/포스)"):
        st.session_state["shopping_keywords_input"] = "나이키 에어포스,아디다스 삼바"
        st.rerun()
with col_temp4:
    if st.button("🏕️ 캠핑 장비 (캠핑 텐트/캠핑 의자)"):
        st.session_state["shopping_keywords_input"] = "캠핑 텐트,캠핑 의자"
        st.rerun()

st.markdown("---")

def remove_html_tags(text):
    return re.sub(r'<[^>]+>', '', text)

with st.form("shopping_search_form"):
    query_input = st.text_input(
        "검색어 (쉼표로 구분하여 여러 개 입력 가능)", 
        value=st.session_state["shopping_keywords_input"]
    )
    
    col1, col2 = st.columns(2)
    with col1:
        display_count = st.slider("검색 건수 (검색어당)", min_value=10, max_value=100, value=50, step=10)
    with col2:
        sort_option = st.selectbox(
            "정렬 기준", 
            options=["sim", "date", "asc", "dsc"], 
            format_func=lambda x: {"sim": "유사도순", "date": "날짜순", "asc": "가격오름차순", "dsc": "가격내림차순"}[x]
        )
        
    submit_button = st.form_submit_button("쇼핑 데이터 검색 및 가격 분석 🔍")

if submit_button:
    queries = [q.strip() for q in query_input.split(",") if q.strip()]
    if not queries:
        st.error("검색어를 입력해주세요.")
    else:
        all_results = []
        with st.spinner("네이버 쇼핑 API로부터 최신 최저가 데이터를 로드하는 중..."):
            for query in queries:
                data = search_shopping(query, client_id, client_secret, display=display_count, sort=sort_option)
                if data and "items" in data:
                    for item in data["items"]:
                        item["query"] = query
                        item["title"] = remove_html_tags(item["title"])
                        all_results.append(item)
            
            if all_results:
                df = pd.DataFrame(all_results)
                # 주요 데이터 정제
                df["lprice"] = pd.to_numeric(df["lprice"])
                
                # 1. 요약 통계량 계산 및 메트릭 카드 출력
                st.subheader("📊 검색어별 가격 통계 요약 (Price Summary)")
                grouped = df.groupby("query")
                col_metrics = st.columns(len(grouped))
                
                for idx, (name, group) in enumerate(grouped):
                    avg_price = group["lprice"].mean()
                    max_price = group["lprice"].max()
                    min_price = group["lprice"].min()
                    
                    with col_metrics[idx]:
                        st.markdown(
                            f"""
                            <div class="metric-card">
                                <h4 style="margin:0;color:#00c73c;">🛒 {name}</h4>
                                <p style="margin:8px 0 0 0;font-size:14px;color:#333;">평균가: <b>{avg_price:,.0f}원</b></p>
                                <p style="margin:4px 0 0 0;font-size:13px;color:#666;">최저가: <span style="color:#d62728;font-weight:600;">{min_price:,.0f}원</span></p>
                                <p style="margin:4px 0 0 0;font-size:13px;color:#666;">최고가: <b>{max_price:,.0f}원</b></p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                
                # 2. 가격 시각화
                st.subheader("📈 가격 통계 시각화 분석")
                tab1, tab2 = st.tabs(["📊 최저가 분포 (Box Plot)", "📉 가격대별 빈도 (Histogram)"])
                
                with tab1:
                    fig_box = px.box(
                        df, x="query", y="lprice", color="query", 
                        title="검색 제품군별 가격 분포 비교 (아웃라이어 분석)",
                        labels={"query": "검색어", "lprice": "최저가 (원)"},
                        points="all",
                        color_discrete_sequence=["#00c73c", "#1f77b4", "#ff7f0e", "#d62728"]
                    )
                    fig_box.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        xaxis=dict(showline=True, linecolor="#dcdcdc"),
                        yaxis=dict(showline=True, linecolor="#dcdcdc", gridcolor="#f0f2f6")
                    )
                    st.plotly_chart(fig_box, use_container_width=True)
                    
                with tab2:
                    fig_hist = px.histogram(
                        df, x="lprice", color="query", barmode="overlay",
                        title="최저가 구간별 상품 등록 빈도 분포",
                        labels={"query": "검색어", "lprice": "최저가 (원)", "count": "상품 개수"},
                        opacity=0.75,
                        color_discrete_sequence=["#00c73c", "#1f77b4", "#ff7f0e", "#d62728"]
                    )
                    fig_hist.update_layout(
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        xaxis=dict(showline=True, linecolor="#dcdcdc"),
                        yaxis=dict(showline=True, linecolor="#dcdcdc", gridcolor="#f0f2f6")
                    )
                    st.plotly_chart(fig_hist, use_container_width=True)
                
                # 3. 데이터 테이블 및 다운로드
                st.subheader("📋 세부 상품 검색 목록")
                
                # 필요한 컬럼만 추출 및 정렬
                display_cols = ["query", "title", "lprice", "mallName", "category1", "category2", "link"]
                df_display = df[[c for c in display_cols if c in df.columns]]
                
                # 다운로드용 데이터 준비
                search_str = "_".join(queries[:3])
                file_name = f"naver_shopping_{search_str}.csv"
                csv = df_display.to_csv(index=False).encode('utf-8-sig')
                
                # 하이퍼링크 컬럼 설정이 포함된 데이터프레임 노출
                st.dataframe(
                    df_display,
                    column_config={
                        "query": st.column_config.TextColumn("검색어"),
                        "title": st.column_config.TextColumn("상품명", width="medium"),
                        "lprice": st.column_config.NumberColumn("최저가 (원)", format="%d"),
                        "mallName": st.column_config.TextColumn("판매몰"),
                        "category1": st.column_config.TextColumn("대분류"),
                        "category2": st.column_config.TextColumn("중분류"),
                        "link": st.column_config.LinkColumn("상품 링크", help="클릭하시면 판매 사이트로 이동합니다.", width="medium")
                    },
                    use_container_width=True
                )
                
                st.download_button(
                    label="📥 쇼핑 데이터 CSV 다운로드",
                    data=csv,
                    file_name=file_name,
                    mime='text/csv'
                )
            else:
                st.info("검색 결과가 없습니다.")
