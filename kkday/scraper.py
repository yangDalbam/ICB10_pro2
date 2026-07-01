"""
이 모듈은 KKDay의 API를 활용하여 한국 지역 체험 상품 데이터를 스크래핑하고 SQLite 데이터베이스에 저장합니다.
"""
from playwright.sync_api import sync_playwright
import sqlite3
import json
import time
import random

import os
import re

DB_DIR = os.path.join(os.path.dirname(__file__), "data")
os.makedirs(DB_DIR, exist_ok=True)
DB_NAME = os.path.join(DB_DIR, "kkday_experiences.db")

def extract_region(title, p_id):
    if str(p_id) == "119655":
        return "용인"
    if str(p_id) == "134684":
        return "부산"
        
    title = title.strip()
    if title.startswith('['):
        end_idx = title.find(']')
        if end_idx != -1:
            bracket_text = title[1:end_idx]
            parts = re.split(r'[\s/|]', bracket_text)
            for p in parts:
                if p.strip():
                    return p.strip()
                    
    parts = title.split(' ')
    for p in parts:
        if p.strip():
            return p.strip()
            
    return ""

def init_db():
    conn = sqlite3.connect(DB_NAME)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS experiences (
            id TEXT PRIMARY KEY,
            title TEXT,
            duration TEXT,
            rating REAL,
            reviews INTEGER,
            price REAL,
            page INTEGER,
            region TEXT,
            raw_data TEXT
        )
    ''')
    conn.commit()
    return conn

def upsert_experience(conn, data):
    cursor = conn.cursor()
    cursor.execute('''
        INSERT INTO experiences (id, title, duration, rating, reviews, price, page, region, raw_data)
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            title=excluded.title,
            duration=excluded.duration,
            rating=excluded.rating,
            reviews=excluded.reviews,
            price=excluded.price,
            page=excluded.page,
            region=excluded.region,
            raw_data=excluded.raw_data
    ''', data)
    conn.commit()

def run():
    conn = init_db()
    
    with sync_playwright() as p:
        browser = p.chromium.launch(headless=True)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
            locale="ko-KR",
            extra_http_headers={"accept-language": "ko-KR,ko;q=0.9"}
        )
        page = context.new_page()
        
        csrf_token = None
        
        def handle_request(request):
            nonlocal csrf_token
            if not csrf_token and 'x-csrf-token' in request.headers:
                csrf_token = request.headers['x-csrf-token']
                
        context.on("request", handle_request)
        
        print("페이지 접속 및 초기화 중...")
        # 통화를 KRW로 설정하여 접속 (API 응답이 KRW로 오게 함)
        page.goto("https://www.kkday.com/ko/category/kr-south-korea/experiences/list?currency=KRW")
        page.wait_for_load_state("networkidle")
        
        # csrf_token이 캡처될 때까지 잠시 대기
        for _ in range(10):
            if csrf_token:
                break
            time.sleep(0.5)
            
        if not csrf_token:
            print("CSRF 토큰을 찾지 못했습니다. 페이지 상호작용으로 트리거합니다.")
            page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
            page.wait_for_timeout(2000)
            
        if not csrf_token:
            print("에러: CSRF 토큰을 획득할 수 없습니다.")
            browser.close()
            return
            
        print(f"CSRF 토큰 확보 완료: {csrf_token}")
        
        current_page = 1
        total_pages = 1 # 임시값, 첫 응답에서 갱신
        
        while current_page <= total_pages:
            print(f"[{current_page}/{total_pages}] 페이지 데이터 수집 중...")
            
            payload = {
                "productCategory": "CATEGORY_018",
                "destination": "D-KR-120",
                "keyword": "",
                "filters": {},
                "sort": "prec",
                "page": current_page,
                "count": 10
            }
            
            # 네트워크 부담을 줄이기 위해 0.1~1초 랜덤 대기
            time.sleep(random.uniform(0.1, 1.0))
            
            # API 직접 호출
            response = context.request.post(
                "https://www.kkday.com/api/_nuxt/category/get-search-products",
                headers={
                    "x-csrf-token": csrf_token,
                    "referer": f"https://www.kkday.com/ko/category/kr-south-korea/experiences/list?currency=KRW&sort=prec&page={current_page}&count=10",
                    "accept": "application/json, text/plain, */*",
                    "content-type": "application/json"
                },
                data=payload
            )
            
            if response.status != 200:
                print(f"API 요청 실패: {response.status}")
                print(response.text())
                break
                
            data = response.json()
            
            # KKDay API 응답 구조 확인 (products가 바로 있거나 data.products에 있을 수 있음)
            if "products" in data:
                products = data["products"]
                total_items = data.get("total", 0)
            elif "data" in data and "products" in data["data"]:
                products = data["data"]["products"]
                total_items = data["data"].get("total", 0)
            else:
                print("데이터를 찾을 수 없습니다.")
                print(data)
                break
                
            if not products:
                print("수집할 상품이 없습니다.")
                break
                
            # total page 갱신
            if total_items > 0:
                total_pages = (total_items + 9) // 10
            
            # 데이터 파싱 및 저장
            for p_info in products:
                p_id = str(p_info.get("prod_oid") or p_info.get("prod_mid", ""))
                title = p_info.get("name", "")
                duration = str(p_info.get("duration", ""))
                rating = float(p_info.get("rating_star", 0.0) or 0.0)
                reviews = int(p_info.get("rating_count", 0) or 0)
                # 금액 정보를 추출
                price = float(p_info.get("min_price", 0.0) or 0.0)
                
                # 타이틀 기반 지역명 추출
                region = extract_region(title, p_id)
                
                raw_data_str = json.dumps(p_info, ensure_ascii=False)
                
                upsert_experience(conn, (
                    p_id, title, duration, rating, reviews, price, current_page, region, raw_data_str
                ))
            
            print(f"{current_page}페이지 수집 완료 ({len(products)}개 상품 저장)")
            current_page += 1
            
        browser.close()
    conn.close()
    print("모든 수집이 완료되었습니다.")

if __name__ == "__main__":
    run()
