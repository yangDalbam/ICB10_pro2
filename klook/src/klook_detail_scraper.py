"""
Klook 상품 상세 페이지 정보 수집 스크립트

주요 기능:
- klook_data.db에서 상위 10개 상품의 URL을 추출
- DrissionPage를 이용하여 실제 브라우저처럼 접근하여 상세 정보 스크래핑
- 수집된 정보를 detail_results 테이블에 저장
"""

import sqlite3
import time
import json
import sys
import os

# cp949 인코딩 에러 방지
if sys.stdout.encoding.lower() != 'utf-8':
    sys.stdout.reconfigure(encoding='utf-8')

from DrissionPage import ChromiumPage, ChromiumOptions

DB_PATH = 'C:/Users/user1/Downloads/ICB10_proj2/klook/data/klook_data.db'

def setup_db(conn):
    """detail_results 테이블을 생성합니다."""
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS detail_results (
            object_id TEXT PRIMARY KEY,
            url TEXT,
            detail_title TEXT,
            description TEXT,
            package_options TEXT,
            price_info TEXT,
            location_info TEXT,
            extracted_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
        )
    ''')
    conn.commit()

def fetch_targets(conn, limit=10):
    """수집 대상 URL을 가져옵니다. (이미 수집된 건 제외)"""
    cursor = conn.cursor()
    cursor.execute('''
        SELECT `track_info.object_id`, `data.deep_link` 
        FROM search_results 
        WHERE `track_info.object_id` NOT IN (SELECT object_id FROM detail_results WHERE location_info IS NOT NULL AND location_info != '')
        LIMIT ?
    ''', (limit,))
    return cursor.fetchall()

def scrape_detail_page(page, url):
    """단일 상세 페이지에서 정보를 수집합니다."""
    print(f"접근 중: {url}", flush=True)
    page.get(url)
    time.sleep(4) # 로딩 및 봇 방어 대기
    
    # 봇 차단 페이지인지 확인
    if "Just a moment..." in page.title or "klook.com" == page.title:
        print("봇 차단 페이지(Cloudflare 등) 감지됨. 5초 추가 대기...", flush=True)
        time.sleep(5)
        
    result = {
        'detail_title': '',
        'description': '',
        'package_options': '',
        'price_info': '',
        'location_info': ''
    }
    
    try:
        # 제목 수집 (h1 태그)
        title_ele = page.ele('tag:h1', timeout=3)
        if title_ele:
            result['detail_title'] = title_ele.text
            
        # 설명 또는 본문 일부 수집
        # Klook은 보통 .activity-desc, .detail-desc 등의 클래스를 사용함
        # 특정 클래스가 없을 수 있으므로 전체 텍스트에서 일부를 가져오거나 특정 문단 선택
        desc_elements = page.eles('.detail-content') or page.eles('xpath://div[contains(@class, "desc")]')
        if desc_elements:
            result['description'] = "\\n".join([e.text for e in desc_elements if e.text])
        
        # 패키지 옵션 텍스트 수집 (간단히 텍스트만)
        pkg_elements = page.eles('.package-list') or page.eles('xpath://div[contains(@class, "package")]')
        if pkg_elements:
            result['package_options'] = "\\n".join([e.text for e in pkg_elements if e.text])
            
        # 가격 정보 수집 (가격 관련 클래스 탐색)
        price_elements = page.eles('.price') or page.eles('.selling-price') or page.eles('xpath://*[contains(text(), "₩") or contains(text(), "원")]')
        if price_elements:
            # 여러 가격이 있을 수 있으므로 상위 몇 개만 텍스트로 합침
            prices = [e.text for e in price_elements if e.text and any(c.isdigit() for c in e.text)]
            result['price_info'] = " | ".join(prices[:3]) if prices else ""

        # 지역 정보 수집 (주소, 위치 관련 요소 탐색)
        loc_elements = page.eles('.location') or page.eles('.address') or page.eles('xpath://*[contains(@class, "location")]')
        if loc_elements:
            locs = [e.text for e in loc_elements if e.text and len(e.text) < 50]
            if locs:
                # 위치 텍스트에서 지역명만 추출
                regions = ['경기 용인', '서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주', '하남', '춘천', '용인', '대한민국']
                for r in regions:
                    if r in locs[0]:
                        result['location_info'] = r
                        break
                
        # 제목에서도 지역명 추출 시도
        if not result['location_info'] and result['detail_title']:
            title_parts = result['detail_title'].split()
            if len(title_parts) >= 1:
                first_two_words = f"{title_parts[0]} {title_parts[1]}" if len(title_parts) >= 2 else title_parts[0]
                regions = ['경기 용인', '서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주', '하남', '춘천', '용인', '대한민국']
                for r in regions:
                    if r in first_two_words:
                        result['location_info'] = r
                        break
            
            # 특정 키워드가 있는 경우 대한민국으로 폴백
            if '티머니' in result['detail_title'] or 'eSIM' in result['detail_title'] or '유심' in result['detail_title']:
                result['location_info'] = '대한민국'
            
        # 만약 위의 방식으로 못찾았다면, 페이지 내 초기 상태 JS 변수 탐색 시도
        state_js = page.run_js("return window.__INITIAL_STATE__ ? JSON.stringify(window.__INITIAL_STATE__) : null;")
        if state_js:
            try:
                state_data = json.loads(state_js)
                # JSON 내에서 정보 찾기 (경로는 페이지 버전에 따라 다를 수 있음)
                # 여기서는 JS 객체 존재 여부만 기록
                result['description'] += "\\n(window.__INITIAL_STATE__ 데이터를 가져왔습니다.)"
            except Exception:
                pass

    except Exception as e:
        print(f"요소 파싱 중 오류 발생: {repr(e)}")
        
    return result

def save_result(conn, object_id, url, data):
    """결과를 DB에 저장합니다."""
    cursor = conn.cursor()
    cursor.execute('''
        INSERT OR REPLACE INTO detail_results (object_id, url, detail_title, description, package_options, price_info, location_info)
        VALUES (?, ?, ?, ?, ?, ?, ?)
    ''', (object_id, url, data['detail_title'], data['description'], data['package_options'], data['price_info'], data['location_info']))
    conn.commit()

def main():
    conn = sqlite3.connect(DB_PATH)
    setup_db(conn)
    targets = fetch_targets(conn, 10)
    
    if not targets:
        print("수집 대상이 없습니다.")
        conn.close()
        return

    # Klook 차단 우회를 위해 일반 모드로 실행 (Headless 해제)
    co = ChromiumOptions()
    co.headless(False) 
    co.set_argument('--no-sandbox')
    co.set_argument('--disable-blink-features=AutomationControlled')
    
    try:
        page = ChromiumPage(co)
    except Exception as e:
        print("브라우저 실행 실패:", e)
        conn.close()
        return
        
    for idx, (object_id, url) in enumerate(targets, 1):
        print(f"[{idx}/{len(targets)}] 수집 시작 (ID: {object_id})", flush=True)
        data = scrape_detail_page(page, url)
        print(f"수집 완료 - 제목: {data.get('detail_title')}", flush=True)
        save_result(conn, object_id, url, data)
        time.sleep(2) # 서버 부하 방지용 딜레이

    print("모든 수집이 완료되었습니다.", flush=True)
    page.quit()
    conn.close()

if __name__ == "__main__":
    main()
