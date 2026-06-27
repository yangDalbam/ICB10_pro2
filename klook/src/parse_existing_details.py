"""
이 모듈은 SQLite DB에 이미 수집된 상세페이지 raw 데이터(detail_results)를 읽어와 
구조화된 상세 정보(Product 정보)를 일괄 파싱하고, URL 기반으로 지역명(region)을 추출하여 
새로운 테이블(detail_parsed_info)에 저장하는 기능을 수행합니다.
주요 기능:
- detail_parsed_info 테이블에 'region' 컬럼 동적 추가 및 테이블 생성
- URL 슬러그에서 나타나는 지명 키워드를 매핑하여 한글 지역명 추출 (경기 용인, 인천, 대구 등)
- 기존 detail_results 내의 JSON-LD 데이터를 파싱하여 SKU, 가격, 평점, 리뷰 수, 이미지 목록 등 추출
- 추출 결과와 지역명 정보를 detail_parsed_info 테이블에 일괄 적재
- 상품 목록(search_results)과 조인하여 지역별 수집 현황 검증 출력
"""

import json
import re
import sqlite3
import traceback

def extract_location(url):
    """
    URL 슬러그 분석을 통해 마지막으로 검출되는 지명 키워드를 한글 지역명으로 매핑합니다.
    """
    if not url:
        return "기타"
        
    # URL에서 마지막 세그먼트 추출 (예: 96156-everland-ticket-gyeonggi-yongin)
    parsed_path = url.rstrip('/').split('/')[-1]
    # 앞에 숫자 ID 패턴 잘라내기
    slug = re.sub(r'^\d+-', '', parsed_path).lower()
    
    # 영어 지명 -> 한글 지역명 맵핑 딕셔너리
    location_map = {
        "gyeonggi-yongin": "경기 용인",
        "gyeonggi-do": "경기",
        "gyeonggi": "경기",
        "seoul": "서울",
        "incheon": "인천",
        "busan": "부산",
        "daegu": "대구",
        "daejeon": "대전",
        "yeosu": "전남 여수",
        "hanam": "경기 하남",
        "goyang": "경기 고양",
        "suwon": "경기 수원",
        "gyeongju": "경북 경주",
        "danyang": "충북 단양",
        "gangneung": "강원 강릉",
        "gapyeong": "경기 가평",
        "pohang": "경북 포항",
        "samcheok": "강원 삼척",
        "tongyeong": "경남 통영",
        "chungju": "충북 충주",
        "jeonju": "전북 전주",
        "andong": "경북 안동",
        "sokcho": "강원 속초",
        "gwanggyo": "경기 광교",
        "yeoju": "경기 여주",
        "jeongseon": "강원 정선",
        "ulsan": "울산",
        "chuncheon": "강원 춘천",
        "nami": "강원 춘천",
        "gwacheon": "경기 과천",
        "ilsan": "경기 일산",
        "cheonan": "충남 천안",
        "ulleung": "경북 울릉",
        "jeju": "제주",
        "gwangju": "경기 광주",
        "hwadam": "경기 광주",
        "yongpyong": "강원 평창",
        "high1": "강원 정선",
        "byeonsan": "전북 부안",
        "vivaldipark": "강원 홍천",
        "dmz": "경기/강원",
        "korea": "한국",
        "southkorea": "한국",
        "south-korea": "한국",
        "kr": "한국"
    }
    
    best_match = "전국/기타"
    last_idx = -1
    for key in location_map.keys():
        idx = slug.rfind(key)
        if idx != -1 and idx > last_idx:
            last_idx = idx
            best_match = location_map[key]
            
    return best_match

def setup_database(conn):
    """
    detail_parsed_info 테이블을 구성하고 region 컬럼이 없으면 동적으로 추가합니다.
    """
    cursor = conn.cursor()
    # 테이블 생성 (기본 region 컬럼 포함)
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
            region TEXT,
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()
    
    # 기존 테이블이 존재할 때 region 컬럼 유무 확인 후 ALTER
    cursor.execute("PRAGMA table_info(detail_parsed_info)")
    columns = [col[1] for col in cursor.fetchall()]
    if 'region' not in columns:
        print("detail_parsed_info 테이블에 'region' 컬럼을 추가합니다.")
        cursor.execute("ALTER TABLE detail_parsed_info ADD COLUMN region TEXT")
        conn.commit()

