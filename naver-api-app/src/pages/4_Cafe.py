"""
이 모듈은 네이버 카페글 검색 API를 활용하여 카페글 검색 결과를 수집하고 분석합니다.
주요 기능:
- 다중 검색어 입력 및 조회 (추천 템플릿 지원)
- 카페글 목록 조회 및 하이퍼링크 설정 (st.column_config.LinkColumn 적용)
- 카페글 제목 및 설명 텍스트 기반 단어 빈도(Top 10) 분석 시각화
- 출처 카페별 검색어 언급량 비교 차트 시각화
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from collections import Counter
import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.search_api import search_cafearticle
from api.naver_client import inject_custom_css

# 프리미엄 CSS 테마 적용
inject_custom_css()

st.set_page_config(page_title="카페글 검색 분석", page_icon="☕", layout="wide")

# 그라디언트 타이틀
st.markdown('<h1 class="gradient-text">카페글 검색 분석 ☕</h1>', unsafe_allow_html=True)
st.markdown("""
네이버 카페 검색 API를 활용하여 특정 키워드에 대한 여론과 실질적인 반응을 수집하고, 활발하게 언급되는 카페 목록 및 연관 키워드 빈도를 비교 분석합니다.  
목록에서 **카페글 링크**를 클릭하시면 해당 게시글로 즉시 이동할 수 있습니다.
""")

client_id = st.session_state.get("client_id")
client_secret = st.session_state.get("client_secret")

if not client_id or not client_secret:
    st.warning("👈 왼쪽 사이드바에서 API Key를 먼저 설정해주세요.")
    st.stop()

# 추천 검색어 세션 관리
if "cafe_keywords_input" not in st.session_state:
    st.session_state["cafe_keywords_input"] = "캠핑장 추천,차박"

# 추천 템플릿 버튼 이벤트
col_temp1, col_temp2, col_temp3, col_temp4 = st.columns(4)
with col_temp1:
    if st.button("⛺ 아웃도어 레저 (캠핑장 추천/차박)"):
        st.session_state["cafe_keywords_input"] = "캠핑장 추천,차박"
        st.rerun()
with col_temp2:
    if st.button("🏠 재테크 여론 (부동산 대책/내집마련)"):
        st.session_state["cafe_keywords_input"] = "부동산 대책,내집마련"
        st.rerun()
with col_temp3:
    if st.button("🚗 자동차 정보 (하이브리드/전기차 추천)"):
        st.session_state["cafe_keywords_input"] = "하이브리드 추천,전기차 추천"
        st.rerun()
with col_temp4:
    if st.button("🍼 육아 교육 (영어 전집/유모차 추천)"):
        st.session_state["cafe_keywords_input"] = "영어 전집,유모차 추천"
        st.rerun()

st.markdown("---")

def remove_html_tags(text):
    return re.sub(r'<[^>]+>', '', text)

def get_top_keywords(df, text_cols, top_n=10):
    """제목 및 본문 설명 텍스트에서 불용어를 제외한 주요 단어 빈도 Top N을 추출합니다."""
    stopwords = set([
        "은", "는", "이", "가", "을", "를", "에", "의", "로", "과", "와", "한", "합니다", "있습니다",
        "하는", "하고", "해서", "그리고", "하지만", "에서", "으로", "로써", "등", "및", "것", "수", "등등",
        "더", "더욱", "그", "이", "저", "이것", "그것", "저것", "이런", "저런", "그런", "대한", "대해", "위해",
        "통해", "의해", "또한", "매우", "가장", "어떤", "어떻게", "왜", "무엇", "몇", "가지", "때문", "때문에",
        "카페", "네이버", "글", "게시글", "후기", "추천", "공유", "질문", "가입", "회원"
    ])
    
    all_text = ""
    for col in text_cols:
        if col in df.columns:
            all_text += " " + df[col].astype(str).str.cat(sep=" ")
            
    # 특수문자 정제
    cleaned_text = re.sub(r'[^가-힣a-zA-Z0-9\s]', '', all_text)
    words = cleaned_text.split()
    
    # 2글자 이상 단어 필터링
    filtered_words = [
        w for w in words 
        if len(w) >= 2 and w not in stopwords and not w.isdigit()
    ]
    
    counter = Counter(filtered_words)
    return counter.most_common(top_n)

with st.form("cafe_search_form"):
    query_input = st.text_input(
        "검색어 (쉼표로 구분하여 여러 개 입력 가능)", 
        value=st.session_state["cafe_keywords_input"]
    )
    col1, col2 = st.columns(2)
    with col1:
        display_count = st.slider("검색 건수 (검색어당)", min_value=10, max_value=100, value=50, step=10)
    with col2:
        sort_option = st.selectbox(
            "정렬 기준", 
            options=["sim", "date"], 
            format_func=lambda x: {"sim": "유사도순", "date": "날짜순"}[x]
        )
    submit_button = st.form_submit_button("카페글 데이터 분석 시작 🚀")

if submit_button:
    queries = [q.strip() for q in query_input.split(",") if q.strip()]
    if not queries:
        st.error("검색어를 입력해주세요.")
    else:
        all_results = []
        with st.spinner("네이버 카페 게시글을 불러오고 있습니다..."):
            for query in queries:
                data = search_cafearticle(query, client_id, client_secret, display=display_count, sort=sort_option)
                if data and "items" in data:
                    for item in data["items"]:
                        item["query"] = query
                        item["title"] = remove_html_tags(item["title"])
                        item["description"] = remove_html_tags(item["description"])
                        all_results.append(item)
            
            if all_results:
                df = pd.DataFrame(all_results)
                
                # 1. 요약 메트릭 카드
                st.subheader("📊 데이터 분석 요약 (Summary)")
                col_m1, col_m2 = st.columns(2)
                with col_m1:
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <h4 style="margin:0;color:#00c73c;">📑 총 수집 카페글</h4>
                            <p style="margin:8px 0 0 0;font-size:24px;font-weight:700;color:#333;">{len(df)} 개</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                with col_m2:
                    unique_cafes = df["cafename"].nunique() if "cafename" in df.columns else 0
                    st.markdown(
                        f"""
                        <div class="metric-card">
                            <h4 style="margin:0;color:#00c73c;">🏡 출처 카페 채널 수</h4>
                            <p style="margin:8px 0 0 0;font-size:24px;font-weight:700;color:#333;">{unique_cafes} 개 카페</p>
                        </div>
                        """,
                        unsafe_allow_html=True
                    )
                
                # 2. 시각화 탭 분리
                st.subheader("📈 채널 언급량 및 키워드 시각화")
                tab1, tab2 = st.tabs(["🏡 출처 카페별 분석", "🔍 주요 핵심 단어 (Top 10)"])
                
                with tab1:
                    # 언급량 집계 및 정렬
                    cafe_trend = df.groupby(["cafename", "query"]).size().reset_index(name="count")
                    # 상위 15개 카페만 필터링하여 그래프 가독성 증대
                    top_cafes = cafe_trend.groupby("cafename")["count"].sum().nlargest(15).index
                    cafe_trend_filtered = cafe_trend[cafe_trend["cafename"].isin(top_cafes)]
                    cafe_trend_filtered = cafe_trend_filtered.sort_values(by="count", ascending=False)
                    
                    fig_trend = px.bar(
                        cafe_trend_filtered, x="cafename", y="count", color="query", 
                        title="주요 출처 카페별 검색어 언급 수 (상위 15개)",
                        labels={"cafename": "카페명", "count": "언급 수 (개)", "query": "검색어"},
                        barmode="stack",
                        color_discrete_sequence=["#00c73c", "#1f77b4", "#ff7f0e", "#d62728"]
                    )
                    fig_trend.update_layout(
                        xaxis={'categoryorder':'total descending', 'showline':True, 'linecolor':'#dcdcdc'},
                        yaxis={'showline':True, 'linecolor':'#dcdcdc', 'gridcolor':'#f0f2f6'},
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)"
                    )
                    st.plotly_chart(fig_trend, use_container_width=True)
                    
                with tab2:
                    # 간이 키워드 분석
                    top_words = get_top_keywords(df, ["title", "description"])
                    if top_words:
                        words_df = pd.DataFrame(top_words, columns=["단어", "빈도"])
                        fig_words = px.bar(
                            words_df, x="빈도", y="단어", orientation="h",
                            title="수집된 전체 카페글 내 주요 연관 핵심 단어 (Top 10)",
                            labels={"빈도": "빈도수 (회)", "단어": "핵심 키워드"},
                            color_discrete_sequence=["#00c73c"]
                        )
                        fig_words.update_layout(
                            yaxis=dict(autorange="reversed"),
                            plot_bgcolor="rgba(0,0,0,0)",
                            paper_bgcolor="rgba(0,0,0,0)",
                            xaxis=dict(showline=True, linecolor="#dcdcdc", gridcolor="#f0f2f6"),
                            yaxis_gridcolor="rgba(0,0,0,0)"
                        )
                        st.plotly_chart(fig_words, use_container_width=True)
                    else:
                        st.info("텍스트가 부족하여 연관 키워드를 분석할 수 없습니다.")
                
                # 3. 데이터 목록 및 다운로드
                st.subheader("📋 세부 카페글 검색 목록")
                
                display_cols = ["query", "title", "description", "cafename", "link"]
                df_display = df[[c for c in display_cols if c in df.columns]]
                
                search_str = "_".join(queries[:3])
                file_name = f"naver_cafe_{search_str}.csv"
                csv = df_display.to_csv(index=False).encode('utf-8-sig')
                
                st.dataframe(
                    df_display,
                    column_config={
                        "query": st.column_config.TextColumn("검색어"),
                        "title": st.column_config.TextColumn("글 제목", width="medium"),
                        "description": st.column_config.TextColumn("내용 요약", width="large"),
                        "cafename": st.column_config.TextColumn("카페명"),
                        "link": st.column_config.LinkColumn("카페글 링크", help="클릭하시면 해당 네이버 카페 글로 이동합니다.", width="medium")
                    },
                    use_container_width=True
                )
                
                st.download_button(
                    label="📥 카페 데이터 CSV 다운로드",
                    data=csv,
                    file_name=file_name,
                    mime='text/csv'
                )
            else:
                st.info("검색 결과가 없습니다.")
