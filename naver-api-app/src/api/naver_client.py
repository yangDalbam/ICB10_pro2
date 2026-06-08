"""
이 모듈은 네이버 OpenAPI 호출을 위한 공통 HTTP 클라이언트 로직을 제공합니다.
주요 기능:
- 인증 헤더 생성
- GET 및 POST 요청 공통 함수 제공
"""

import requests
import streamlit as st

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
