"""
한국관광공사 지역별 관광 다양성 및 자원 수요 API 연동 모듈입니다.

주요 기능:
- AreaTarDivService (관광객, 소비, 국제 다양성) API 데이터 연동
- AreaTarResDemService (서비스 수요, 문화 자원 수요) API 데이터 연동
- Streamlit Caching 기능을 이용한 실시간 로딩 최적화
- API 호출 실패(404 등) 시 기획 시나리오 검증용 고품질 Mock 데이터(도시 1 vs 도시 2 특징 탑재) 자동 생성
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

@st.cache_data(show_spinner="지역별 관광 다양성 데이터를 불러오는 중...")
def get_area_visitor_diversity(base_ym: str = "202601") -> pd.DataFrame:
    """
    지역별 관광객 다양성 정보(연령별 방문자 등)를 조회합니다.
    """
    params = {"baseYm": base_ym}
    items = _request_kto_api(KTO_DIV_ENDPOINT, "getAreaVisitorDivList", params)
    if items:
        return pd.DataFrame(items)
    
    print("[KTO API] getAreaVisitorDivList 호출 실패로 Mock 데이터를 제공합니다.")
    return _generate_mock_visitor_div_data(base_ym)

@st.cache_data(show_spinner="지역별 관광 소비 다양성 데이터를 불러오는 중...")
def get_area_spend_diversity(base_ym: str = "202601") -> pd.DataFrame:
    """
    지역별 관광 소비 다양성 정보(업종별/연령별 소비액)를 조회합니다.
    """
    params = {"baseYm": base_ym}
    items = _request_kto_api(KTO_DIV_ENDPOINT, "getAreaSpendDivList", params)
    if items:
        return pd.DataFrame(items)
    
    print("[KTO API] getAreaSpendDivList 호출 실패로 Mock 데이터를 제공합니다.")
    return _generate_mock_spend_div_data(base_ym)

@st.cache_data(show_spinner="지역별 국제 다양성 데이터를 불러오는 중...")
def get_area_intl_diversity(base_ym: str = "202601") -> pd.DataFrame:
    """
    지역별 국제 다양성 정보(외국인 소비 및 방문 국적 다양성)를 조회합니다.
    """
    params = {"baseYm": base_ym}
    items = _request_kto_api(KTO_DIV_ENDPOINT, "getAreaIntlDivList", params)
    if items:
        return pd.DataFrame(items)
    
    print("[KTO API] getAreaIntlDivList 호출 실패로 Mock 데이터를 제공합니다.")
    return _generate_mock_intl_div_data(base_ym)

@st.cache_data(show_spinner="지역별 관광 서비스 수요 데이터를 불러오는 중...")
def get_area_service_demand(base_ym: str = "202601") -> pd.DataFrame:
    """
    지역별 관광 서비스 수요 정보(SNS 언급량, 검색량 등 관심도)를 조회합니다.
    """
    params = {"baseYm": base_ym}
    items = _request_kto_api(KTO_DEM_ENDPOINT, "getAreaServDemList", params)
    if items:
        return pd.DataFrame(items)
    
    print("[KTO API] getAreaServDemList 호출 실패로 Mock 데이터를 제공합니다.")
    return _generate_mock_service_demand_data(base_ym)

@st.cache_data(show_spinner="지역별 문화 자원 수요 데이터를 불러오는 중...")
def get_area_cultural_demand(base_ym: str = "202601") -> pd.DataFrame:
    """
    지역별 문화 자원 수요 정보(내비게이션 유형별 목적지 검색량)를 조회합니다.
    """
    params = {"baseYm": base_ym}
    items = _request_kto_api(KTO_DEM_ENDPOINT, "getAreaCultDemList", params)
    if items:
        return pd.DataFrame(items)
    
    print("[KTO API] getAreaCultDemList 호출 실패로 Mock 데이터를 제공합니다.")
    return _generate_mock_cultural_demand_data(base_ym)


# ==========================================
# Mock 데이터 생성기 (도시 1 vs 도시 2 가중치 시나리오 탑재)
# ==========================================

# 가상의 시군구 목록 및 관심도-방문도 유형 정의
# 도시 1: 관심도(SNS)도 높고, 실제 방문/소비도 높음 (성공)
# 도시 2: 관심도(SNS)는 높으나, 실제 방문/소비는 낮음 (개선 대상)
CITIES = [
    {"signguCd": "11110", "signguNm": "서울 종로구", "type": "도시1", "sns_weight": 1.5, "visit_weight": 1.5, "spend_weight": 1.4},
    {"signguCd": "11440", "signguNm": "서울 마포구", "type": "도시1", "sns_weight": 1.8, "visit_weight": 1.7, "spend_weight": 1.6},
    {"signguCd": "26000", "signguNm": "부산 해운대구", "type": "도시1", "sns_weight": 1.6, "visit_weight": 1.5, "spend_weight": 1.5},
    {"signguCd": "39110", "signguNm": "제주 제주시", "type": "도시1", "sns_weight": 1.7, "visit_weight": 1.6, "spend_weight": 1.5},
    
    {"signguCd": "32170", "signguNm": "강원 삼척시", "type": "도시2", "sns_weight": 1.3, "visit_weight": 0.5, "spend_weight": 0.4},
    {"signguCd": "37110", "signguNm": "경북 안동시", "type": "도시2", "sns_weight": 1.4, "visit_weight": 0.6, "spend_weight": 0.5},
    {"signguCd": "36110", "signguNm": "전남 여수시", "type": "도시2", "sns_weight": 1.5, "visit_weight": 0.7, "spend_weight": 0.6},
    {"signguCd": "31110", "signguNm": "경기 수원시", "type": "도시2", "sns_weight": 1.2, "visit_weight": 0.8, "spend_weight": 0.7},
    
    # 일반 대조군 도시들
    {"signguCd": "31140", "signguNm": "경기 성남시", "type": "일반", "sns_weight": 0.9, "visit_weight": 1.0, "spend_weight": 1.1},
    {"signguCd": "32010", "signguNm": "강원 춘천시", "type": "일반", "sns_weight": 1.1, "visit_weight": 1.0, "spend_weight": 0.9},
    {"signguCd": "34110", "signguNm": "충남 천안시", "type": "일반", "sns_weight": 0.8, "visit_weight": 0.8, "spend_weight": 0.8},
    {"signguCd": "35110", "signguNm": "전북 전주시", "type": "일반", "sns_weight": 1.2, "visit_weight": 1.1, "spend_weight": 1.0},
    {"signguCd": "38110", "signguNm": "경남 창원시", "type": "일반", "sns_weight": 0.7, "visit_weight": 0.7, "spend_weight": 0.8}
]

def _generate_mock_visitor_div_data(base_ym: str) -> pd.DataFrame:
    """
    지역별 관광객 다양성 Mock 데이터를 생성합니다.
    """
    import numpy as np
    np.random.seed(int(base_ym))
    rows = []
    for city in CITIES:
        # 연령대별 방문객 분포
        base_visitors = 50000 * city["visit_weight"]
        ages = ["20대 이하", "20대", "30대", "40대", "50대", "60대 이상"]
        
        # 도시 1은 청년층 비중이 높음
        if city["type"] == "도시1":
            probs = [0.15, 0.35, 0.25, 0.12, 0.08, 0.05]
        else:
            probs = [0.10, 0.15, 0.20, 0.25, 0.18, 0.12]
            
        visitor_counts = np.random.multinomial(int(base_visitors), probs)
        
        for age, count in zip(ages, visitor_counts):
            rows.append({
                "baseYm": base_ym,
                "signguCd": city["signguCd"],
                "signguNm": city["signguNm"],
                "ageGrp": age,
                "visitorCo": count,
                "cityType": city["type"] # 시각화 시 그룹 필터링용
            })
    return pd.DataFrame(rows)

def _generate_mock_spend_div_data(base_ym: str) -> pd.DataFrame:
    """
    지역별 관광 소비 다양성 Mock 데이터를 생성합니다.
    """
    import numpy as np
    np.random.seed(int(base_ym) + 1)
    rows = []
    industries = ["식음료", "쇼핑", "숙박", "여가/레저", "교통", "문화/체험"]
    
    for city in CITIES:
        base_spend = 100000000 * city["spend_weight"] # 백만원 단위
        
        # 도시 1은 쇼핑과 숙박, 식음료가 균형있게 발달
        if city["type"] == "도시1":
            probs = [0.30, 0.30, 0.20, 0.10, 0.05, 0.05]
        # 도시 2는 식음료에 매우 편중되고 숙박/쇼핑이 저조(관광 인프라 부족 시나리오)
        elif city["type"] == "도시2":
            probs = [0.65, 0.10, 0.05, 0.10, 0.05, 0.05]
        else:
            probs = [0.40, 0.20, 0.15, 0.10, 0.10, 0.05]
            
        spend_amounts = np.random.multinomial(int(base_spend), probs)
        
        for ind, amount in zip(industries, spend_amounts):
            rows.append({
                "baseYm": base_ym,
                "signguCd": city["signguCd"],
                "signguNm": city["signguNm"],
                "indutyNm": ind,
                "cardUseAmt": amount,
                "cityType": city["type"]
            })
    return pd.DataFrame(rows)

def _generate_mock_intl_div_data(base_ym: str) -> pd.DataFrame:
    """
    지역별 국제 다양성 Mock 데이터를 생성합니다.
    """
    import numpy as np
    np.random.seed(int(base_ym) + 2)
    rows = []
    nationalities = ["중국", "일본", "미국", "대만", "유럽", "기타"]
    
    for city in CITIES:
        base_foreigner = 5000 * city["visit_weight"]
        
        # 도시 1은 여러 국적의 외국인이 다양하게 분포 (다양성 지수 높음)
        if city["type"] == "도시1":
            probs = [0.25, 0.25, 0.20, 0.15, 0.10, 0.05]
        # 도시 2는 특정 인접국가나 단일 국적에 극도로 편중됨
        elif city["type"] == "도시2":
            probs = [0.70, 0.10, 0.05, 0.05, 0.05, 0.05]
        else:
            probs = [0.40, 0.20, 0.15, 0.10, 0.10, 0.05]
            
        foreigner_counts = np.random.multinomial(int(base_foreigner), probs)
        
        for nat, count in zip(nationalities, foreigner_counts):
            rows.append({
                "baseYm": base_ym,
                "signguCd": city["signguCd"],
                "signguNm": city["signguNm"],
                "ntntyNm": nat,
                "foreignerVisitorCo": count,
                "cityType": city["type"]
            })
    return pd.DataFrame(rows)

def _generate_mock_service_demand_data(base_ym: str) -> pd.DataFrame:
    """
    지역별 관광 서비스 수요 Mock 데이터를 생성합니다.
    """
    import numpy as np
    np.random.seed(int(base_ym) + 3)
    rows = []
    for city in CITIES:
        # 관심도(SNS 언급량) 생성
        sns_mention = int(10000 * city["sns_weight"] * np.random.uniform(0.9, 1.1))
        # 실제 방문지 내비게이션 검색량
        navi_search = int(8000 * city["visit_weight"] * np.random.uniform(0.9, 1.1))
        
        # SNS 키워드 목업
        if city["type"] == "도시1":
            sns_keywords = "핫플, 인스타감성, 오션뷰, 맛집, 야경"
        elif city["type"] == "도시2":
            sns_keywords = "가족여행, 힐링, 특산물, 축제, 자연"
        else:
            sns_keywords = "당일치기, 주차장, 가성비, 산책, 역사"
            
        rows.append({
            "baseYm": base_ym,
            "signguCd": city["signguCd"],
            "signguNm": city["signguNm"],
            "snsMentionCo": sns_mention,      # SNS 언급량 (관심도)
            "naviSearchCo": navi_search,      # 내비게이션 검색량 (방문도)
            "snsKeywords": sns_keywords,      # SNS 검색 키워드
            "cityType": city["type"]
        })
    return pd.DataFrame(rows)

def _generate_mock_cultural_demand_data(base_ym: str) -> pd.DataFrame:
    """
    지역별 문화 자원 수요 Mock 데이터를 생성합니다.
    """
    import numpy as np
    np.random.seed(int(base_ym) + 4)
    rows = []
    categories = ["역사관광지", "자연관광지", "휴양관광지", "문화시설", "레저스포츠"]
    
    for city in CITIES:
        base_demand = 15000 * city["visit_weight"]
        
        if city["type"] == "도시1":
            probs = [0.20, 0.20, 0.20, 0.30, 0.10]
        elif city["type"] == "도시2":
            # 도시 2는 역사/자연 관광지에 몰려있고 문화시설이나 휴양 인프라가 부족한 시나리오
            probs = [0.45, 0.40, 0.05, 0.05, 0.05]
        else:
            probs = [0.25, 0.25, 0.20, 0.15, 0.15]
            
        demand_counts = np.random.multinomial(int(base_demand), probs)
        
        for cat, count in zip(categories, demand_counts):
            rows.append({
                "baseYm": base_ym,
                "signguCd": city["signguCd"],
                "signguNm": city["signguNm"],
                "clNm": cat,
                "searchCo": count,
                "cityType": city["type"]
            })
    return pd.DataFrame(rows)
