"""
이 모듈은 네이버 API 대시보드의 메인 진입점(Entry Point)입니다.
주요 기능:
- 애플리케이션 기본 설정 및 글로벌 디자인 주입 (inject_custom_css)
- 사이드바를 통한 API Key (Client ID, Client Secret) 입력 및 .env 저장/로드
- 세션 상태 및 환경 변수를 통한 API Key 관리
- 각 메뉴별 카드형 안내 레이아웃 연출
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

# 세션 상태 초기화
# 1순위: Streamlit secrets (배포 환경 설정)
# 2순위: 환경 변수 / .env 파일 (로컬 개발 환경)
if "client_id" not in st.session_state:
    val = None
    try:
        if "NAVER_CLIENT_ID" in st.secrets:
            val = st.secrets["NAVER_CLIENT_ID"]
    except Exception:
        pass
    if not val:
        val = os.getenv("NAVER_CLIENT_ID", "")
    st.session_state["client_id"] = val.strip() if val else ""

if "client_secret" not in st.session_state:
    val = None
    try:
        if "NAVER_CLIENT_SECRET" in st.secrets:
            val = st.secrets["NAVER_CLIENT_SECRET"]
    except Exception:
        pass
    if not val:
        val = os.getenv("NAVER_CLIENT_SECRET", "")
    st.session_state["client_secret"] = val.strip() if val else ""

from api.naver_client import inject_custom_css

# 프리미엄 CSS 테마 적용
inject_custom_css()

st.set_page_config(
    page_title="Naver API Dashboard",
    page_icon="🟢",
    layout="wide"
)

# 그라디언트 타이틀
st.markdown('<h1 class="gradient-text">네이버 API 분석 대시보드 📊</h1>', unsafe_allow_html=True)
st.markdown("""
이 대시보드는 네이버 검색 및 데이터랩 API를 활용하여 트렌드, 쇼핑, 뉴스, 블로그 등 다각도의 채널 데이터를 실시간 수집하고 시각화 분석을 수행합니다.  
왼쪽 메뉴(사이드바)에서 **API Key**가 정상적으로 설정된 후, 왼쪽의 각 분석 페이지 메뉴를 이동하여 이용해 주세요.
""")

# 메인 뷰 카드 레이아웃 구성
st.subheader("🛠️ 제공하는 분석 서비스")

col1, col2 = st.columns(2)

with col1:
    st.markdown(
        """
        <div class="metric-card">
            <h3>📈 검색어 트렌드 분석</h3>
            <p style="color:#666;font-size:14px;">네이버 데이터랩 API를 연동하여 특정 검색어들의 일별/주별/월별 검색량 추이를 다중 비교합니다. 
            기기, 성별, 연령대별 세부 필터 기능을 지원하여 상세한 수요 변화를 파악할 수 있습니다.</p>
        </div>
        <div class="metric-card">
            <h3>🛍️ 쇼핑 검색 최저가 분석</h3>
            <p style="color:#666;font-size:14px;">지정한 상품 키워드들의 네이버 쇼핑 최저가 정보를 대량으로 긁어모아 평균가, 최저가, 최고가 분포를 한눈에 비교하고 
            가격대별 분포(Box Plot 및 Histogram)를 분석해 줍니다.</p>
        </div>
        <div class="metric-card">
            <h3>📝 블로그 트렌드 분석</h3>
            <p style="color:#666;font-size:14px;">특정 주제에 대한 최신 블로그 발행물들을 수집하고, 일별 발행 추이 및 제목/요약문 내에 가장 많이 등장하는 
            핵심 핵심 단어 Top 10을 시각화 분석하여 전달합니다.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

with col2:
    st.markdown(
        """
        <div class="metric-card">
            <h3>🛒 쇼핑 클릭 트렌드 분석</h3>
            <p style="color:#666;font-size:14px;">네이버 데이터랩의 쇼핑 카테고리별 클릭량 트렌드를 조회합니다. 
            주요 카테고리 안에서 상품 키워드에 대한 타겟 연령/성별의 클릭 전환 매력도를 일 단위로 정밀하게 추적합니다.</p>
        </div>
        <div class="metric-card">
            <h3>📰 뉴스 보도 동향 분석</h3>
            <p style="color:#666;font-size:14px;">검색어와 관련된 주요 언론 기사들의 보도량 추이 변화 및 원문 아웃링크를 연동합니다. 
            수집된 뉴스 기사의 제목과 본문을 기반으로 가장 뜨거운 최근 시사 핵심 단어들을 시각화해 줍니다.</p>
        </div>
        <div class="metric-card">
            <h3>☕ 카페 여론 분석</h3>
            <p style="color:#666;font-size:14px;">카페 게시글을 수집하여 실질적인 소비자의 바이럴 여론 및 후기를 파악합니다. 
            어떤 카페 커뮤니티 채널에서 해당 주제가 가장 뜨겁게 논의되고 있는지 채널별 언급량을 그래프로 제공합니다.</p>
        </div>
        """,
        unsafe_allow_html=True
    )

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


