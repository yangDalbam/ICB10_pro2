"""
이 모듈은 네이버 API 대시보드의 메인 진입점(Entry Point)입니다.
주요 기능:
- 애플리케이션 기본 설정
- 사이드바를 통한 API Key (Client ID, Client Secret) 입력
- 세션 상태에 API Key 저장 및 관리
"""

import streamlit as st

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
    client_id = st.text_input("Client ID", type="password")
    client_secret = st.text_input("Client Secret", type="password")
    
    if st.button("설정 저장"):
        if client_id and client_secret:
            st.session_state["client_id"] = client_id.strip()
            st.session_state["client_secret"] = client_secret.strip()
            st.success("API Key가 저장되었습니다!")
        else:
            st.error("Client ID와 Client Secret을 모두 입력해주세요.")
            
    st.markdown("---")
    if "client_id" in st.session_state and "client_secret" in st.session_state:
        st.success("✅ API 설정 완료")
    else:
        st.warning("⚠️ API 설정 필요")
