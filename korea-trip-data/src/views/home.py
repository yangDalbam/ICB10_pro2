"""
홈 화면 뷰 모듈입니다.
주요 기능: 
- 대시보드 타이틀 및 안내 제공
"""
import streamlit as st
from datetime import datetime

@st.dialog("🇰🇷 한국 관광 데이터 대시보드 데이터 수집 및 분석 명세", width="large")
def show_data_source_dialog():
    st.markdown("""
    ### 1. 데이터 수집 기준 및 처리 프로세스
    본 대시보드는 2024년 기준의 한국관광 데이터랩(KTO), 공공데이터포털(ODCloud), 신한카드/BC카드 빅데이터, 구글 트렌드 검색어 데이터를 수집하여 개발되었습니다. 모든 데이터는 정교한 전처리 과정을 거쳐 지역별 및 지표별 통계로 가공되었습니다.
    
    ### 2. 지표별 데이터 수집 상세 근거
    - 📈 **방한 외래관광객 트렌드:** 출처: 한국관광 데이터랩(KTO) 및 한국문화관광연구원. 월별/국가별/연령별 외래 관광객 실태조사 데이터를 기반으로 집계된 수치입니다.
    - 💳 **관광 소비 현황:** 출처: 신한카드 및 BC카드 빅데이터. 외국인 관광객의 실제 카드 소비 결제 금액 및 건수를 바탕으로 산출된 인덱스입니다.
    - 🗺️ **인기 관광 지역 (온라인 관심도):** KTO 지역별 'SNS 언급량'을 100점 만점으로 정규화한 값(50%)과 구글 트렌드 API(`pytrends`)의 최근 3개월 지역별 평균 검색 관심도(50%)를 합산하여 종합 관심도를 산출했습니다.
    - 🧭 **실제 방문도 및 방문 목적:** 한국관광공사 지역별 관광 자원 수요 API 데이터를 활용하여, 내비게이션 검색량을 목적별(역사, 자연, 휴양, 문화, 레저)로 세분화하여 누적 시각화했습니다.
    - 📍 **지역 집중화 추이 및 성수기 히트맵:** 공공데이터포털 외국인 방문객 데이터 기반으로 누적 방문객이 가장 많은 상위 5개 지역의 월별 변동 추이와 성수기 집중도를 시각화했습니다.
    - 🧩 **온-오프라인 매트릭스 진단:** 종합 관심도와 실제 방문도(내비게이션)를 활용하여 2x2 매트릭스를 구성하고, 내비게이션 검색 데이터를 활용해 각 지역의 관광 목적 강점을 다각도로 분석한 방사형 차트입니다.
    """)

def render_home():
    # 메인 헤더 영역
    col_title, col_date = st.columns([4, 1])
    with col_title:
        st.title("🇰🇷 한국 관광 데이터 대시보드")
        st.caption("공공 데이터를 기반으로 한 국내 관광 트렌드 및 분석 현황 (온/오프라인 행동 융합)")
        
        c_text, c_btn = st.columns([4, 1])
        with c_text:
            st.markdown("<p style='font-size: 0.9rem; color: #94A3B8; margin-top: 5px;'>📊 <b>분석 근거 기준:</b> 한국관광공사(데이터랩), 공공데이터포털, 구글 트렌드 (모두 2024년 기준)</p>", unsafe_allow_html=True)
        with c_btn:
            if st.button("상세 출처/근거 보기", use_container_width=True):
                show_data_source_dialog()
                
    with col_date:
        today_str = datetime.today().strftime("%Y-%m-%d")
        st.markdown(f"<div style='text-align: right; color: #64748B; padding-top: 2rem; font-size: 0.9rem;'>Data updated: {today_str}</div>", unsafe_allow_html=True)

    st.write("---")
