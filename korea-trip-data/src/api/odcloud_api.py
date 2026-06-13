"""
ODCloud 방한 외래관광객 통계 API 연동 모듈입니다.

주요 기능:
- 한국관광공사 방한 외래관광객 상세 월별 집계 API 호출 및 데이터 가공
- Streamlit Caching 적용을 통한 성능 최적화
- API 호출 실패 시 대안 데이터(Mock) 제공
"""

import os
import requests
import pandas as pd
import streamlit as st
from dotenv import load_dotenv

# .env 파일 로드
load_dotenv()

ODCLOUD_API_KEY = os.getenv("ODCLOUD_API_KEY")
ODCLOUD_BASE_URL = os.getenv("ODCLOUD_BASE_URL", "https://api.odcloud.kr/api")

@st.cache_data(show_spinner="방한 외래객 데이터를 불러오는 중...")
def get_foreigner_monthly_data(page: int = 1, per_page: int = 10000) -> pd.DataFrame:
    """
    방한 외래관광객 상세 월별 집계 데이터를 호출하여 Pandas DataFrame으로 반환합니다.
    API 호출에 실패할 경우, 시각화 검증을 위한 Mock 데이터를 생성하여 반환합니다.
    """
    url = f"{ODCLOUD_BASE_URL}/15136774/v1/uddi:ef3ac703-f138-45ec-a09d-f1f57eade496"
    
    params = {
        "serviceKey": ODCLOUD_API_KEY,
        "page": page,
        "perPage": per_page,
        "returnType": "JSON"
    }
    
    try:
        response = requests.get(url, params=params, timeout=10)
        response.encoding = "utf-8"
        if response.status_code == 200:
            res_data = response.json()
            if "data" in res_data:
                df = pd.DataFrame(res_data["data"])
                # 컬럼명 매핑 정규화 (필요시)
                # API 명세 상 컬럼: 기준연월, 성별, 연령별, 목적별, 교통수단별, 인원수
                return df
            
        print(f"[ODCloud API Error] Status Code: {response.status_code}")
    except Exception as e:
        print(f"[ODCloud API Connection Error]: {e}")
        
    # API 실패 시 시뮬레이션을 위한 Mock 데이터 생성
    print("[ODCloud API] 호출 실패로 인해 테스트용 Mock 데이터를 로드합니다.")
    return _generate_mock_foreigner_data()

def _generate_mock_foreigner_data() -> pd.DataFrame:
    """
    API 호출 실패 시 사용할 2023-2024년 방한 외래관광객 Mock 데이터를 생성합니다.
    """
    import numpy as np
    
    dates = pd.date_range(start="2023-01-01", end="2024-12-01", freq="MS")
    countries = ["중국", "일본", "미국", "대만", "홍콩", "기타"]
    genders = ["여성", "남성"]
    ages = ["20대 이하", "20대", "30대", "40대", "50대", "60대 이상"]
    purposes = ["관광", "상용", "공무", "유학/연수", "기타"]
    transports = ["항공", "선박"]
    
    rows = []
    np.random.seed(42)
    
    for date in dates:
        date_str = date.strftime("%Y-%m-%d")
        for country in countries:
            for gender in genders:
                for age in ages:
                    # 국가별/조건별 관광객 수 가중치 부여
                    base_cnt = 500
                    if country == "일본":
                        base_cnt = 1200
                    elif country == "중국":
                        base_cnt = 1000
                    elif country == "미국":
                        base_cnt = 700
                    
                    if age in ["20대", "30대"]:
                        base_cnt = int(base_cnt * 1.5)
                        
                    people_count = int(np.random.poisson(base_cnt))
                    
                    rows.append({
                        "기준연월": date_str,
                        "국적": country,
                        "성별": gender,
                        "연령별": age,
                        "목적별": np.random.choice(purposes, p=[0.7, 0.05, 0.02, 0.08, 0.15]),
                        "교통수단별": np.random.choice(transports, p=[0.85, 0.15]),
                        "인원수": people_count
                    })
                    
    return pd.DataFrame(rows)
