"""
이 모듈은 네이버 검색 API(뉴스, 블로그, 카페글, 쇼핑)를 호출하는 기능을 제공합니다.
주요 기능:
- 뉴스 검색 (search_news)
- 블로그 검색 (search_blog)
- 카페글 검색 (search_cafearticle)
- 쇼핑 검색 (search_shopping)
"""

from .naver_client import make_get_request

BASE_URL = "https://openapi.naver.com/v1/search"

def search_news(query: str, client_id: str, client_secret: str, display: int = 100, start: int = 1, sort: str = "date"):
    url = f"{BASE_URL}/news.json"
    params = {"query": query, "display": display, "start": start, "sort": sort}
    return make_get_request(url, params, client_id, client_secret)

def search_blog(query: str, client_id: str, client_secret: str, display: int = 100, start: int = 1, sort: str = "sim"):
    url = f"{BASE_URL}/blog.json"
    params = {"query": query, "display": display, "start": start, "sort": sort}
    return make_get_request(url, params, client_id, client_secret)

def search_cafearticle(query: str, client_id: str, client_secret: str, display: int = 100, start: int = 1, sort: str = "sim"):
    url = f"{BASE_URL}/cafearticle.json"
    params = {"query": query, "display": display, "start": start, "sort": sort}
    return make_get_request(url, params, client_id, client_secret)

def search_shopping(query: str, client_id: str, client_secret: str, display: int = 100, start: int = 1, sort: str = "sim"):
    url = f"{BASE_URL}/shop.json"
    params = {"query": query, "display": display, "start": start, "sort": sort}
    return make_get_request(url, params, client_id, client_secret)
