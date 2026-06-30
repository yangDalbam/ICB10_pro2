"""
홈 화면 뷰 모듈입니다.
주요 기능: 
- 대시보드 타이틀 및 안내 제공
"""
import streamlit as st
from datetime import datetime

def render_home():
    # 메인 헤더 영역
    col_title, col_date = st.columns([4, 1])
    with col_title:
        st.title("🇰🇷 한국 관광 데이터 대시보드")
        st.caption("공공 데이터를 기반으로 한 국내 관광 트렌드 및 분석 현황 (온/오프라인 행동 융합)")
        st.caption("🔹 **자료 출처:** 한국관광공사(한국관광 데이터랩), 공공데이터포털(ODCloud)")
    with col_date:
        today_str = datetime.today().strftime("%Y-%m-%d")
        st.markdown(f"<div style='text-align: right; color: #64748B; padding-top: 2rem; font-size: 0.9rem;'>Data updated: {today_str}</div>", unsafe_allow_html=True)

    st.write("---")
