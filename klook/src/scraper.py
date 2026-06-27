"""
이 모듈은 Klook API를 호출하여 전체 검색 결과와 상세페이지 정보를 수집하고 SQLite DB에 저장하는 기능을 수행합니다.
주요 기능:
- Klook 검색 API를 호출하여 전체 페이지(최대 1000개 상품) 목록 수집 및 search_results 테이블 저장
- 수집된 모든 상품의 상세페이지(deep_link)를 실제 브라우저 위장(impersonate='chrome', referer 설정) 방식으로 호출
- 상세페이지 HTML 파싱 및 LD-JSON에서 세부 구조화 데이터(SKU, 가격, 평점, 리뷰수, 브랜드, 이미지) 추출
- URL 분석을 통한 한글 지역명(region) 자동 매핑 및 추출
- 상세페이지 세부 데이터 및 원본 데이터를 각각 detail_parsed_info, detail_results 테이블에 저장
- 이미 수집된 상세페이지는 네트워크 요청을 스킵하고 이어서 수집하는 Resume(재개) 기능 지원
"""

import json
import time
import random
import re
import sqlite3
import math
import traceback
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from scrapling import Fetcher
from bs4 import BeautifulSoup

def get_url_for_page(base_url, page):
    """
    페이지 번호에 맞게 API URL의 start 매개변수를 조정합니다.
    """
    parsed = urlparse(base_url)
    query_params = dict(parse_qsl(parsed.query))
    # start = (page - 1) * size + 1
    size = int(query_params.get('size', 15))
    start_val = (page - 1) * size + 1
    query_params['start'] = str(start_val)
    new_query = urlencode(query_params)
    return urlunparse(parsed._replace(query=new_query))

def create_tables(conn):
    """
    데이터 저장에 필요한 테이블들을 생성합니다.
    """
    cursor = conn.cursor()
    # 1. 검색 결과 상품 목록 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS search_results (
            id TEXT PRIMARY KEY,
            title TEXT,
            price TEXT,
            detail_link TEXT,
            rating TEXT,
            review_count TEXT,
            purchase_count TEXT,
            free_cancellation INTEGER,
            instant_confirmation INTEGER,
            raw_json TEXT
        )
    ''')
    # 2. 상세페이지 원본 데이터 테이블 (백업/raw 보관용)
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detail_results (
            detail_link TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            ld_json TEXT,
            raw_html_length INTEGER
        )
    ''')
    # 3. 상세페이지 파싱 데이터 테이블 (구조화 및 지역명 정보 포함)
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

def extract_general_tags(tags, keyword):
    """
    태그 목록에서 특정 키워드가 포함되어 있는지 확인합니다.
    """
    if not tags:
        return 0
    for tag in tags:
        tag_text = str(tag.get('text', '')).lower()
        tag_key = str(tag.get('tagKey', '')).lower()
        if keyword in tag_text or keyword in tag_key:
            return 1
    return 0

def extract_location(url):
    """
    URL 슬러그 분석을 통해 마지막으로 검출되는 지명 키워드를 한글 지역명으로 매핑합니다.
    """
    if not url:
        return "기타"
    
    parsed_path = url.rstrip('/').split('/')[-1]
    slug = re.sub(r'^\d+-', '', parsed_path).lower()
    
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

def upsert_search_results(conn, items):
    """
    검색 결과 리스트 데이터를 search_results 테이블에 Upsert 합니다.
    """
    cursor = conn.cursor()
    sql = '''
        INSERT INTO search_results (
            id, title, price, detail_link, rating, review_count, 
            purchase_count, free_cancellation, instant_confirmation, raw_json
        )
        VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?, ?)
        ON CONFLICT(id) DO UPDATE SET
            title=excluded.title,
            price=excluded.price,
            detail_link=excluded.detail_link,
            rating=excluded.rating,
            review_count=excluded.review_count,
            purchase_count=excluded.purchase_count,
            free_cancellation=excluded.free_cancellation,
            instant_confirmation=excluded.instant_confirmation,
            raw_json=excluded.raw_json
    '''
    cursor.executemany(sql, items)
    conn.commit()

def upsert_detail_results(conn, item):
    """
    상세페이지 raw HTML 보관용 테이블에 Upsert 합니다.
    """
    cursor = conn.cursor()
    sql = '''
        INSERT INTO detail_results (
            detail_link, title, description, ld_json, raw_html_length
        )
        VALUES (?, ?, ?, ?, ?)
        ON CONFLICT(detail_link) DO UPDATE SET
            title=excluded.title,
            description=excluded.description,
            ld_json=excluded.ld_json,
            raw_html_length=excluded.raw_html_length
    '''
    cursor.execute(sql, item)
    conn.commit()

