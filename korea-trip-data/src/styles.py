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
            color: #2D3748; /* 차콜 그레이 기본 텍스트 */
            letter-spacing: -0.01em;
        }

        /* 전체 배경 깔끔하게 조정 (Streamlit 구/신버전 호환) */
        .reportview-container, .main, [data-testid="stAppViewContainer"], [data-testid="stApp"] {
            background-color: #f8f9fa !important;
        }

        /* 카드 스타일 컨테이너 정의 */
        .metric-card {
            background-color: #ffffff;
            padding: 20px;
            border-radius: 16px;
            box-shadow: 0 2px 4px rgba(0,0,0,0.05);
            border: 1px solid #e9ecef;
            word-break: keep-all;
            overflow-wrap: break-word;
        }

        /* [개선 1] 메인 배경색 및 레이아웃 최상단 여백 최적화 */
        .main .block-container {
            padding-top: 1.5rem !important; /* 상단 여백 대폭 감소 */
            padding-bottom: 3rem;
            padding-left: 5%;
            padding-right: 5%;
            max-width: 1200px;
        }

        /* [개선 21] Streamlit 상단 고정 헤더 영역의 빈 공간 제거 */
        header[data-testid="stHeader"] {
            height: 2.5rem !important;
            background: transparent !important;
        }

        /* 타이틀 스타일 개선 */
        h1 {
            font-size: 2.2rem !important;
            font-weight: 700 !important;
            color: #1A365D !important;
            margin-bottom: 0.5rem !important;
            letter-spacing: -0.02em !important;
            line-height: 1.3 !important;
        }
        
        /* 서브헤더 스타일 개선 */
        h2 {
            font-size: 1.6rem !important;
            font-weight: 600 !important;
            color: #2B6CB0 !important;
            margin-top: 1.5rem !important;
            margin-bottom: 0.8rem !important;
            letter-spacing: -0.01em !important;
        }
        
        h3 {
            font-size: 1.25rem !important;
            font-weight: 600 !important;
            color: #2D3748 !important;
            margin-top: 1.2rem !important;
            margin-bottom: 0.6rem !important;
        }

        /* [개선 2] 단락 텍스트 가독성 (줄높이 1.8 증가 및 자간 조정) */
        p, li {
            line-height: 1.8 !important;
            font-size: 1.05rem !important;
            color: #4A5568 !important;
            margin-bottom: 0.9rem !important;
        }
        
        /* 굵은 글씨 강조 색상 변경 */
        strong {
            color: #1A365D !important;
        }

        /* 구분선 스타일 조정 */
        hr {
            margin: 2rem 0 !important;
            border: 0;
            border-top: 1px solid #E2E8F0 !important;
        }

        /* [개선 8] Streamlit 기본 알림 박스 (st.info, st.success, st.warning 등) 디자인 커스텀 */
        div[data-testid="stAlert"] {
            border-radius: 12px !important;
            border: 1px solid #E2E8F0 !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05) !important;
            padding: 1.25rem !important;
            margin-bottom: 1.5rem !important;
            background-color: #F8FAFC !important; /* 투박한 노란색/붉은색을 덮는 차분한 배경 */
        }
        
        /* stAlert 경고 메시지 톤앤매너 완화 */
        div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] p {
            color: #334155 !important;
            font-size: 1rem !important;
            line-height: 1.6 !important;
            margin: 0 !important;
        }

        /* [개선 5] Metric (지표 카드) 가독성 및 호버 모션 향상 */
        [data-testid="stMetric"] {
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 16px !important;
            padding: 1.5rem 1.25rem !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.01) !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
            word-break: keep-all !important;
            overflow-wrap: break-word !important;
        }
        
        [data-testid="stMetric"]:hover {
            transform: translateY(-4px) !important; /* 더 뚜렷한 리프트업 효과 */
            box-shadow: 0 10px 15px -3px rgba(0, 0, 0, 0.05), 0 4px 6px -2px rgba(0, 0, 0, 0.03) !important;
            border-color: #2563EB !important; /* 비비드 블루로 보더 하이라이트 */
        }

        /* Label 영역 스타일링 (보조 정보) */
        [data-testid="stMetricLabel"], [data-testid="stMetricLabel"] * {
            font-size: 15px !important;
            font-weight: 500 !important;
            color: #94A3B8 !important;
            text-transform: uppercase !important;
            letter-spacing: 0.02em !important;
        }

        /* stMetricValue와 stMetricDelta를 세로로 강제 배치 */
        [data-testid="stMetric"] > div {
            display: flex !important;
            flex-direction: column !important;
            flex-wrap: nowrap !important;
            align-items: flex-start !important;
            gap: 0.8rem !important; /* 제목과 수치 사이의 여백 넉넉하게 확보 */
        }

        /* Label 래퍼 속성 */
        [data-testid="stMetric"] > div > [data-testid="stMetricLabel"],
        [data-testid="stMetricLabel"] {
            width: 100% !important;
            margin-bottom: 0.2rem !important;
        }

        /* Value 영역 크기 확대 (핵심 정보) */
        [data-testid="stMetricValue"], [data-testid="stMetricValue"] * {
            font-size: 36px !important; /* 32~40px 권장 사이즈 적용 */
            font-weight: 800 !important; /* Bold 유지 */
            color: #2563EB !important; /* 시선을 사로잡는 선명한 블루 계열 */
            letter-spacing: -0.02em !important;
            line-height: 1.1 !important;
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

        /* 혹시나 Streamlit 최신 버전에서 중간 래퍼 없이 직접 자식인 경우 */
        [data-testid="stMetric"] {
            display: flex !important;
            flex-direction: column !important;
            flex-wrap: nowrap !important;
            align-items: flex-start !important;
            gap: 0.2rem !important;
            background-color: #FFFFFF !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 16px !important;
            padding: 1.5rem 1.25rem !important;
            margin-bottom: 2.5rem !important; /* 지표와 하단 차트 간의 행간 여백 확보 */
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.02), 0 2px 4px -1px rgba(0, 0, 0, 0.01) !important;
            transition: all 0.25s cubic-bezier(0.4, 0, 0.2, 1) !important;
            word-break: keep-all !important;
            overflow-wrap: break-word !important;
        }

        /* [개선 9] 사이드바 스타일링 및 컴포넌트 간 여백 부여 */
        section[data-testid="stSidebar"] {
            background-color: #08162A !important; /* Deep Dark Teal/Navy */
            color: #F8FAFC !important;
        }
        
        section[data-testid="stSidebar"] .stMarkdown p {
            color: #E2E8F0 !important;
        }
        
        section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
            color: #F8FAFC !important;
        }
        
        /* 사이드바 입력 폼 간 간격 확보 */
        section[data-testid="stSidebar"] div.element-container {
            margin-bottom: 1.25rem !important;
        }

        /* 데이터프레임 컨테이너 가독성 개선 */
        div[data-testid="stDataFrame"] {
            border: 1px solid #E2E8F0 !important;
            border-radius: 8px !important;
            overflow: hidden !important;
            margin-bottom: 1.5rem !important;
        }
        
        /* 캡션 글자 크기 조정 */
        .stCaption {
            font-size: 0.85rem !important;
            color: #64748B !important;
            line-height: 1.5 !important;
        }
    </style>
    """
    st.markdown(style, unsafe_allow_html=True)
