"""
이 모듈은 iHerb의 스포츠 카테고리(sports) 페이지를 크롤링하여 상품 데이터를 수집합니다.
주요 기능:
- Chrome DevTools Protocol 기반 도구(Playwright)를 사용하여 실제 브라우저처럼 동작하게 하여 403 차단 우회
- 메인 페이지를 먼저 접속하여 쿠키/세션을 획득한 후 Ajax 엔드포인트 호출
- BeautifulSoup을 이용해 HTML에서 상품 정보 추출
- 1페이지부터 10페이지까지 순회하며 데이터를 SQLite DB에 저장 (매 페이지마다 commit)
"""

from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from bs4 import BeautifulSoup
import sqlite3
import os
import time

def init_db(db_path):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS sports_products (
            product_id TEXT PRIMARY KEY,
            name TEXT,
            url TEXT,
            image_url TEXT,
            price REAL,
            rating TEXT,
            recent_sales TEXT,
            page INTEGER
        )
    ''')
    conn.commit()
    return conn

def extract_product_info(product_div, page):
    try:
        a_tag = product_div.select_one('a.absolute-link.product-link')
        if not a_tag:
            return None
            
        product_id = a_tag.get('data-product-id', '')
        name = a_tag.get('title', '')
        url = a_tag.get('href', '')
        
        img_tag = product_div.select_one('img')
        image_url = img_tag.get('src', '') if img_tag else ''
        
        meta_price = product_div.select_one('meta[itemprop="price"]')
        price = meta_price.get('content', 0.0) if meta_price else 0.0
        
        stars_a = product_div.select_one('a.stars')
        rating = stars_a.get('title', '') if stars_a else ''
        
        sales_div = product_div.select_one('div.recent-activity-message-wrapper')
        recent_sales = sales_div.get_text(strip=True) if sales_div else ''
        
        return (product_id, name, url, image_url, float(price), rating, recent_sales, page)
    except Exception as e:
        print(f"Error parsing product: {e}")
        return None

def scrape_iherb_sports_products():
    db_path = os.path.join(os.path.dirname(__file__), "..", "data", "sports_products.db")
    conn = init_db(db_path)
    cursor = conn.cursor()
    
    base_url = "https://kr.iherb.com/c/sports?p={}&isAjax=true"
    
    headers = {
        "priority": "u=1, i",
        "referer": "https://kr.iherb.com/c/sports",
        "sec-ch-ua": '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "x-requested-with": "XMLHttpRequest",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
    }

    total_inserted = 0

    with sync_playwright() as p:
        # headless=False 로 설정하여 봇 차단을 회피할 확률을 높임
        browser = p.chromium.launch(headless=False)
        context = browser.new_context(
            user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36"
        )
        page_obj = context.new_page()
        Stealth().apply_stealth_sync(page_obj)
        
        print("Visiting main page to pass Cloudflare/bot protections...")
        page_obj.goto("https://kr.iherb.com/c/sports", wait_until="domcontentloaded")
        page_obj.wait_for_timeout(5000) # 5초 대기하며 쿠키 설정 및 JS 챌린지 수행
        
        for page in range(1, 11):
            url = base_url.format(page)
            print(f"Requesting URL: {url}")
            
            try:
                # 브라우저 컨텍스트 내에서 직접 fetch 를 실행하여 봇 탐지를 회피
                html_content = page_obj.evaluate(f'''
                    async () => {{
                        const response = await fetch("{url}", {{
                            headers: {{
                                "x-requested-with": "XMLHttpRequest",
                                "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8"
                            }}
                        }});
                        if (response.status !== 200) {{
                            return "STATUS:" + response.status;
                        }}
                        return await response.text();
                    }}
                ''')
            except Exception as e:
                print(f"Request failed: {e}")
                break
                
            if not str(html_content).startswith("STATUS:"):
                soup = BeautifulSoup(html_content, 'html.parser')
                
                product_divs = soup.select('div.product-inner')
                if not product_divs:
                    print(f"Page {page}: No products found in HTML. Stopping.")
                    break
                    
                print(f"Page {page}: Found {len(product_divs)} products.")
                
                page_data = []
                for div in product_divs:
                    info = extract_product_info(div, page)
                    if info and info[0]:
                        page_data.append(info)
                
                cursor.executemany('''
                    INSERT OR REPLACE INTO sports_products 
                    (product_id, name, url, image_url, price, rating, recent_sales, page)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                ''', page_data)
                conn.commit()
                
                total_inserted += len(page_data)
                print(f"Page {page} successfully saved to DB.")
                
                page_obj.wait_for_timeout(2000) # 2초 대기
            else:
                print(f"Failed to fetch data at page {page}. {html_content}")
                break
                
        browser.close()

    conn.close()
    print(f"\nSuccessfully saved {total_inserted} total products to {os.path.abspath(db_path)}")

if __name__ == "__main__":
    scrape_iherb_sports_products()
