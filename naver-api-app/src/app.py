"""
이 모듈은 네이버 API 대시보드의 메인 진입점(Entry Point)입니다.
주요 기능:
- 애플리케이션 기본 설정
- 사이드바를 통한 API Key (Client ID, Client Secret) 입력 및 .env 저장/로드
- 세션 상태 및 환경 변수를 통한 API Key 관리
"""

import os
import streamlit as st
from dotenv import load_dotenv

# .env 파일 로드 설정
# 실행 경로(CWD), app.py가 속한 디렉토리, 그 상위 디렉토리 순서로 로드 시도
current_dir = os.path.dirname(os.path.abspath(__file__))
parent_dir = os.path.dirname(current_dir)  # naver-api-app 폴더

# 1) 현재 디렉토리 및 상위 디렉토리의 .env 로드
load_dotenv()
load_dotenv(os.path.join(current_dir, ".env"))
load_dotenv(os.path.join(parent_dir, ".env"))

# 세션 상태 초기화 (.env 또는 환경 변수값 우선 활용)
# Windows 캐리지 리턴(\r) 등으로 인한 인증 실패를 예방하기 위해 strip() 처리 적용
if "client_id" not in st.session_state:
    val = os.getenv("NAVER_CLIENT_ID", "")
    st.session_state["client_id"] = val.strip() if val else ""
if "client_secret" not in st.session_state:
    val = os.getenv("NAVER_CLIENT_SECRET", "")
    st.session_state["client_secret"] = val.strip() if val else ""

st.set_page_config(
    page_title="Naver API Dashboard",
    page_icon="🟢",
    layout="wide"
)

st.title("네이버 API 분석 대시보드 📊")
st.markdown("""
이 대시보드는 네이버 검색 및 데이터랩 API를 활용하여 다양한 데이터를 분석합니다.
왼쪽 메뉴(사이드바)에서 **API Key**를 입력한 후, 각 페이지를 이용해 주세요.
""")

with st.sidebar:
    st.header("🔑 API 설정")
    
    # 세션 상태에 값이 있을 경우 기본값(value)으로 설정
    client_id = st.text_input("Client ID", value=st.session_state["client_id"], type="password")
    client_secret = st.text_input("Client Secret", value=st.session_state["client_secret"], type="password")
    
    # .env 파일 저장 여부 체크박스 추가
    save_to_file = st.checkbox("입력한 키를 .env 파일에 저장하여 자동 로드", value=True)
    
    if st.button("설정 저장"):
        if client_id and client_secret:
            st.session_state["client_id"] = client_id.strip()
            st.session_state["client_secret"] = client_secret.strip()
            
            save_success = True
            if save_to_file:
                # naver-api-app/.env 파일에 저장
                env_file_path = os.path.join(parent_dir, ".env")
                try:
                    with open(env_file_path, "w", encoding="utf-8") as f:
                        f.write(f"NAVER_CLIENT_ID={client_id.strip()}\n")
                        f.write(f"NAVER_CLIENT_SECRET={client_secret.strip()}\n")
                except Exception as e:
                    st.error(f".env 파일 저장 실패: {e}")
                    save_success = False
            
            if save_success:
                st.success("API 설정이 저장되었습니다! (세션 적용 완료)")
                if save_to_file:
                    st.info("💡 `.env` 파일에 기록되어 다음 실행 시 자동으로 로드됩니다.")
        else:
            st.error("Client ID와 Client Secret을 모두 입력해주세요.")
            
    st.markdown("---")
    if st.session_state["client_id"] and st.session_state["client_secret"]:
        st.success("✅ API 설정 완료")
    else:
        st.warning("⚠️ API 설정 필요")

