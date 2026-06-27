"""
이 모듈은 GetYourGuide에서 대한민국 관련 여행 상품 데이터를 스크래핑하여 저장하는 기능을 수행합니다.
주요 기능:
- 페이지 단위로 상품 정보(제목, 소요시간, 평점, 리뷰수, 가격) 스크래핑
- 1페이지부터 10페이지까지 데이터 수집
- SQLite 데이터베이스 및 CSV 파일로 수집된 데이터 저장
- 요청 간 0.1~1.0초의 랜덤 대기 시간을 통한 네트워크 부담 완화
"""

import sqlite3
import csv
import time
import random
import os
from bs4 import BeautifulSoup
from curl_cffi import requests

headers = {
    'accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
    'accept-encoding': 'gzip, deflate, br, zstd',
    'accept-language': 'ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7',
    'cache-control': 'max-age=0',
    'cookie': 'visitor_id=RMDNSXRP7EF05O5GCJ60ER5MB1DDI3JK; cur=KRW; locale_code=ko-KR; par_sess=h=CD951&c=ga&v=&t=0&s=; locale_autoredirect_origin=www.getyourguide.com; locale_autoredirect_deviceLocale=ko-KR; session_id=20478360-79dd-44dd-984a-a1aa14366863; ab.storage.deviceId.32b57c7b-1181-4973-9f07-79cdd6d2c403=g%3Acc5ad653-1d71-4b24-a90b-98916d38bdd4%7Ce%3Aundefined%7Cc%3A1782540961851%7Cl%3A1782540961851; _gcl_aw=GCL.1782540962.Cj0KCQjwxvjRBhC2ARIsAI7KJa32shq59CPGUraB_LS31cvkCBauGahiYGMgUaqAMTb3_uQT84tDvMoaAjh1EALw_wcB; _gcl_gs=2.1.k1$i1782540958$u142448292; _gcl_au=1.1.1836976856.1782540962; __rtbh.ssgtm.aid=1kf2iG2fJmne6KpPgdY; _ga=GA1.1.1858673430.1782540962; crto_is_user_optout=false; crto_mapped_user_id=bxHOKl9NYkpIcWVYdmFkZ1JvVlNPaSUyQkc4ZkExY1ZUWmhKa1lCZEJqJTJCWEhBV21BS2tFZmJ1bGlsOWxnJTJGdk40SCUyQlplT00; _hjSession_318029=eyJpZCI6IjNmMmIyMjRjLTJiMzAtNDlhYS1hODE3LTViYTRlZWVkMTQ4ZCIsImMiOjE3ODI1NDA5NjI3ODMsInMiOjAsInIiOjAsInNiIjowLCJzciI6MCwic2UiOjAsImZzIjoxLCJzcCI6MX0=; _hjHasCachedUserAttributes=true; FPID=FPID2.2.oXG7S9Ty217qlvwYAPOUSpyy%2FFGGvB6YJk4VrI7QxGo%3D.1782540962; FPGCLAW=2.1.kCj0KCQjwxvjRBhC2ARIsAI7KJa32shq59CPGUraB_LS31cvkCBauGahiYGMgUaqAMTb3_uQT84tDvMoaAjh1EALw_wcB$i1782540963; FPGCLGS=2.1.k1$i1782540958$u142448292; FPAU=1.1.1836976856.1782540962; _fbp=fb.1.1782540962918.90912536826371640; _scid=7bad95a4-1212-4b1a-995d-4d26de36a000; FPLC=cVo3JqAygljxvi7vcYpGDBQxVCiqpy6ORyqaZUxCHcFYgJ2CntgtD0m8C8HEz9SWMER2fFRp3UnnwegZgo%2F4XgI4YyBt6OsUNGBlVjnM4yg%2FA8s0Fg%2F30SgO%2FveTew%3D%3D; cookieBannerClosed=1; _gtmeec=eyJzdCI6ImQ1NjQ3MDA1ZDMxZGNiYjY2ZmY1MzFjNWUwOTc1NDRhMDM1NThiYzUzOGI5YzY1ZWUyNTM5NTk0ODg2ZmZiYzAiLCJjb3VudHJ5IjoiZDU2NDcwMDVkMzFkY2JiNjZmZjUzMWM1ZTA5NzU0NGEwMzU1OGJjNTM4YjljNjVlZTI1Mzk1OTQ4ODZmZmJjMCIsImV4dGVybmFsX2lkIjoiNTdkOTdkYzUxYWUwOWFkZmZlZThkYmNmYWVlNTVmYWFmMmMxOGI4NWU1ZDlhODdiMjE5Zjk1Zjk1YWE1MzQyZiJ9; _hjSessionUser_318029=eyJpZCI6IjJkNGE1ZDk4LTljMjYtNWMwOS04M2UwLThkOTRmMDhiN2I2OSIsImNyZWF0ZWQiOjE3ODI1NDA5NjI3ODEsImV4aXN0aW5nIjp0cnVlfQ==; _hjSessionUser_1380923=eyJpZCI6ImYzYzRlYTZmLTVjMDYtNTA2ZS04OTk2LTU3NWU4OTcyYmY0MiIsImNyZWF0ZWQiOjE3ODI1NDM0MDkxOTcsImV4aXN0aW5nIjp0cnVlfQ==; forterToken=48afc1f8a3fd4643a07bb57ce51a106f_1782543408341__UDF43-m4_25ck_; tfeAppletName=locations; __cf_bm=ZFT.cRK4nUOCZUJRHVsBR_oeTC3Vc8KkJnTrE5J24Ik-1782546792.9525547-1.0.1.1-2g4JKXfMIF8_DlyIEd3YamCc1Rq_uLpdqlTQy2o4XQtqL.PrOhKNPtax98ew_YyvFK92_CrlVYCWWbg_nwNNZ2afeM7qjw.bXWvQQzg_l8Ju7gcx7UtwS14UT.jHDYTR; csrfToken=91a962c4d570c2df4120e2d27c40e09bcfff344bea68f97605cea1f5b9d58695; AP-VID=r7i1ktqogulxoradlrigrg74ruxdefij; visitor_last_seen_at=1782546803; __rtbh.aid=%7B%22eventType%22%3A%22aid%22%2C%22id%22%3A%221kf2iG2fJmne6KpPgdY%22%2C%22expiryDate%22%3A%222027-06-27T07%3A53%3A24.353Z%22%7D; __rtbh.lid=%7B%22eventType%22%3A%22lid%22%2C%22id%22%3A%22bkW3ufKcTlHd4IjzSeHY%22%2C%22expiryDate%22%3A%222027-06-27T07%3A53%3A24.354Z%22%7D; cto_bundle=ogD1il9SY0cwUW1ra2xrb0FHTzhmSzglMkJHU3dZSUlSZVNQb1dIRUdmQnF2eiUyQiUyQkNIZzJTdW9yQ3dyaW85VGt1QmZHeloyZ0h4SFNLbjgxc0ZqUXpUJTJCTlVRZE5kYkZEQ0toakh2UDUxZmx4T3NBa0Q3WUhvWEpIenVvbnFOdEtWRnk5RkhiUElpaWxFR1YzdHgzJTJGNFdzYjE4aFVBJTNEJTNE; session_pageview_count=16; _uetsid=ac85e8e071ef11f199eab1e078257fff|c8inp8|2|g79|1|2369; _uetvid=ac85fd1071ef11f1a13f636b794dbac9|84dqi6|1782546806059|22|1|bat.bing.com/p/insights/c/y; FPGSID=1.1782546805.1782546805.G-BJKL76S993.R8vly1EW_2HXQDRhAm5law; _ga_BJKL76S993=GS2.1.s1782540962$o1$g1$t1782546808$j57$l1$h1355843020; ab.storage.sessionId.32b57c7b-1181-4973-9f07-79cdd6d2c403=g%3A99294020-9ef9-4436-a841-e38f66d83035%7Ce%3A1782548615263%7Cc%3A1782540961844%7Cl%3A1782546815263; _dd_s=aid=721c7c21-5ffa-4268-bf68-ecad8b4adfda&logs=1&id=e88fd355-c006-4007-9b5a-78ab6a5e8e25&created=1782540960745&expire=1782547723106&rum=0',
    'priority': 'u=0, i',
    'sec-ch-ua': '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
    'sec-fetch-dest': 'document',
    'sec-fetch-mode': 'navigate',
    'sec-fetch-site': 'same-origin',
    'sec-fetch-user': '?1',
    'upgrade-insecure-requests': '1',
    'user-agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36'
}

