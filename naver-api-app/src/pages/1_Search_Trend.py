"""
이 모듈은 네이버 데이터랩 검색어 트렌드 API를 활용하여 검색어별 관심도 변화를 시각화합니다.
주요 기능:
- 검색어, 기간, 단위 입력 폼 (연령, 성별, 기기 세부 필터링 지원)
- 퀵 기간 설정 및 검색어 추천 템플릿 기능
- 데이터랩 통합 검색 API 호출 및 예외 처리
- 주요 통계 메트릭 카드 및 Plotly 라인 차트 고도화 시각화
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from datetime import datetime, timedelta
import sys
import os

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
from api.datalab_api import get_search_trend
from api.naver_client import inject_custom_css

# 프리미엄 CSS 테마 적용
inject_custom_css()

st.set_page_config(page_title="검색어 트렌드 분석", page_icon="📈", layout="wide")

# 그라디언트 타이틀
st.markdown('<h1 class="gradient-text">검색어 트렌드 분석 📈</h1>', unsafe_allow_html=True)
st.markdown("""
네이버 검색어 트렌드 API를 사용하여 특정 검색어들의 관심도 변화 추이를 분석합니다.  
성별, 기기, 연령대 등 세분화된 조건 설정을 지원하며 수치값은 조회 기간 내 **최대 검색량 100 기준의 상대값**입니다.
""")

client_id = st.session_state.get("client_id")
client_secret = st.session_state.get("client_secret")

if not client_id or not client_secret:
    st.warning("👈 왼쪽 사이드바에서 API Key를 먼저 설정해주세요.")
    st.stop()

# 추천 검색어 세션 관리
if "trend_keywords_input" not in st.session_state:
    st.session_state["trend_keywords_input"] = "파이썬,자바스크립트,자바"

# 추천 템플릿 버튼 이벤트
col_temp1, col_temp2, col_temp3, col_temp4 = st.columns(4)
with col_temp1:
    if st.button("💻 개발 언어 비교 (파이썬/자바/JS)"):
        st.session_state["trend_keywords_input"] = "파이썬,자바스크립트,자바"
        st.rerun()
with col_temp2:
    if st.button("🤖 AI 기술 트렌드 (챗GPT/AI/딥러닝)"):
        st.session_state["trend_keywords_input"] = "ChatGPT,인공지능,딥러닝"
        st.rerun()
with col_temp3:
    if st.button("✈️ 여행 트렌드 (일본/베트남/유럽)"):
        st.session_state["trend_keywords_input"] = "일본 여행,베트남 여행,유럽 여행"
        st.rerun()
with col_temp4:
    if st.button("☕ 프랜차이즈 커피 (스타벅스/메가커피)"):
        st.session_state["trend_keywords_input"] = "스타벅스,메가커피,이디야"
        st.rerun()

st.markdown("---")

with st.form("search_trend_form"):
    keywords_input = st.text_input(
        "검색어 그룹 (쉼표로 구분하여 입력, 최대 5개까지 가능)", 
        value=st.session_state["trend_keywords_input"]
    )
    
    # 퀵 기간 설정 버튼 시뮬레이션을 위한 날짜 설정
    col1, col2, col3 = st.columns([2, 2, 2])
    with col1:
        # 퀵 기간 선택 라디오
        quick_period = st.radio("빠른 기간 선택", options=["최근 1개월", "최근 3개월", "최근 6개월", "최근 1년", "직접 지정"], index=1, horizontal=True)
    
    # 빠른 기간 선택에 따른 날짜 자동 셋업
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

    submit_button = st.form_submit_button("트렌드 분석 시작 🚀")

if submit_button:
    # 검색어 정제
    keywords = [k.strip() for k in keywords_input.split(",") if k.strip()]
    if not keywords:
        st.error("최소 1개 이상의 검색어를 입력해주세요.")
    else:
        # 최대 5개 검색그룹 제한 처리
        if len(keywords) > 5:
            st.warning("⚠️ 네이버 검색어 트렌드 API는 최대 5개 그룹까지만 비교가 가능합니다. 앞의 5개 검색어(그룹)로만 진행합니다.")
            keywords = keywords[:5]
            
        keyword_groups = [{"groupName": k, "keywords": [k]} for k in keywords]
        
        with st.spinner("네이버 데이터랩 트렌드 데이터를 분석하고 있습니다..."):
            data = get_search_trend(
                start_date.strftime("%Y-%m-%d"),
                end_date.strftime("%Y-%m-%d"),
                time_unit,
                keyword_groups,
                client_id,
                client_secret,
                device=device,
                gender=gender,
                ages=selected_ages if selected_ages else None
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
                    
                    # 1. 요약 통계량 계산 및 메트릭 카드 출력
                    st.subheader("📊 주요 통계 요약 (Key Metrics)")
                    
                    # 각 검색어 그룹별로 주요 통계량 계산
                    grouped = df.groupby("검색어")
                    col_metrics = st.columns(len(grouped))
                    
                    for idx, (name, group) in enumerate(grouped):
                        avg_val = group["검색량(상대값)"].mean()
                        max_row = group.loc[group["검색량(상대값)"].idxmax()]
                        max_val = max_row["검색량(상대값)"]
                        max_date = max_row["날짜"]
                        
                        with col_metrics[idx]:
                            st.markdown(
                                f"""
                                <div class="metric-card">
                                    <h4 style="margin:0;color:#00c73c;">{name}</h4>
                                    <p style="margin:5px 0 0 0;font-size:14px;color:#666;">평균 관심도: <b>{avg_val:.2f}</b></p>
                                    <p style="margin:5px 0 0 0;font-size:14px;color:#666;">최대 관심도: <b>{max_val}</b></p>
                                    <span style="font-size:11px;color:#999;">(기록일: {max_date})</span>
                                </div>
                                """,
                                unsafe_allow_html=True
                            )
                    
                    # 2. Plotly 고급 시각화
                    st.subheader("📈 관심도 변화 추이")
                    
                    # 커스텀 라인 차트 생성
                    fig = go.Figure()
                    
                    # 색상 테마 조합 정의 (네이버 그린 중심의 프리미엄 조합)
                    colors = ["#00c73c", "#1f77b4", "#ff7f0e", "#d62728", "#9467bd"]
                    
                    for idx, (name, group) in enumerate(grouped):
                        fig.add_trace(go.Scatter(
                            x=group["날짜"],
                            y=group["검색량(상대값)"],
                            mode="lines+markers",
                            name=name,
                            line=dict(width=3, color=colors[idx % len(colors)]),
                            marker=dict(size=6, symbol="circle"),
                            hovertemplate=f"<b>{name}</b><br>날짜: %{{x}}<br>검색량: %{{y:.2f}}%<extra></extra>"
                        ))
                    
                    # 차트 레이아웃 스타일 개선
                    fig.update_layout(
                        hovermode="x unified",
                        plot_bgcolor="rgba(0,0,0,0)",
                        paper_bgcolor="rgba(0,0,0,0)",
                        xaxis=dict(
                            title="조회 기간",
                            gridcolor="#f0f2f6",
                            showline=True,
                            linecolor="#dcdcdc"
                        ),
                        yaxis=dict(
                            title="상대 검색량 (%)",
                            gridcolor="#f0f2f6",
                            showline=True,
                            linecolor="#dcdcdc"
                        ),
                        legend=dict(
                            orientation="h",
                            yanchor="bottom",
                            y=1.02,
                            xanchor="right",
                            x=1
                        ),
                        margin=dict(l=40, r=40, t=80, b=40)
                    )
                    
                    st.plotly_chart(fig, use_container_width=True)
                    
                    # 3. 데이터 테이블 및 다운로드
                    st.subheader("📋 세부 조회 데이터 테이블")
                    
                    # 다운로드 파일명 동적 생성
                    search_str = "_".join(keywords[:3])
                    start_str = start_date.strftime("%Y%m%d")
                    end_str = end_date.strftime("%Y%m%d")
                    file_name = f"naver_trend_{search_str}_{start_str}_to_{end_str}.csv"
                    
                    # CSV 다운로드 버튼 확장
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
                    st.info("조회된 데이터가 없습니다. 검색어 및 날짜 설정을 다시 확인해 주세요.")
