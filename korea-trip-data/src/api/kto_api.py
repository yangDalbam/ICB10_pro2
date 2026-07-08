"""
한국관광공사 지역별 관광 다양성 및 자원 수요 API 연동 모듈입니다.

주요 기능:
- AreaTarDivService (관광객, 소비, 국제 다양성) API 데이터 연동
- AreaTarResDemService (서비스 수요, 문화 자원 수요) API 데이터 연동
- Streamlit Caching 기능을 이용한 실시간 로딩 최적화
- API 호출 실패 시 또는 미구현 함수는 빈 데이터프레임을 반환합니다 (Mock 생성 로직 제거)
"""

import os
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# .env 로드
load_dotenv()

KTO_API_KEY = os.getenv("KTO_API_KEY")
KTO_DIV_ENDPOINT = os.getenv("KTO_DIV_ENDPOINT", "https://apis.data.go.kr/B551011/AreaTarDivService")
KTO_DEM_ENDPOINT = os.getenv("KTO_DEM_ENDPOINT", "https://apis.data.go.kr/B551011/AreaTarResDemService")

def _request_kto_api(base_url: str, operation: str, params: dict) -> list:
    """
    공공데이터포털 한국관광공사 API를 호출하는 공통 헬퍼 함수입니다.
    """
    url = f"{base_url}/{operation}"
    full_params = {
        "serviceKey": KTO_API_KEY,
        "numOfRows": 1000,
        "pageNo": 1,
        "MobileOS": "ETC",
        "MobileApp": "AppTest",
        "_type": "json"
    }
    full_params.update(params)
    
    try:
        response = requests.get(url, params=full_params, timeout=10)
        if response.status_code == 200:
            res_json = response.json()
            # 공공데이터포털 표준 response 구조 파싱
            body = res_json.get("response", {}).get("body", {})
            items = body.get("items", {})
            if isinstance(items, dict) and "item" in items:
                item_list = items["item"]
                return item_list if isinstance(item_list, list) else [item_list]
        print(f"[KTO API Error] {operation} Status Code: {response.status_code}")
    except Exception as e:
        print(f"[KTO API Connection Error] {operation}: {e}")
    return []

# ==========================================
# 기존 API 연동 함수 (Mock 제거 및 빈 값 반환 적용)
# ==========================================

@st.cache_data(show_spinner="지역별 관광 다양성 데이터를 불러오는 중...")
def get_area_visitor_diversity(base_ym: str = "202601") -> pd.DataFrame:
    """지역별 관광객 다양성 정보(연령별 방문자 등)를 조회합니다."""
    params = {"baseYm": base_ym}
    items = _request_kto_api(KTO_DIV_ENDPOINT, "getAreaVisitorDivList", params)
    if items:
        return pd.DataFrame(items)
    return pd.DataFrame()

@st.cache_data(show_spinner="지역별 관광 소비 다양성 데이터를 불러오는 중...")
def get_area_spend_diversity(base_ym: str = "202601") -> pd.DataFrame:
    """지역별 관광 소비 다양성 정보(업종별/연령별 소비액)를 조회합니다."""
    params = {"baseYm": base_ym}
    items = _request_kto_api(KTO_DIV_ENDPOINT, "getAreaSpendDivList", params)
    if items:
        return pd.DataFrame(items)
    return pd.DataFrame()

@st.cache_data(show_spinner="지역별 국제 다양성 데이터를 불러오는 중...")
def get_area_intl_diversity(base_ym: str = "202601") -> pd.DataFrame:
    """지역별 국제 다양성 정보(외국인 소비 및 방문 국적 다양성)를 조회합니다."""
    params = {"baseYm": base_ym}
    items = _request_kto_api(KTO_DIV_ENDPOINT, "getAreaIntlDivList", params)
    if items:
        return pd.DataFrame(items)
    return pd.DataFrame()

@st.cache_data(show_spinner="지역별 관광 서비스 수요 데이터를 불러오는 중...")
def get_area_service_demand(base_ym: str = "202601") -> pd.DataFrame:
    """지역별 관광 서비스 수요 정보(SNS 언급량, 검색량 등 관심도)를 조회합니다."""
    params = {"baseYm": base_ym}
    items = _request_kto_api(KTO_DEM_ENDPOINT, "getAreaServDemList", params)
    if items:
        return pd.DataFrame(items)
    return pd.DataFrame()

@st.cache_data(show_spinner="지역별 문화 자원 수요 데이터를 불러오는 중...", ttl=86400)
def get_area_cultural_demand(base_ym: str = "202601") -> pd.DataFrame:
    """지역별 문화 자원 수요 정보(내비게이션 유형별 목적지 검색량)를 조회합니다."""
    params = {"baseYm": base_ym}
    items = _request_kto_api(KTO_DEM_ENDPOINT, "getAreaCultDemList", params)
    if items:
        return pd.DataFrame(items)
    return pd.DataFrame()


# ==========================================
# 신규 요청된 12개 수집 항목 (현재 뼈대만 작성, 빈 데이터프레임 반환)
# ==========================================

def get_foreign_visitor_region_ratio(base_ym: str = "202601") -> pd.DataFrame:
    """1. 외래관광객지역비율"""
    # TODO: 정확한 KTO API Endpoint 및 Operation 파악 후 구현
    return pd.DataFrame()

def get_foreign_visitor_activity(base_ym: str = "202601") -> pd.DataFrame:
    """2. 외래관광객방한활동비율(식도락, 업무, 투어 등)"""
    return pd.DataFrame()

def get_foreign_visitor_spend(base_ym: str = "202601") -> pd.DataFrame:
    """3. 외래관광객지출(1인 평균 지출 등)"""
    return pd.DataFrame()

def get_related_tourist_spots(base_ym: str = "202601") -> pd.DataFrame:
    """4. 키워드 검색 관광지별 연관 관광지 정보 목록"""
    return pd.DataFrame()

def get_local_visitor_count(base_ym: str = "202601") -> pd.DataFrame:
    """5. 광역/기초 지차제 지역방문자수 집계 데이터"""
    return pd.DataFrame()

def get_foreign_visitor_demographics(base_ym: str = "202601") -> pd.DataFrame:
    """6. 성별, 연령별, 교통수단별 방한 외래관광객"""
    return pd.DataFrame()

def get_visitor_by_nationality(base_ym: str = "202601") -> pd.DataFrame:
    """7. 국적별 방문자 수, 소비액"""
    return pd.DataFrame()

def get_sns_and_navigation(base_ym: str = "202601") -> pd.DataFrame:
    """8. SNS 언급량, 소비액, 내비게이션"""
    return pd.DataFrame()

def get_search_by_tour_type(base_ym: str = "202601") -> pd.DataFrame:
    """9. 문화 관광/레저 스포츠/역사 관광/체험 관광/자연 관광 유형별 목적지 검색량"""
    return pd.DataFrame()

def get_spend_type_by_country(base_ym: str = "202601") -> pd.DataFrame:
    """10. 국가별 관광소비 유형"""
    return pd.DataFrame()

def get_spend_trend_by_industry(base_ym: str = "202601") -> pd.DataFrame:
    """11. 업종별 관광소비 추이"""
    return pd.DataFrame()

def get_foreign_visitor_trend_by_region(base_ym: str = "202601") -> pd.DataFrame:
    """12. 외국인 지역별 방문자 수 추이"""
    return pd.DataFrame()
