"""
이 모듈은 네이버 OpenAPI 호출을 위한 공통 HTTP 클라이언트 로직을 제공합니다.
주요 기능:
- 인증 헤더 생성
- GET 및 POST 요청 공통 함수 제공
- .env 및 환경 변수로부터 API Key 자동 로드 및 세션 초기화
"""

import os
import requests
import streamlit as st
from dotenv import load_dotenv

# .env 파일 로드 설정
# 실행 경로(CWD), naver_client.py가 속한 디렉토리의 부모 디렉토리(naver-api-app) 등을 탐색하여 로드
current_dir = os.path.dirname(os.path.abspath(__file__))  # src/api
src_dir = os.path.dirname(current_dir)                    # src
naver_api_app_dir = os.path.dirname(src_dir)              # naver-api-app

load_dotenv()
load_dotenv(os.path.join(current_dir, ".env"))
load_dotenv(os.path.join(src_dir, ".env"))
load_dotenv(os.path.join(naver_api_app_dir, ".env"))

# st.session_state에 값이 없을 경우 API Key 로드
# 1순위: Streamlit secrets (배포 환경 설정)
# 2순위: 환경 변수 / .env 파일 (로컬 개발 환경)
if "client_id" not in st.session_state or not st.session_state["client_id"]:
    val = None
    try:
        if "NAVER_CLIENT_ID" in st.secrets:
            val = st.secrets["NAVER_CLIENT_ID"]
    except Exception:
        pass
    if not val:
        val = os.getenv("NAVER_CLIENT_ID", "")
    st.session_state["client_id"] = val.strip() if val else ""

if "client_secret" not in st.session_state or not st.session_state["client_secret"]:
    val = None
    try:
        if "NAVER_CLIENT_SECRET" in st.secrets:
            val = st.secrets["NAVER_CLIENT_SECRET"]
    except Exception:
        pass
    if not val:
        val = os.getenv("NAVER_CLIENT_SECRET", "")
    st.session_state["client_secret"] = val.strip() if val else ""

def get_headers(client_id: str, client_secret: str) -> dict:
    return {
        "X-Naver-Client-Id": client_id,
        "X-Naver-Client-Secret": client_secret
    }

def make_get_request(url: str, params: dict, client_id: str, client_secret: str) -> dict:
    if not client_id or not client_secret:
        st.error("API Key (Client ID, Client Secret)가 설정되지 않았습니다. 왼쪽 메뉴에서 입력해주세요.")
        return None
        
    headers = get_headers(client_id, client_secret)
    try:
        response = requests.get(url, headers=headers, params=params)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API 요청 중 오류가 발생했습니다: {e}")
        if response.text:
            st.error(f"오류 상세: {response.text}")
        return None

def make_post_request(url: str, json_data: dict, client_id: str, client_secret: str) -> dict:
    if not client_id or not client_secret:
        st.error("API Key (Client ID, Client Secret)가 설정되지 않았습니다. 왼쪽 메뉴에서 입력해주세요.")
        return None
        
    headers = get_headers(client_id, client_secret)
    headers["Content-Type"] = "application/json"
    
    try:
        response = requests.post(url, headers=headers, json=json_data)
        response.raise_for_status()
        return response.json()
    except requests.exceptions.RequestException as e:
        st.error(f"API 요청 중 오류가 발생했습니다: {e}")
        try:
            if response.text:
                st.error(f"오류 상세: {response.text}")
        except Exception:
            pass
        return None

def inject_custom_css():
    """모든 페이지에 네이버 브랜드 테마 및 현대적인 UI 디자인 스타일을 주입합니다."""
    st.markdown(
        """
        <style>
        /* 기본 폰트 설정 및 배경 개선 */
        @import url('https://fonts.googleapis.com/css2?family=Inter:wght@300;400;500;600;700&family=Outfit:wght@300;400;500;600;700&family=Noto+Sans+KR:wght@300;400;500;700&display=swap');
        
        html, body, [class*="css"] {
            font-family: 'Inter', 'Outfit', 'Noto Sans KR', sans-serif !important;
        }
        
        /* 버튼 스타일링 */
        div.stButton > button {
            background-color: #00c73c !important;
            color: white !important;
            border-radius: 8px !important;
            border: none !important;
            font-weight: 600 !important;
            padding: 0.5rem 1.25rem !important;
            transition: all 0.25s ease !important;
            box-shadow: 0 4px 6px -1px rgba(0, 199, 60, 0.15), 0 2px 4px -1px rgba(0, 199, 60, 0.05) !important;
        }
        
        div.stButton > button:hover {
            background-color: #00b135 !important;
            transform: translateY(-1px) !important;
            box-shadow: 0 8px 12px -3px rgba(0, 199, 60, 0.25), 0 4px 6px -2px rgba(0, 199, 60, 0.08) !important;
        }
        
        /* 카드 컴포넌트 */
        .metric-card {
            background-color: #ffffff;
            border-radius: 12px;
            padding: 1rem;
            border: 1px solid #eef2f6;
            box-shadow: 0 4px 12px rgba(0, 0, 0, 0.03);
            margin-bottom: 0.75rem;
            transition: transform 0.2s ease, box-shadow 0.2s ease;
        }
        
        .metric-card:hover {
            transform: translateY(-2px);
            box-shadow: 0 8px 20px rgba(0, 0, 0, 0.06);
        }
        
        /* 사이드바 글래스모피즘 */
        [data-testid="stSidebar"] {
            background-color: #f8f9fa !important;
            border-right: 1px solid #eef2f6 !important;
        }
        
        /* 그라디언트 텍스트 및 헤더 */
        .gradient-text {
            background: linear-gradient(135deg, #00c73c 0%, #009c2f 100%);
            -webkit-background-clip: text;
            -webkit-text-fill-color: transparent;
            font-weight: 800;
        }
        
        /* 로딩 스피너 커스텀 */
        .stSpinner > div {
            border-top-color: #00c73c !important;
        }
        
        /* 데이터프레임 스타일 */
        [data-testid="stDataFrame"] {
            border-radius: 10px;
            overflow: hidden;
            border: 1px solid #eef2f6;
        }
        </style>
        """,
        unsafe_allow_html=True
    )