def upsert_detail_parsed_info(conn, item):
    """
    파싱된 상세 구조화 데이터와 지역명을 detail_parsed_info 테이블에 Upsert 합니다.
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
    cursor.execute(sql, item)
    conn.commit()

def main():
    base_url = "https://www.klook.com/v1/cardinfocenterservicesrv/search/platform/complete_search_v3?location=158%2C157%2C156%2C5031%2C8928%2C24975%2C28741%2C545%2C6166%2C6268%2C703649%2C703648%2C705582%2C6955%2C15088%2C701102%2C16467%2C707516%2C26374%2C7204%2C20296%2C28785%2C28972%2C8898%2C23546%2C30633%2C15378%2C16365%2C28742%2C10956%2C26961%2C10093%2C16560%2C25178%2C7741%2C11925%2C24865%2C25140%2C30570%2C7030%2C707332%2C7558%2C8989%2C10706%2C11364%2C11745%2C13523%2C14446%2C15281%2C15603%2C16655%2C18214%2C18323%2C20392%2C22390%2C22675%2C23237%2C24520%2C24762%2C25060%2C26454%2C27895%2C29136%2C29872%2C30051%2C30265%2C30376%2C30466%2C31247%2C705101%2C9079&sort=most_relevant&tab_key=0&start=1&query=%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD&size=15&search_scope=main_search&k_lang=ko_KR&k_currency=KRW"

    headers = {
        "accept": "application/json, text/plain, */*",
        "accept-language": "ko_KR",
        "priority": "u=1, i",
        "referer": "https://www.klook.com/ko/search/result/?query=%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD&search_scope=main_search",
        "sec-ch-ua": '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-platform": '"Windows"',
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "x-klook-host": "www.klook.com",
        "x-klook-market": "global",
        "x-klook-user-residence": "10_KR",
        "x-platform": "desktop",
        "x-requested-with": "XMLHttpRequest"
    }

    db_path = "klook/data/klook_data.db"
    conn = sqlite3.connect(db_path)
    create_tables(conn)
    
    fetcher = Fetcher()
    
    # 1. 1페이지를 먼저 호출하여 총 검색 개수(total) 파악 및 동적 페이지 수 계산
    print("--- 1. Klook 검색 목록 전체 수집 시작 ---")
    print("1페이지 호출 중...")
    try:
        res1 = fetcher.get(base_url, headers=headers)
        if res1.status != 200:
            print(f"API 호출 실패 (HTTP Status: {res1.status})")
            conn.close()
            return
            
        data1 = res1.json()
        if not data1.get("success"):
            print("API 응답 success=false")
            conn.close()
            return
            
        search_result = data1.get("result", {}).get("search_result", {})
        total_items = search_result.get("total", 0)
        print(f"검색어 '대한민국'에 대한 총 상품 수: {total_items}개")
        
        # 페이지 수 계산 (한 페이지당 size=15)
        total_pages_to_collect = math.ceil(total_items / 15)
        # Klook API 제한 및 봇 감지 고려해 최대 67페이지(약 1000개 상품)로 제한
        total_pages_to_collect = min(total_pages_to_collect, 67)
        print(f"수집할 총 페이지 수: {total_pages_to_collect} 페이지")
        
    except Exception as e:
        print(f"초기 페이지 분석 중 오류 발생: {e}")
        conn.close()
        return

    collected_links = []
    
    # 1페이지부터 순차적으로 수집 진행
    for page in range(1, total_pages_to_collect + 1):
        url = get_url_for_page(base_url, page)
        print(f"Requesting list page {page}/{total_pages_to_collect}...")
        
        try:
            # 1페이지는 위에서 가져왔으므로 재사용 가능하지만, 로직 단순화를 위해 재호출하거나 분기 처리
            if page == 1:
                data = data1
            else:
                response = fetcher.get(url, headers=headers)
                if response.status != 200:
                    print(f"Page {page} fetching failed. Status: {response.status}")
                    break
                data = response.json()
            
            if data.get("success"):
                search_result = data.get("result", {}).get("search_result", {})
                cards = search_result.get("cards", [])
                
                if not cards:
                    print("수집할 카드가 없습니다. 루프를 종료합니다.")
                    break
                
                db_items = []
                for card in cards:
                    cdata = card.get('data', {})
                    track_info = card.get('track_info', {})
                    
                    item_id = str(cdata.get('vertical_id', '')) + "_" + str(cdata.get('vertical_type', ''))
                    if not item_id or item_id == "_":
                        item_id = track_info.get('card_content_id', str(random.randint(1000000, 9999999)))
                        
                    title = cdata.get('title', '')
                    price_obj = cdata.get('price', {})
                    price = price_obj.get('selling_price') or price_obj.get('selling_price_format', '')
                    
                    deep_link = cdata.get('deep_link', '')
                    if deep_link and deep_link not in collected_links:
                        collected_links.append(deep_link)
                        
                    review_obj = cdata.get('review_obj', {})
                    rating = review_obj.get('star', '')
                    review_count = review_obj.get('number') or str(track_info.get('review_count', ''))
                    purchase_count = review_obj.get('booked') or str(track_info.get('product_participant_count', ''))
                    
                    general_tags = cdata.get('general_tag', [])
                    free_cancellation = extract_general_tags(general_tags, 'free cancellation') or extract_general_tags(general_tags, '무료 취소')
                    instant_confirmation = extract_general_tags(general_tags, 'instant confirm') or extract_general_tags(general_tags, '즉시 확정')
                    
                    raw_json = json.dumps(card, ensure_ascii=False)
                    
                    db_items.append((
                        item_id, title, price, deep_link, rating, review_count, 
                        purchase_count, free_cancellation, instant_confirmation, raw_json
                    ))
                
                upsert_search_results(conn, db_items)
                print(f"Page {page} 수집 완료: {len(db_items)} 건 데이터베이스 업데이트.")
                
            else:
                print(f"API success=false (Page {page})")
                break

        except Exception as e:
            print(f"오류 발생 (Page {page}): {e}")
            traceback.print_exc()
            break
            
        time.sleep(random.uniform(0.2, 0.8))
        
    print(f"\n--- 총 {len(collected_links)}개의 상품 상세링크가 수집되었습니다. ---")
    
    # 2. 상세페이지 수집 및 즉시 파싱 적재 (Resume 기능 탑재)
    print("\n--- 2. 상세페이지 세부 정보 수집 및 실시간 파싱 시작 ---")
    
    # 우회용 헤더
    detail_headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "accept-language": "ko-KR,ko;q=0.9",
        "referer": "https://www.klook.com/ko/search/result/?query=%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD&search_scope=main_search"
    }

    # 이미 수집 완료된 detail_link 리스트 조회 (중복 요청 최소화)
    cursor = conn.cursor()
    cursor.execute("SELECT detail_link FROM detail_parsed_info")
    already_parsed = {row[0] for row in cursor.fetchall()}
    print(f"이미 파싱 완료된 상품 수 (네트워크 요청 스킵 대상): {len(already_parsed)}개")

    skipped_count = 0
    success_count = 0
    failed_count = 0

    for idx, deep_link in enumerate(collected_links, 1):
        if not deep_link.startswith('http'):
            continue
            
        # Resume 기능: 이미 수집한 이력이 있는 상세링크는 스킵
        if deep_link in already_parsed:
            skipped_count += 1
            continue
            
        print(f"[{idx}/{len(collected_links)}] 수집 및 파싱 진행 중: {deep_link}")
        
        try:
            # impersonate='chrome'로 TLS 지문 우회 요청
            res = fetcher.get(deep_link, headers=detail_headers, impersonate='chrome')
            
            if res.status == 200:
                soup = BeautifulSoup(res.body, 'html.parser')
                
                page_title = soup.title.string if soup.title else ''
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                description = meta_desc.get('content', '') if meta_desc else ''
                
                # LD-JSON 구조화된 데이터 추출
                scripts = soup.find_all('script', type='application/ld+json')
                ld_jsons = []
                for s in scripts:
                    try:
                        ld_jsons.append(json.loads(s.text))
                    except:
                        pass
                
                ld_json_str = json.dumps(ld_jsons, ensure_ascii=False) if ld_jsons else ''
                
                # A. raw 백업 테이블에 저장
                upsert_detail_results(conn, (deep_link, page_title, description, ld_json_str, len(res.body)))
                
                # B. Product 구조화 데이터 파싱
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
                
                if product_obj:
                    sku = product_obj.get('sku') or product_obj.get('mpn', '')
                    name = product_obj.get('name', page_title)
                    desc_detail = product_obj.get('description', description)
                    
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
                else:
                    # Product 정보가 없을 시 리스트 메타 기반 기본값 구성
                    sku = ''
                    name = page_title
                    desc_detail = description
                    images_str = '[]'
                    rating_value = None
                    review_count = None
                    price_val = None
                    price_currency = ''
                    brand = 'Klook'
                
                # C. 지역명 추출
                region = extract_location(deep_link)
                
                # D. 구조화 테이블 적재
                upsert_detail_parsed_info(conn, (
                    deep_link, sku, name, desc_detail, images_str,
                    rating_value, review_count, price_val, price_currency, brand, region
                ))
                success_count += 1
            else:
                print(f"  접근 실패: HTTP Status {res.status}")
                failed_count += 1
                
        except Exception as e:
            print(f"  오류 발생: {e}")
            traceback.print_exc()
            failed_count += 1
            
        # 0.5초 ~ 1.5초 사이의 안전한 랜덤 딜레이
        time.sleep(random.uniform(0.5, 1.5))

    conn.close()
    
    print("\n--- 최종 결과 리포트 ---")
    print(f"목록 수집 대상 링크: {len(collected_links)}개")
    print(f"기 수집 스킵 건수(Resume): {skipped_count}개")
    print(f"신규 수집 성공 건수: {success_count}개")
    print(f"신규 수집 실패 건수: {failed_count}개")
    print(f"DB 저장 완료: {db_path}")
    print("전체 데이터 수집 및 파싱이 완료되었습니다.")

if __name__ == "__main__":
    main()