def init_db(db_path):
    os.makedirs(os.path.dirname(db_path), exist_ok=True)
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute('''
        CREATE TABLE IF NOT EXISTS activities (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            title TEXT,
            duration TEXT,
            rating TEXT,
            reviews TEXT,
            price TEXT,
            page INTEGER
        )
    ''')
    conn.commit()
    return conn

def scrape_page(page, conn):
    url = f"https://www.getyourguide.com/ko-kr/south-korea-l169035?destinations=90389,166877,105124,105115,90654,7931&page={page}"
    try:
        response = requests.get(url, headers=headers, impersonate="chrome110")
        if response.status_code != 200:
            print(f"[Page {page}] Failed with status code {response.status_code}")
            return []
    except Exception as e:
        print(f"[Page {page}] Error: {e}")
        return []
    
    soup = BeautifulSoup(response.text, 'html.parser')
    cards = soup.select('div[id="vertical-card-body"]')
    if not cards:
        cards = soup.select('.vertical-layout.granular-layout-activity-card-body')
    
    results = []
    for card in cards:
        title_el = card.select_one('span[id$="-title"]')
        title = title_el.text.strip() if title_el else 'N/A'
        
        attr_el = card.select_one('span[id$="-attributes"]')
        duration = attr_el.text.strip() if attr_el else 'N/A'
        
        rating_el = card.select_one('span[id$="-one-star-review-text"]')
        rating = rating_el.text.strip() if rating_el else 'N/A'
        
        reviews_el = card.select_one('span[id$="-one-star-review-description"]')
        reviews = reviews_el.text.strip() if reviews_el else 'N/A'
        # reviews usually have () around them, let's remove them
        if reviews.startswith('(') and reviews.endswith(')'):
            reviews = reviews[1:-1]
        
        price_els = card.select('span[id$="-inline-price-text"] span')
        price = 'N/A'
        if price_els:
            for pel in price_els:
                if '₩' in pel.text or 'US$' in pel.text or 'price' in pel.get('class', []):
                    price = pel.text.strip()
            if price == 'N/A' and len(price_els) > 1:
                price = price_els[-1].text.strip()
                
        results.append((title, duration, rating, reviews, price, page))
        
    if results:
        cursor = conn.cursor()
        cursor.executemany('''
            INSERT INTO activities (title, duration, rating, reviews, price, page)
            VALUES (?, ?, ?, ?, ?, ?)
        ''', results)
        conn.commit()
        
    return results

