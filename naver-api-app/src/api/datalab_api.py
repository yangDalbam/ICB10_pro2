"""
이 모듈은 네이버 데이터랩 API(통합 검색어 트렌드, 쇼핑 인사이트)를 호출하는 기능을 제공합니다.
주요 기능:
- 검색어 트렌드 조회 (get_search_trend)
- 쇼핑 인사이트 조회 (get_shopping_insight)
"""

from .naver_client import make_post_request

DATALAB_BASE_URL = "https://openapi.naver.com/v1/datalab"

def get_search_trend(start_date: str, end_date: str, time_unit: str, keyword_groups: list, client_id: str, client_secret: str):
    url = f"{DATALAB_BASE_URL}/search"
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "keywordGroups": keyword_groups
    }
    return make_post_request(url, body, client_id, client_secret)

def get_shopping_insight(start_date: str, end_date: str, time_unit: str, category: str, keyword: str, client_id: str, client_secret: str):
    url = f"{DATALAB_BASE_URL}/shopping/category/keywords"
    body = {
        "startDate": start_date,
        "endDate": end_date,
        "timeUnit": time_unit,
        "category": category,
        "keyword": [
            {"name": keyword, "param": [keyword]}
        ]
    }
    return make_post_request(url, body, client_id, client_secret)
