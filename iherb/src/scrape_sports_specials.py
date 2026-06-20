"""
이 모듈은 iHerb의 스포츠 카테고리 특가 상품(sports/specials) 데이터를 수집하는 기능을 수행합니다.
주요 기능:
- iHerb 카탈로그 API(https://catalog.app.iherb.com/...)에 GET 요청을 보내어 데이터 로드
- 전체 페이지(1페이지부터 마지막 페이지까지)의 상품 정보를 수집
- 수집된 'products' 데이터를 하나의 CSV 파일로 저장
"""
import requests
import pandas as pd
import json
import os
import time

def scrape_iherb_sports_specials():
    base_url = "https://catalog.app.iherb.com/category/sports/specials?isMobile=false&pageSize=18&page={}"
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/115.0.0.0 Safari/537.36",
        "Accept": "application/json, text/plain, */*",
        "Origin": "https://kr.iherb.com",
        "Referer": "https://kr.iherb.com/"
    }

    all_products = []
    page = 1
    
    while True:
        url = base_url.format(page)
        print(f"Requesting URL: {url}")
        
        try:
            response = requests.get(url, headers=headers)
        except requests.exceptions.RequestException as e:
            print(f"Request failed: {e}")
            break
            
        if response.status_code == 200:
            data = response.json()
            if 'products' in data and data['products']:
                products = data['products']
                print(f"Page {page}: Found {len(products)} products.")
                all_products.extend(products)
                page += 1
                time.sleep(1) # delay between requests to be polite
            else:
                print(f"Page {page}: No more products found. Stopping.")
                break
        else:
            print(f"Failed to fetch data at page {page}. Status code: {response.status_code}")
            print(response.text)
            break

    if all_products:
        df = pd.DataFrame(all_products)
        output_path = os.path.join(os.path.dirname(__file__), "..", "data", "sports_specials.csv")
        df.to_csv(output_path, index=False, encoding='utf-8-sig')
        print(f"\nSuccessfully saved {len(all_products)} total products to {os.path.abspath(output_path)}")
    else:
        print("No products were scraped.")

if __name__ == "__main__":
    scrape_iherb_sports_specials()
