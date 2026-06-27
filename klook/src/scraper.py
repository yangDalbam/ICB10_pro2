"""
이 모듈은 Klook API를 호출하여 검색 결과와 상세페이지 정보를 수집하고 SQLite DB에 저장하는 기능을 수행합니다.
주요 기능:
- Klook API HTTP GET 요청 (scrapling 라이브러리 사용)
- 검색 결과 목록(1~5페이지) 수집 및 주요 필드 추출
- 검색된 상품의 상세 페이지 정보 수집
- 0.1~1초 랜덤 딜레이 적용
- 중복 방지를 위한 SQLite DB 업데이트(Upsert) 저장
"""

import json
import time
import random
import sqlite3
import traceback
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse
from scrapling import Fetcher
from bs4 import BeautifulSoup

def get_url_for_page(base_url, page):
    parsed = urlparse(base_url)
    query_params = dict(parse_qsl(parsed.query))
    query_params['start'] = str(page)
    new_query = urlencode(query_params)
    return urlunparse(parsed._replace(query=new_query))

def create_tables(conn):
    cursor = conn.cursor()
    # 상품 목록 테이블
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
    # 상세페이지 정보 테이블
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detail_results (
            detail_link TEXT PRIMARY KEY,
            title TEXT,
            description TEXT,
            ld_json TEXT,
            raw_html_length INTEGER
        )
    ''')
    conn.commit()

def extract_general_tags(tags, keyword):
    if not tags:
        return 0
    for tag in tags:
        if keyword in str(tag.get('text', '')).lower() or keyword in str(tag.get('tagKey', '')).lower():
            return 1
    return 0

def upsert_search_results(conn, items):
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
    
    total_pages_to_collect = 5
    collected_links = []
    
    # 1. 목록 수집 (1~5 페이지)
    print("--- 1. 검색 결과 수집 시작 ---")
    for page in range(1, total_pages_to_collect + 1):
        url = get_url_for_page(base_url, page)
        print(f"Requesting page {page}...")
        
        try:
            response = fetcher.get(url, headers=headers)
            if response.status != 200:
                print(f"Failed to fetch page {page}. Status: {response.status}")
                break
                
            data = response.json()
            
            if data.get("success"):
                search_result = data.get("result", {}).get("search_result", {})
                cards = search_result.get("cards", [])
                
                if not cards:
                    print("더 이상 수집할 상품이 없습니다.")
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
                print(f"Page {page} 수집 완료: {len(db_items)} 건 업데이트됨.")
                
            else:
                print(f"API success=false 반환 (페이지 {page})")
                print(data.get("error"))
                break

        except Exception as e:
            print(f"오류 발생 (페이지 {page}): {e}")
            traceback.print_exc()
            break
            
        time.sleep(random.uniform(0.1, 1.0))
        
    print(f"\n--- 총 {len(collected_links)}개의 상품이 수집되었습니다. ---")
    
    # 2. 상세페이지 수집
    print("\n--- 2. 상세페이지 정보 수집 시작 ---")
    
    # 상세페이지용 기본 헤더 (Referer 헤더 필수 제공)
    detail_headers = {
        "accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8",
        "accept-language": "ko-KR,ko;q=0.9",
        "referer": "https://www.klook.com/ko/search/result/?query=%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD&search_scope=main_search"
    }

    for idx, deep_link in enumerate(collected_links, 1):
        if not deep_link.startswith('http'):
            continue
            
        print(f"[{idx}/{len(collected_links)}] 상세페이지 수집 중: {deep_link}")
        
        try:
            # impersonate='chrome' 옵션을 직접 부여하여 TLS 지문 우회 적용
            res = fetcher.get(deep_link, headers=detail_headers, impersonate='chrome')
            if res.status == 200:
                # res.text 대신 res.body를 사용하여 HTML 소스를 정상 파싱
                soup = BeautifulSoup(res.body, 'html.parser')
                
                page_title = soup.title.string if soup.title else ''
                meta_desc = soup.find('meta', attrs={'name': 'description'})
                # KeyError: 'content'를 예방하기 위해 .get() 메서드를 사용합니다.
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
                
                # 상세정보 저장 (Upsert)
                upsert_detail_results(conn, (deep_link, page_title, description, ld_json_str, len(res.body)))
            else:
                print(f"상세페이지 접근 실패: {res.status}")
                
        except Exception as e:
            print(f"상세페이지 수집 중 오류 발생: {e}")
            
        time.sleep(random.uniform(0.1, 1.0))

    conn.close()
    
    print("\n--- 결과 리포트 ---")
    print(f"수집 프로세스가 성공적으로 완료되었습니다.")
    print(f"DB 저장 경로: {db_path}")
    print("목록 및 상세페이지 데이터가 모두 DB에 저장되었습니다.")

if __name__ == "__main__":
    main()
