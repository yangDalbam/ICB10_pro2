"""
Streamlit 애플리케이션의 시각적 가독성 및 UI 디자인을 향상시키기 위한 공통 CSS 스타일을 정의하는 모듈입니다.

이 모듈은 UI/UX를 개선하기 위해 폰트, 여백, 카드 레이아웃, 메트릭 디자인 등의 커스텀 CSS를 주입할 수 있는 
함수를 제공합니다.
"""

import streamlit as st

def apply_custom_style():
    """
    Streamlit 앱에 커스텀 CSS 스타일을 적용합니다.
    """
    style = """
    <link rel="stylesheet" as="style" crossorigin href="https://cdn.jsdelivr.net/gh/orioncactus/pretendard@v1.3.9/dist/web/static/pretendard.css" />
    <style>
        /* 기본 폰트 설정 및 가독성 향상 */
        html, body, [class*="css"], .stMarkdown {
            font-family: 'Pretendard', -apple-system, BlinkMacSystemFont, system-ui, Roboto, "Helvetica Neue", "Segoe UI", "Apple SD Gothic Neo", "Noto Sans KR", "Malgun Gothic", sans-serif;
            font-size: 16px;
            color: #E2E8F0;
            letter-spacing: -0.01em;
        }

        /* 전체 배경 깔끔하게 조정 (Dark Mode) */
        .reportview-container, .main, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
            background-color: #0B1120 !important;
        }

        /* 탭 메뉴(st.tabs) 다크 모드 UI 커스텀 */
        [data-testid="stTabs"] {
            background-color: transparent !important;
        }
        
        button[data-baseweb="tab"] {
            font-size: 16px !important;
            font-weight: 600 !important;
            color: #94A3B8 !important;
            padding: 0.75rem 1.5rem !important;
            border-radius: 8px !important;
            margin-right: 0.5rem !important;
            border: none !important;
            background-color: transparent !important;
            transition: all 0.2s ease-in-out !important;
        }
        
        button[data-baseweb="tab"]:hover {
            color: #00F0FF !important;
            background-color: #1E293B !important;
        }
        
        button[data-baseweb="tab"][aria-selected="true"] {
            color: #00F0FF !important;
            background-color: #121824 !important;
            box-shadow: 0 1px 3px rgba(0,0,0,0.5) !important;
            border-bottom: 2px solid #00F0FF !important;
        }
        
        /* 탭 하단 기본 실선 제거 */
        div[data-baseweb="tab-list"] {
            border-bottom: none !important;
            gap: 4px;
            padding-bottom: 10px;
        }
        
        /* 탭 전환 시 부드러운 Fade-in 애니메이션 */
        div[data-baseweb="tab-panel"] {
            animation: fadeIn 0.4s ease-in-out;
        }
        
        @keyframes fadeIn {
            from { opacity: 0; transform: translateY(10px); }
            to { opacity: 1; transform: translateY(0); }
        }

        /* 메인 배경색 및 레이아웃 최상단 여백 최적화 (Wide Layout) */
        .main .block-container {
            padding-top: 1.5rem !important; 
            padding-bottom: 3rem;
            padding-left: 3%;
            padding-right: 3%;
            max-width: 100%;
        }

        /* Streamlit 상단 고정 헤더 영역의 빈 공간 제거 */
        header[data-testid="stHeader"] {
            height: 2.5rem !important;
            background: transparent !important;
        }

        /* 타이틀 스타일 개선 */
        h1 {
            font-size: 2.2rem !important;
            font-weight: 700 !important;
            color: #F8FAFC !important;
            margin-bottom: 0.5rem !important;
            letter-spacing: -0.02em !important;
            line-height: 1.3 !important;
        }
        
        /* 서브헤더 스타일 개선 */
        h2 {
            font-size: 1.6rem !important;
            font-weight: 600 !important;
            color: #38BDF8 !important;
            margin-top: 1.5rem !important;
            margin-bottom: 0.8rem !important;
            letter-spacing: -0.01em !important;
        }
        
        h3 {
            font-size: 1.25rem !important;
            font-weight: 600 !important;
            color: #E2E8F0 !important;
            margin-top: 1.2rem !important;
            margin-bottom: 0.6rem !important;
        }

        /* 단락 텍스트 가독성 */
        p, li {
            line-height: 1.8 !important;
            font-size: 1.05rem !important;
            color: #94A3B8 !important;
            margin-bottom: 0.9rem !important;
        }
        
        /* 굵은 글씨 강조 색상 변경 */
        strong {
            color: #00F0FF !important;
        }

        /* 구분선 스타일 조정 */
        hr {
            margin: 2rem 0 !important;
            border: 0;
            border-top: 1px solid #1E293B !important;
        }

        /* Streamlit 기본 알림 박스 (st.info, st.success, st.warning 등) 디자인 커스텀 */
        div[data-testid="stAlert"] {
            border-radius: 12px !important;
            border: 1px solid #1E293B !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.5) !important;
            padding: 1.25rem !important;
            margin-bottom: 1.5rem !important;
            background-color: #121824 !important; 
        }
        
        /* stAlert 경고 메시지 톤앤매너 완화 */
        div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] p {
            color: #E2E8F0 !important;
            font-size: 1rem !important;
            line-height: 1.6 !important;
            margin: 0 !important;
        }

        /* Metric (지표 카드) 가독성 및 호버 모션 향상 - 다크 테마 적용 */
        [data-testid="stMetric"] {
            background-color: #121824 !important; 
            border: 1px solid #1E293B !important;
            border-radius: 16px !important; 
            padding: 1.5rem 1.25rem !important; 
            margin-bottom: 2.5rem !important;
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.5), 0 4px 6px -2px rgba(0, 0, 0, 0.3) !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            white-space: nowrap !important;
        }
        
        [data-testid="stMetric"]:hover {
            transform: translateY(-4px) !important; 
            box-shadow: 0 20px 25px -5px rgba(0, 240, 255, 0.15), 0 10px 10px -5px rgba(0, 240, 255, 0.1) !important;
            border-color: #00F0FF !important; 
        }

        /* Label 영역 스타일링 (보조 정보) */
        [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {
            font-size: 15px !important;
            font-weight: 500 !important;
            color: #94A3B8 !important; 
            text-transform: uppercase !important;
            letter-spacing: 0.02em !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            white-space: nowrap !important;
            max-width: 100% !important;
        }

        /* stMetricValue와 stMetricDelta를 세로로 강제 배치 */
        [data-testid="stMetric"] > div {
            display: flex !important;
            flex-direction: column !important;
            flex-wrap: nowrap !important;
            align-items: flex-start !important;
            gap: 0.8rem !important; 
            width: 100% !important;
            overflow: hidden !important;
        }

        [data-testid="stMetric"] > div > [data-testid="stMetricLabel"],
        [data-testid="stMetricLabel"] {
            width: 100% !important;
            margin-bottom: 0.2rem !important;
        }

        /* Value 영역 크기 확대 (핵심 정보) */
        [data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
            font-size: 36px !important; 
            font-weight: 800 !important; 
            color: #F8FAFC !important; 
            letter-spacing: -0.02em !important;
            line-height: 1.1 !important;
            overflow: hidden !important;
            text-overflow: ellipsis !important;
            white-space: nowrap !important;
            max-width: 100% !important;
        }

        /* Delta 영역 인라인 및 크기 조절 */
        [data-testid="stMetricDelta"] {
            font-size: 0.95rem !important;
            font-weight: 700 !important;
            margin-top: 0 !important;
            display: inline-flex !important;
            align-items: center !important;
            width: auto !important;
            padding-left: 0 !important;
        }

        /* 사이드바 스타일링 및 컴포넌트 간 여백 부여 */
        section[data-testid="stSidebar"] {
            background-color: #080D1A !important; 
            color: #F8FAFC !important;
        }
        
        section[data-testid="stSidebar"] .stMarkdown p {
            color: #94A3B8 !important;
        }
        
        section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
            color: #F8FAFC !important;
        }
        
        section[data-testid="stSidebar"] div.element-container {
            margin-bottom: 1.25rem !important;
        }

        /* 데이터프레임 컨테이너 가독성 개선 */
        div[data-testid="stDataFrame"] {
            border: 1px solid #1E293B !important;
            border-radius: 8px !important;
            overflow: hidden !important;
            margin-bottom: 1.5rem !important;
            background-color: #121824 !important;
        }
        
        /* 캡션 글자 크기 조정 */
        .stCaption {
            font-size: 0.85rem !important;
            color: #64748B !important;
            line-height: 1.5 !important;
        }
        
        [data-testid="collapsedControl"] {
            display: none !important;
        }

        /* st.tabs(탭) UI 쾌적하고 고급스럽게 디자인 개선 */
        [data-baseweb="tab-list"] {
            gap: 2rem;
            padding-bottom: 0.5rem;
            border-bottom: 2px solid #1E293B !important;
        }
        [data-baseweb="tab"] {
            font-size: 1.15rem !important;
            font-weight: 600 !important;
            padding-top: 1rem !important;
            padding-bottom: 1rem !important;
            color: #64748B !important;
            border-bottom: 3px solid transparent !important;
            transition: all 0.2s ease-in-out !important;
            background-color: transparent !important;
        }
        [data-baseweb="tab"]:hover {
            color: #00F0FF !important;
        }
        [data-baseweb="tab"][aria-selected="true"] {
            color: #00F0FF !important;
            border-bottom: 3px solid #00F0FF !important;
        }
        [data-baseweb="tab-highlight"] {
            background-color: transparent !important; 
        }

        /* 아코디언 메뉴(Expander) 제목 영역 상하 여백 통일 */
        [data-testid="stExpander"] details summary {
            display: flex !important;
            align-items: center !important;
            justify-content: flex-start !important;
            padding: 10px 15px !important;
            min-height: 40px !important;
            height: auto !important;
            background-color: #121824 !important;
            border: 1px solid #1E293B !important;
            border-radius: 8px !important;
        }
        
        [data-testid="stExpander"] details summary > div,
        [data-testid="stExpander"] details summary > span,
        .streamlit-expanderHeader {
            display: flex !important;
            align-items: center !important;
            margin: 0 !important;
            padding: 0 !important;
            flex: 1 1 0% !important;
        }

        [data-testid="stExpander"] details summary p {
            margin: 0 !important;
            padding: 0 !important;
            line-height: normal !important;
            display: inline-flex !important;
            align-items: center !important;
            color: #E2E8F0 !important;
        }

        /* 사용자 요청 대시보드 밀도 꽉 차게 */
        .block-container {
            padding-top: 2rem !important;
            padding-bottom: 2rem !important;
            padding-left: 3rem !important;
            padding-right: 3rem !important;
            max-width: 100% !important;
        }
    </style>
    """
    st.markdown(style, unsafe_allow_html=True)