def upsert_detail_parsed_with_region(conn, data):
    """
    region 정보가 포함된 상세페이지 파싱 데이터를 detail_parsed_info 테이블에 Upsert 합니다.
    """
    cursor = conn.cursor()
    sql = '''
        INSERT INTO detail_parsed_info (
            detail_link, sku, name, description, images, 
            rating_value, review_count, price, price_currency, brand, region
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
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
            region=excluded.region,
            extracted_at=CURRENT_TIMESTAMP
    '''
    cursor.execute(sql, data)

def main():
    db_path = "klook/data/klook_data.db"
    conn = sqlite3.connect(db_path)
    setup_database(conn)
    
    # 1. detail_results에서 기존 수집 데이터 전체 조회
    cursor = conn.cursor()
    cursor.execute("SELECT detail_link, title, ld_json FROM detail_results")
    rows = cursor.fetchall()
    
    if not rows:
        print("파싱할 원본 상세데이터(detail_results)가 DB에 없습니다.")
        conn.close()
        return
        
    print(f"--- 기존 데이터 일괄 파싱 시작 (대상: {len(rows)}건) ---")
    
    parsed_count = 0
    for idx, (detail_link, title, ld_json_str) in enumerate(rows, 1):
        if not ld_json_str:
            continue
            
        try:
            ld_json = json.loads(ld_json_str)
            product_obj = None
            for item in ld_json:
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
                # Product 객체가 없다면 스킵
                continue
                
            # 데이터 추출
            sku = product_obj.get('sku') or product_obj.get('mpn', '')
            name = product_obj.get('name', title)
            description = product_obj.get('description', '')
            
            images_raw = product_obj.get('image', [])
            images_str = json.dumps(images_raw if isinstance(images_raw, list) else [images_raw], ensure_ascii=False)
            
            rating_obj = product_obj.get('aggregateRating', {})
            rating_value = rating_obj.get('ratingValue')
            review_count = rating_obj.get('reviewCount')
            if rating_value is not None:
                rating_value = float(rating_value)
            if review_count is not None:
                review_count = int(review_count)
                
            offer_obj = product_obj.get('offers', {})
            price_val = offer_obj.get('price')
            price_currency = offer_obj.get('priceCurrency', '')
            if price_val is not None:
                price_val = float(price_val)
                
            brand_obj = product_obj.get('brand', {})
            if isinstance(brand_obj, dict):
                brand = brand_obj.get('name', 'Klook')
            else:
                brand = str(brand_obj)
            
            # 2. 지역명 추출
            region = extract_location(detail_link)
            
            # Upsert
            upsert_detail_parsed_with_region(conn, (
                detail_link, sku, name, description, images_str,
                rating_value, review_count, price_val, price_currency, brand, region
            ))
            parsed_count += 1
            
        except Exception as e:
            print(f"[{idx}] 파싱 오류 발생 ({detail_link}): {e}")
            
    conn.commit()
    print(f"--- 일괄 파싱 완료: 총 {parsed_count}건의 상세 정보가 detail_parsed_info 테이블에 업데이트되었습니다. ---")
    
    # 3. 조인 결과 및 지역별 통계 출력 검증
    print("\n\n=== [검증] 지역명이 적용된 상품 목록과 상세 정보 조인 결과 (상위 15개) ===")
    cursor.execute("""
        SELECT 
            s.title as [상품명],
            d.region as [지역명],
            d.price as [원화가격],
            d.rating_value as [평점],
            d.review_count as [리뷰수]
        FROM search_results s
        JOIN detail_parsed_info d ON s.detail_link = d.detail_link
        LIMIT 15
    """)
    headers = [desc[0] for desc in cursor.description]
    join_rows = cursor.fetchall()
    
    from tabulate import tabulate
    print(tabulate(join_rows, headers=headers, tablefmt="grid"))
    
    print("\n\n=== [통계] 지역별 수집된 상품 건수 ===")
    cursor.execute("""
        SELECT region as [지역명], COUNT(*) as [상품 건수]
        FROM detail_parsed_info
        GROUP BY region
        ORDER BY [상품 건수] DESC
    """)
    stat_headers = [desc[0] for desc in cursor.description]
    stat_rows = cursor.fetchall()
    print(tabulate(stat_rows, headers=stat_headers, tablefmt="grid"))
    
    conn.close()

if __name__ == "__main__":
    main()
