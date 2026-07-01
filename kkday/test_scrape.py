"""
이 모듈은 KKDay API의 CSRF 토큰을 가져오고 데이터를 테스트 조회하는 스크립트입니다.
"""
import requests
import json
import re

session = requests.Session()
headers = {
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
}

# 1. 페이지 접속해서 쿠키 및 CSRF 토큰 얻기
res = session.get("https://www.kkday.com/ko/category/kr-south-korea/experiences/list?currency=KRW", headers=headers)
print("Cookies:", session.cookies.get_dict())
match = re.search(r'csrfToken', res.text, re.IGNORECASE)
if match:
    start = max(0, match.start() - 50)
    end = min(len(res.text), match.end() + 100)
    print("Found 'csrf' around:", res.text[start:end])
else:
    match2 = re.search(r'csrf', res.text, re.IGNORECASE)
    if match2:
        start = max(0, match2.start() - 50)
        end = min(len(res.text), match2.end() + 100)
        print("Found 'csrf' around:", res.text[start:end])
    else:
        print("No csrf found in HTML")


# API 요청
api_url = "https://www.kkday.com/api/_nuxt/category/get-search-products"
post_headers = headers.copy()
post_headers["referer"] = "https://www.kkday.com/ko/category/kr-south-korea/experiences/list?currency=KRW"
if csrf_token:
    post_headers["x-csrf-token"] = csrf_token

payload = {
    "productCategory":"CATEGORY_018",
    "destination":"D-KR-120",
    "keyword":"",
    "filters":{},
    "sort":"prec",
    "page":1,
    "count":10
}

response = session.post(api_url, json=payload, headers=post_headers)
print("POST Status Code:", response.status_code)
if response.status_code == 200:
    data = response.json()
    print("Keys:", data.keys())
else:
    print(response.text)
