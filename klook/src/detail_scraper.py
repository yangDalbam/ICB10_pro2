"""
이 모듈은 SQLite DB(klook_data.db)의 상품 목록에서 상위 10개 상품의 상세페이지(Deep Link)를 추출하고,
실제 브라우저의 요청처럼 위장하여 상세페이지 내부의 구조화된 데이터(LD-JSON)를 정밀하게 수집하는 기능을 수행합니다.
주요 기능:
- SQLite DB의 search_results 테이블에서 상위 10개 상품의 detail_link 조회
- curl_cffi 기반의 TLS/UA 위장(impersonate='chrome')을 통해 403 차단 우회 및 상세페이지 HTML 수집
- 수집한 HTML에서 application/ld+json 데이터를 파싱하여 상품 고유 SKU, 평점, 리뷰 수, 가격, 브랜드, 이미지 등 상세 데이터 추출
- 추출한 데이터를 별도의 테이블(detail_parsed_info)에 Upsert 방식으로 저장
- 상품 정보와 조인(JOIN)하여 결과를 출력 및 검증
"""

import json
import time
import random
import sqlite3
import traceback
from scrapling import Fetcher
from bs4 import BeautifulSoup

def create_parsed_table(conn):
    """
    상세페이지의 구조화된 데이터를 저장할 별도의 테이블을 생성합니다.
    """
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detail_parsed_info (
            detail_link TEXT PRIMARY KEY,
            sku TEXT,
            name TEXT,
            description TEXT,
            images TEXT,
            rating_value REAL,
            review_count INTEGER,
            price REAL,
            price_currency TEXT,
            brand TEXT,
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

def upsert_detail_parsed(conn, data):
    """
    상세페이지 수집 정보를 detail_parsed_info 테이블에 저장합니다.
    """
    cursor = conn.cursor()
    sql = '''
        INSERT INTO detail_parsed_info (
            detail_link, sku, name, description, images, 
            rating_value, review_count, price, price_currency, brand
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(detail_link) DO UPDATE SET
            sku=excluded.sku,
            name=excluded.name,
            description=excluded.description,
            images=excluded.images,
            rating_value=excluded.rating_value,
            review_count=excluded.review_count,
            price=excluded.price,
            price_currency=excluded.price_currency,
            brand=excluded.brand,
            extracted_at=CURRENT_TIMESTAMP
    '''
    cursor.execute(sql, data)
    conn.commit()

def main():
    db_path = "klook/data/klook_data.db"
    conn = sqlite3.connect(db_path)
    create_parsed_table(conn)
    
    # 1. search_results 테이블에서 상위 10개 상품의 detail_link 가져오기
    cursor = conn.cursor()
    cursor.execute("""
        SELECT detail_link, title, price 
        FROM search_results 
        WHERE detail_link IS NOT NULL AND detail_link != '' 
        LIMIT 10
    """)
    rows = cursor.fetchall()
    
    if not rows:
        print("수집할 상품 링크가 DB에 없습니다. 먼저 scraper.py를 실행해 주세요.")
        conn.close()
        return
        
    print(f"--- 상세페이지 정보 수집을 시작합니다 (대상: {len(rows)}개 상품) ---")
    
    fetcher = Fetcher()
    
    # 상세페이지 헤더 설정 (우회를 위해 referer 필수 지정)
    detail_headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "accept-language": "ko-KR,ko;q=0.9",
        "referer": "https://www.klook.com/ko/search/result/?query=%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD&search_scope=main_search"
    }
    
    for idx, (deep_link, list_title, list_price) in enumerate(rows, 1):
        print(f"\n[{idx}/10] 수집 중: {list_title} ({deep_link})")
        
        try:
            # 실제 브라우저 처럼 접근하기 위해 impersonate='chrome' 옵션 사용
            res = fetcher.get(deep_link, headers=detail_headers, impersonate='chrome')
            
            if res.status != 200:
                print(f"  접근 실패 (HTTP Status: {res.status})")
                continue
                
            soup = BeautifulSoup(res.body, 'html.parser')
            
            # LD-JSON 구조화된 데이터 추출
            scripts = soup.find_all('script', type='application/ld+json')
            ld_jsons = []
            for s in scripts:
                try:
                    ld_jsons.append(json.loads(s.text))
                except:
                    pass
            
            # Product 타입의 객체 찾기
            product_obj = None
            for item in ld_jsons:
                if isinstance(item, list):
                    for sub_item in item:
                        if isinstance(sub_item, dict) and sub_item.get("@type") == "Product":
                            product_obj = sub_item
                            break
                elif isinstance(item, dict):
                    if item.get("@type") == "Product":
                        product_obj = item
                        break
                if product_obj:
                    break
            
            if not product_obj:
                print("  LD-JSON에서 Product 정보를 찾을 수 없습니다. HTML 구조가 변경되었을 수 있습니다.")
                continue
                
            # 데이터 추출 및 가공
            sku = product_obj.get('sku') or product_obj.get('mpn', '')
            name = product_obj.get('name', list_title)
            description = product_obj.get('description', '')
            
            # 이미지 목록
            images_raw = product_obj.get('image', [])
            images_str = json.dumps(images_raw if isinstance(images_raw, list) else [images_raw], ensure_ascii=False)
            
            # 평점 및 리뷰 수
            rating_obj = product_obj.get('aggregateRating', {})
            rating_value = rating_obj.get('ratingValue')
            review_count = rating_obj.get('reviewCount')
            
            if rating_value is not None:
                rating_value = float(rating_value)
            if review_count is not None:
                review_count = int(review_count)
                
            # 가격 및 통화
            offer_obj = product_obj.get('offers', {})
            price_val = offer_obj.get('price')
            price_currency = offer_obj.get('priceCurrency', '')
            
            if price_val is not None:
                price_val = float(price_val)
                
            # 브랜드
            brand_obj = product_obj.get('brand', {})
            if isinstance(brand_obj, dict):
                brand = brand_obj.get('name', 'Klook')
            else:
                brand = str(brand_obj)
                
            # DB에 저장
            parsed_data = (
                deep_link, sku, name, description, images_str, 
                rating_value, review_count, price_val, price_currency, brand
            )
            upsert_detail_parsed(conn, parsed_data)
            print("  -> 상세 데이터 수집 완료 및 DB 저장 성공!")
            
        except Exception as e:
            print(f"  오류 발생: {e}")
            traceback.print_exc()
            
        # 1초 ~ 3초 딜레이
        time.sleep(random.uniform(1.0, 3.0))
        
    print("\n\n--- [검증] 상품 정보와 상세페이지 정보 조인(JOIN) 결과 (상위 10개) ---")
    cursor.execute("""
        SELECT 
            s.title as [검색 제목],
            s.price as [검색 가격],
            d.name as [상세 제목],
            d.price as [상세 가격],
            d.price_currency as [통화],
            d.rating_value as [평점],
            d.review_count as [리뷰수],
            d.brand as [브랜드]
        FROM search_results s
        JOIN detail_parsed_info d ON s.detail_link = d.detail_link
        LIMIT 10
    """)
    headers = [desc[0] for desc in cursor.description]
    join_rows = cursor.fetchall()
    
    # 간이 표(Table) 포맷으로 출력
    from tabulate import tabulate
    print(tabulate(join_rows, headers=headers, tablefmt="grid"))
    
    conn.close()
    print("\n상세페이지 정보 수집 프로세스가 모두 완료되었습니다.")

if __name__ == "__main__":
    main()
