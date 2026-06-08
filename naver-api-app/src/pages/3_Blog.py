"""
이 모듈은 네이버 블로그 검색 API를 활용하여 블로그 검색 결과를 수집하고 보여줍니다.
주요 기능:
- 다중 검색어 입력 및 조회
- 검색어별 블로그 게시글 결과 제공
- HTML 태그 제거 및 날짜 형식 변환
"""

import streamlit as st
import pandas as pd
import sys
import os
import re

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.search_api import search_blog

st.set_page_config(page_title="블로그 검색 분석", page_icon="📝")
st.title("블로그 검색 분석 📝")

client_id = st.session_state.get("client_id")
client_secret = st.session_state.get("client_secret")

if not client_id or not client_secret:
    st.warning("👈 왼쪽 사이드바에서 API Key를 먼저 설정해주세요.")
    st.stop()

def remove_html_tags(text):
    return re.sub(r'<[^>]+>', '', text)

with st.form("blog_search_form"):
    query_input = st.text_input("검색어 (쉼표로 구분하여 여러 개 입력 가능)", value="인공지능")
    display_count = st.slider("검색 건수", min_value=10, max_value=100, value=50, step=10)
    sort_option = st.selectbox("정렬 기준", options=["sim", "date"], format_func=lambda x: {"sim": "유사도순", "date": "날짜순"}[x])
    submit_button = st.form_submit_button("블로그 검색")

if submit_button:
    queries = [q.strip() for q in query_input.split(",") if q.strip()]
    if not queries:
        st.error("검색어를 입력해주세요.")
    else:
        all_results = []
        with st.spinner("블로그 데이터를 검색 중입니다..."):
            for query in queries:
                data = search_blog(query, client_id, client_secret, display=display_count, sort=sort_option)
                if data and "items" in data:
                    for item in data["items"]:
                        item["query"] = query
                        item["title"] = remove_html_tags(item["title"])
                        item["description"] = remove_html_tags(item["description"])
                        all_results.append(item)
            
            if all_results:
                df = pd.DataFrame(all_results)
                display_cols = ["query", "title", "description", "bloggername", "postdate", "link"]
                df_display = df[[c for c in display_cols if c in df.columns]]
                
                st.subheader("검색 결과 목록")
                st.dataframe(df_display, use_container_width=True)
                
                st.subheader("검색어별 날짜 추이")
                import plotly.express as px
                df_display["date"] = pd.to_datetime(df_display["postdate"]).dt.date
                trend_df = df_display.groupby(["date", "query"]).size().reset_index(name="count")
                fig = px.line(trend_df, x="date", y="count", color="query", markers=True, title="날짜별 블로그 포스트 발행 수")
                st.plotly_chart(fig, use_container_width=True)
            else:
                st.info("검색 결과가 없습니다.")
