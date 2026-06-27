"""
외래 관광객 트렌드 및 지역 관광 활성화를 위한 Streamlit 대시보드의 메인 진입점(App)입니다.
"""
import os
import sys
import streamlit as st

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from src.styles import apply_custom_style
from src.views.home import render_home
from src.views.foreigner_trend import render_foreigner_trend
from src.views.tourism_diversity import render_tourism_diversity
from src.views.demand_analysis import render_demand_analysis
from src.views.eda_insights import render_eda_insights

# 페이지 환경설정 (고급 에스테틱 테마 적용)
st.set_page_config(
    page_title="Korea Trip Data랩 - 관광 대시보드",
    page_icon="🗺️",
    layout="wide",
    initial_sidebar_state="collapsed"
)

# 커스텀 CSS 스타일 적용
apply_custom_style()

# 탭 구성
tabs = st.tabs([
    "🏠 홈", 
    "📈 방한 외래객 추이", 
    "💳 관광 소비 현황", 
    "🗺️ 인기 관광 지역", 
    "💡 관광 인사이트 및 관광 활성화 제언"
])

with tabs[0]:
    render_home()
with tabs[1]:
    render_foreigner_trend()
with tabs[2]:
    render_tourism_diversity()
with tabs[3]:
    render_demand_analysis()
with tabs[4]:
    render_eda_insights()


 
