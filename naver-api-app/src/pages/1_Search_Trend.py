"""
이 모듈은 네이버 데이터랩 검색어 트렌드 API를 활용하여 검색어별 관심도 변화를 시각화합니다.
주요 기능:
- 검색어, 기간, 단위 입력 폼
- 데이터랩 통합 검색 API 호출
- Plotly를 이용한 트렌드 꺾은선 그래프 시각화
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.datalab_api import get_search_trend

st.set_page_config(page_title="검색어 트렌드 분석", page_icon="📈")
st.title("검색어 트렌드 분석 📈")

client_id = st.session_state.get("client_id")
client_secret = st.session_state.get("client_secret")

if not client_id or not client_secret:
    st.warning("👈 왼쪽 사이드바에서 API Key를 먼저 설정해주세요.")
    st.stop()

with st.form("search_trend_form"):
    keywords_input = st.text_input("검색어 (쉼표로 구분하여 여러 개 입력 가능)", value="파이썬,자바스크립트")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("시작일", value=datetime.today() - timedelta(days=30))
    with col2:
        end_date = st.date_input("종료일", value=datetime.today())
        
    time_unit = st.selectbox("조회 단위", options=["date", "week", "month"], format_func=lambda x: {"date": "일간", "week": "주간", "month": "월간"}[x])
    
    submit_button = st.form_submit_button("트렌드 조회")

if submit_button:
    keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
    if not keywords:
        st.error("검색어를 입력해주세요.")
    else:
        keyword_groups = [{"groupName": k, "keywords": [k]} for k in keywords]
        
        with st.spinner("데이터를 조회 중입니다..."):
            data = get_search_trend(
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
                time_unit,
                keyword_groups,
                client_id,
                client_secret
            )
            
            if data and "results" in data:
                all_records = []
                for result in data["results"]:
                    title = result["title"]
                    for d in result["data"]:
                        all_records.append({
                            "날짜": d["period"],
                            "검색량(상대값)": d["ratio"],
                            "검색어": title
                        })
                
                if all_records:
                    df = pd.DataFrame(all_records)
                    fig = px.line(df, x="날짜", y="검색량(상대값)", color="검색어", markers=True, title="검색어 트렌드 비교")
                    st.plotly_chart(fig, use_container_width=True)
                    st.dataframe(df)
                else:
                    st.info("조회된 데이터가 없습니다.")
