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
        if response.text:
            st.error(f"오류 상세: {response.text}")
        return None
