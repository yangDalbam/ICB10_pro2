"""
이 모듈은 네이버 데이터랩 쇼핑 인사이트 API를 활용하여 쇼핑 트렌드를 시각화합니다.
주요 기능:
- 카테고리별 검색어 클릭 트렌드 조회
- Plotly를 이용한 트렌드 꺾은선 그래프 시각화
"""

import streamlit as st
import pandas as pd
import plotly.express as px
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.datalab_api import get_shopping_insight

st.set_page_config(page_title="쇼핑 트렌드 분석", page_icon="🛒")
st.title("쇼핑 트렌드 분석 🛒")

client_id = st.session_state.get("client_id")
client_secret = st.session_state.get("client_secret")

if not client_id or not client_secret:
    st.warning("👈 왼쪽 사이드바에서 API Key를 먼저 설정해주세요.")
    st.stop()

with st.form("shopping_trend_form"):
    categories = {
        "패션의류": "50000000",
        "패션잡화": "50000001",
        "화장품/미용": "50000002",
        "디지털/가전": "50000003",
        "가구/인테리어": "50000004",
        "출산/육아": "50000005",
        "식품": "50000006",
        "스포츠/레저": "50000007",
        "생활/건강": "50000008",
        "여가/생활편의": "50000009",
        "면세점": "50000010",
        "도서": "50005542"
    }
    category_name = st.selectbox("카테고리", options=list(categories.keys()))
    category = categories[category_name]
    
    keyword = st.text_input("검색어", value="원피스")
    
    col1, col2 = st.columns(2)
    with col1:
        start_date = st.date_input("시작일", value=datetime.today() - timedelta(days=30))
    with col2:
        end_date = st.date_input("종료일", value=datetime.today())
        
    time_unit = st.selectbox("조회 단위", options=["date", "week", "month"], format_func=lambda x: {"date": "일간", "week": "주간", "month": "월간"}[x])
    
    submit_button = st.form_submit_button("쇼핑 트렌드 조회")

if submit_button:
    if not category.strip() or not keyword.strip():
        st.error("카테고리 ID와 검색어를 모두 입력해주세요.")
    else:
        with st.spinner("쇼핑 인사이트 데이터를 조회 중입니다..."):
            data = get_shopping_insight(
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
                time_unit,
                category.strip(),
                keyword.strip(),
                client_id,
                client_secret
            )
            
            if data and "results" in data:
                all_records = []
                for result in data["results"]:
                    title = result.get("title", keyword)
                    for d in result["data"]:
                        all_records.append({
                            "날짜": d["period"],
                            "클릭량(상대값)": d["ratio"],
                            "검색어": title
                        })
                
                if all_records:
                    df = pd.DataFrame(all_records)
                    fig = px.line(df, x="날짜", y="클릭량(상대값)", color="검색어", markers=True, title=f"[{category}] 쇼핑 클릭 트렌드")
                    st.plotly_chart(fig, use_container_width=True)
                    st.dataframe(df)
                else:
                    st.info("조회된 데이터가 없습니다.")
