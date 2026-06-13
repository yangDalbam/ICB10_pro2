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
            color: #2D3748;
        }

        /* 메인 배경색 및 레이아웃 패딩 최적화 */
        .main .block-container {
            padding-top: 3rem;
            padding-bottom: 3rem;
            padding-left: 5%;
            padding-right: 5%;
            max-width: 1200px;
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

        /* 단락 텍스트 가독성 (줄높이 및 여백) */
        p, li {
            line-height: 1.7 !important;
            font-size: 1.05rem !important;
            color: #4A5568 !important;
            margin-bottom: 0.8rem !important;
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

        /* Streamlit 기본 알림 박스 (st.info, st.success 등) 디자인 커스텀 */
        div[data-testid="stAlert"] {
            border-radius: 12px !important;
            border: none !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05), 0 2px 4px -1px rgba(0, 0, 0, 0.03) !important;
            padding: 1.25rem !important;
            margin-bottom: 1.5rem !important;
        }
        
        div[data-testid="stAlert"] [data-testid="stMarkdownContainer"] p {
            color: #2D3748 !important;
            font-size: 1rem !important;
            line-height: 1.6 !important;
            margin: 0 !important;
        }

        /* Metric (지표 카드) 가독성 향상 */
        div[data-testid="stMetric"] {
            background-color: #F8FAFC !important;
            border: 1px solid #E2E8F0 !important;
            border-radius: 12px !important;
            padding: 1rem 1.25rem !important;
            box-shadow: 0 1px 3px 0 rgba(0, 0, 0, 0.05) !important;
            transition: transform 0.2s ease, box-shadow 0.2s ease !important;
        }
        
        div[data-testid="stMetric"]:hover {
            transform: translateY(-2px) !important;
            box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.1) !important;
            border-color: #CBD5E1 !important;
        }

        div[data-testid="stMetricLabel"] {
            font-size: 0.9rem !important;
            font-weight: 500 !important;
            color: #64748B !important;
            margin-bottom: 0.25rem !important;
        }

        div[data-testid="stMetricValue"] {
            font-size: 1.6rem !important;
            font-weight: 700 !important;
            color: #0F172A !important;
        }

        div[data-testid="stMetricDelta"] {
            font-size: 0.85rem !important;
            font-weight: 600 !important;
        }

        /* 사이드바 스타일링 */
        section[data-testid="stSidebar"] {
            background-color: #0F172A !important;
            color: #F8FAFC !important;
        }
        
        section[data-testid="stSidebar"] .stMarkdown p {
            color: #E2E8F0 !important;
        }
        
        section[data-testid="stSidebar"] h1, section[data-testid="stSidebar"] h2, section[data-testid="stSidebar"] h3 {
            color: #F8FAFC !important;
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