def save_to_csv(csv_path, all_data):
    os.makedirs(os.path.dirname(csv_path), exist_ok=True)
    with open(csv_path, 'w', newline='', encoding='utf-8-sig') as f:
        writer = csv.writer(f)
        writer.writerow(['Title', 'Duration', 'Rating', 'Reviews', 'Price', 'Page'])
        writer.writerows(all_data)

def main():
    db_path = os.path.join('getyourguide', 'data', 'getyourguide.db')
    csv_path = os.path.join('getyourguide', 'data', 'getyourguide.csv')
    
    # DB 초기화 시 기존 파일이 있다면 삭제 (또는 덮어쓰기 위해)
    if os.path.exists(db_path):
        os.remove(db_path)
        
    conn = init_db(db_path)
    all_data = []
    
    # cp949 인코딩 에러 방지를 위해 ascii 문자만 출력되도록 처리 (명령 프롬프트 환경 고려)
    print("스크래핑을 시작합니다... (1~10페이지)")
    
    for page in range(1, 11):
        print(f"{page}페이지 수집 중...")
        page_data = scrape_page(page, conn)
        all_data.extend(page_data)
        print(f" -> {len(page_data)}개 수집 완료")
        
        if page < 10:
            delay = random.uniform(0.1, 1.0)
            time.sleep(delay)
            
    conn.close()
    
    save_to_csv(csv_path, all_data)
    
    print("\\n=== 수집 리포트 ===")
    print(f"총 수집된 상품 수: {len(all_data)}")
    print(f"DB 저장 경로: {db_path}")
    print(f"CSV 저장 경로: {csv_path}")

if __name__ == "__main__":
    main()
