"""
이 모듈은 네이버 데이터랩 쇼핑 인사이트 API를 활용하여 쇼핑 트렌드를 시각화합니다.
주요 기능:
- 카테고리별 검색어 클릭 트렌드 조회 (연령, 성별, 기기 세부 필터 지원)
- 퀵 기간 설정 및 카테고리/검색어 추천 템플릿 제공
- 평균 클릭량 및 최대 클릭 기록일 요약 메트릭 카드 노출
- Plotly를 이용한 트렌드 꺾은선 그래프 시각화 고도화
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.datalab_api import get_shopping_insight
from api.naver_client import inject_custom_css

# 프리미엄 CSS 테마 적용
inject_custom_css()

st.set_page_config(page_title="쇼핑 트렌드 분석", page_icon="🛒", layout="wide")

# 그라디언트 타이틀
st.markdown('<h1 class="gradient-text">쇼핑 트렌드 분석 🛒</h1>', unsafe_allow_html=True)
st.markdown("""
네이버 쇼핑인사이트 API를 활용하여 카테고리 내 특정 검색어의 클릭량 추이를 비교 분석합니다.  
기기별, 성별별, 연령대별 세부 필터를 설정하여 타겟 고객들의 상세한 관심도 흐름을 추적할 수 있습니다.
""")

client_id = st.session_state.get("client_id")
client_secret = st.session_state.get("client_secret")

if not client_id or not client_secret:
    st.warning("👈 왼쪽 사이드바에서 API Key를 먼저 설정해주세요.")
    st.stop()

# 카테고리 사전 정의
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

# 추천 카테고리/검색어 세션 관리
if "shop_trend_cat" not in st.session_state:
    st.session_state["shop_trend_cat"] = "디지털/가전"
if "shop_trend_key" not in st.session_state:
    st.session_state["shop_trend_key"] = "노트북"

# 추천 템플릿 버튼 이벤트
col_temp1, col_temp2, col_temp3, col_temp4 = st.columns(4)
with col_temp1:
    if st.button("💻 IT 가전 (디지털/가전 - 노트북)"):
        st.session_state["shop_trend_cat"] = "디지털/가전"
        st.session_state["shop_trend_key"] = "노트북"
        st.rerun()
with col_temp2:
    if st.button("👗 트렌디 패션 (패션의류 - 원피스)"):
        st.session_state["shop_trend_cat"] = "패션의류"
        st.session_state["shop_trend_key"] = "원피스"
        st.rerun()
with col_temp3:
    if st.button("🍽️ 간편 식품 (식품 - 밀키트)"):
        st.session_state["shop_trend_cat"] = "식품"
        st.session_state["shop_trend_key"] = "밀키트"
        st.rerun()
with col_temp4:
    if st.button("💄 스킨케어 (화장품/미용 - 선크림)"):
        st.session_state["shop_trend_cat"] = "화장품/미용"
        st.session_state["shop_trend_key"] = "선크림"
        st.rerun()

st.markdown("---")

with st.form("shopping_trend_form"):
    category_name = st.selectbox(
        "카테고리 선택", 
        options=list(categories.keys()),
        index=list(categories.keys()).index(st.session_state["shop_trend_cat"])
    )
    category = categories[category_name]
    
    keyword = st.text_input("분석 검색어", value=st.session_state["shop_trend_key"])
    
    # 퀵 기간 설정
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        quick_period = st.radio("빠른 기간 선택", options=["최근 1개월", "최근 3개월", "최근 6개월", "최근 1년", "직접 지정"], index=1, horizontal=True)
    
    today = datetime.today()
    if quick_period == "최근 1개월":
        default_start = today - timedelta(days=30)
    elif quick_period == "최근 3개월":
        default_start = today - timedelta(days=90)
    elif quick_period == "최근 6개월":
        default_start = today - timedelta(days=180)
    elif quick_period == "최근 1년":
        default_start = today - timedelta(days=365)
    else:
        default_start = today - timedelta(days=90)

    with col2:
        start_date = st.date_input("시작일", value=default_start)
    with col3:
        end_date = st.date_input("종료일", value=today)
        
    col_filter1, col_filter2, col_filter3 = st.columns(3)
    with col_filter1:
        time_unit = st.selectbox(
            "조회 단위", 
            options=["date", "week", "month"], 
            format_func=lambda x: {"date": "일간", "week": "주간", "month": "월간"}[x]
        )
    with col_filter2:
        device = st.selectbox(
            "기기 필터", 
            options=[None, "pc", "mo"], 
            format_func=lambda x: {None: "전체 기기", "pc": "PC", "mo": "모바일"}[x]
        )
    with col_filter3:
        gender = st.selectbox(
            "성별 필터", 
            options=[None, "m", "f"], 
            format_func=lambda x: {None: "전체 성별", "m": "남성", "f": "여성"}[x]
        )
        
    # 연령대 필터 익스팬더 적용
    with st.expander("🔞 연령대 필터 선택 (미선택 시 전체 연령 자동 반영)"):
        ages_options = {
            "1": "~12세", "2": "13~18세", "3": "19~24세", "4": "25~29세",
            "5": "30~34세", "6": "35~39세", "7": "40~44세", "8": "45~49세",
            "9": "50~54세", "10": "55~59세", "11": "60세 이상"
        }
        selected_ages = []
        col_age1, col_age2, col_age3 = st.columns(3)
        for idx, (code, label) in enumerate(ages_options.items()):
            if idx % 3 == 0:
                with col_age1:
                    if st.checkbox(label, key=f"age_{code}"):
                        selected_ages.append(code)
            elif idx % 3 == 1:
                with col_age2:
                    if st.checkbox(label, key=f"age_{code}"):
                        selected_ages.append(code)
            else:
                with col_age3:
                    if st.checkbox(label, key=f"age_{code}"):
                        selected_ages.append(code)

    submit_button = st.form_submit_button("쇼핑 클릭 트렌드 조회 🚀")

if submit_button:
    if not category.strip() or not keyword.strip():
        st.error("카테고리와 검색어를 모두 입력해주세요.")
    else:
        with st.spinner("네이버 쇼핑인사이트 클릭 트렌드 데이터를 분석하고 있습니다..."):
            data = get_shopping_insight(
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
                time_unit,
                category.strip(),
                keyword.strip(),
                client_id,
                client_secret,
                device=device,
                gender=gender,
                ages=selected_ages if selected_ages else None
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
                    
                    # 1. 요약 통계량 계산 및 메트릭 카드 출력
                    st.subheader(f"📊 [{category_name} - {keyword}] 클릭 통계 요약")
                    col_m1, col_m2 = st.columns(2)
                    
                    avg_click = df["클릭량(상대값)"].mean()
                    max_row = df.loc[df["클릭량(상대값)"].idxmax()]
                    max_click = max_row["클릭량(상대값)"]
                    max_date = max_row["날짜"]
                    
                    with col_m1:
                        st.markdown(
                            f"""
                            <div class="metric-card">
                                <h4 style="margin:0;color:#00c73c;">📈 평균 클릭량 관심도</h4>
                                <p style="margin:8px 0 0 0;font-size:24px;font-weight:700;color:#333;">{avg_click:.2f} %</p>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    with col_m2:
                        st.markdown(
                            f"""
                            <div class="metric-card">
                                <h4 style="margin:0;color:#00c73c;">🔥 최대 클릭 관심도 (피크)</h4>
                                <p style="margin:8px 0 0 0;font-size:24px;font-weight:700;color:#333;">{max_click:.2f} %</p>
                                <span style="font-size:12px;color:#999;">(기록 날짜: {max_date})</span>
                            </div>
                            """,
                            unsafe_allow_html=True
                        )
                    
                    # 2. Plotly 고급 라인 차트
                    st.subheader("📈 쇼핑 카테고리 클릭량 트렌드")
                    fig = go.Figure()
                    fig.add_trace(go.Scatter(
                        x=df["날짜"],
                        y=df["클릭량(상대값)"],
                        mode="lines+markers",
                        name=f"{category_name} > {keyword}",
                        line=dict(width=3.5, color="#00c73c"),
                        marker=dict(size=7, symbol="circle"),
                        hovertemplate=f"<b>{keyword}</b><br>날짜: %{{x}}<br>클릭량: %{{y:.2f}}%<extra></extra>"
                    ))
                    
                    fig.update_layout(
                        title=dict(text=f"기간별 상대 클릭량 변화 추이 ({category_name})", font=dict(size=15)),
                        hovermode="x unified",
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        xaxis=dict(showline=True, linecolor="#dcdcdc", gridcolor="#f0f2f6"),
                        yaxis=dict(showline=True, linecolor="#dcdcdc", gridcolor="#f0f2f6"),
                        margin=dict(l=40, r=40, t=60, b=40)
                    )
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 3. 데이터 테이블 및 CSV 다운로드
                    st.subheader("📋 세부 조회 데이터 테이블")
                    
                    file_name = f"naver_shop_trend_{category_name}_{keyword}.csv"
                    csv = df.to_csv(index=False).encode('utf-8-sig')
                    
                    col_dl1, col_dl2 = st.columns([8, 2])
                    with col_dl1:
                        st.dataframe(df, use_container_width=True)
                    with col_dl2:
                        st.download_button(
                            label="📥 CSV 데이터 다운로드",
                            data=csv,
                            file_name=file_name,
                            mime='text/csv'
                        )
                else:
                    st.info("조회된 데이터가 없습니다.")
            else:
                st.info("조회된 데이터가 없습니다. 카테고리 및 검색어 조건을 다시 확인해 주세요.")
