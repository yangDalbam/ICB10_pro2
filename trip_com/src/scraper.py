"""
이 모듈은 Scrapling과 Playwright를 사용하여 Trip.com 호텔 리뷰의 첫 페이지 데이터를 수집합니다.
주요 기능:
- 브라우저를 띄워(headless=False) 봇 방지 또는 로그인 요구 시 사용자가 수동 개입 가능
- 페이지 내의 __NEXT_DATA__ (JSON) 영역을 파싱하여 리뷰 데이터를 추출
- 수집된 제목, 내용, 별점 데이터를 CSV 파일로 저장
"""

import json
import re
import os
import time
import pandas as pd
from playwright.sync_api import sync_playwright
from playwright_stealth import Stealth
from scrapling import Selector

URL = "https://kr.trip.com/hotels/detail/?cityEnName=Seoul&cityId=274&hotelId=58635410&checkIn=2026-06-22&checkOut=2026-06-23&adult=2&children=0&crn=1&ages=&curr=KRW&barcurr=KRW&hoteluniquekey=H4sIAAAAAAAA_-M6wcTFJMEkdZCJo3XuntdsQoxGBiv5La5mOR7-qhHTX1Tg4Nn6OnCHnGSRQwBPIQMYuDjMYJz08pf0RkbNmP5DXzOsHHYwMp1gbGtmWcD050OzwykWZo6XepdYDjFGVytlp1YqWZnoKJVkluSkKlkpvd7W8GoDCL3ZOeNNyw4lHaWU1OJkoASQlZibX5pXAmSbWloa6xkYAIVKEis8U8AGJCfmJJfmJJakhlQWAA0y01HKLHYuKcosCErNzSwpSQWqSkvMKU4FiQelFgNlksGCSn5AY4qgApn5eRDtBihiYYk5pakQNwAtdEuF2mFYG_uIhSk69hMLwy-gn1a5NrEydLEyTGJl4QB6dhcrR4iRc6CHka7hBdYNJ1ikFA0NDAyMTE2NzHUNEi0Tk40NknRNLE0NjE11DY1NDQ0szDR65y7_8c7YSPYUo5ShuamJpYWpubG5oaWhnqWFuXmeYXBOkkdOiQdjEJuloYWbi1uUDRezd1C4YMam-nlsPEX2UiCeIoynBeIZwniBsjtV9sYFuNpHwkSSWLPzdb2DMlaKFjA2MDJ1MXILMHowRjBWAHmMqxgZNjAy7mD8DwOMrxhB5gEA1rgozBECAAA&masterhotelid_tracelogid=100025527-0a9ac30b-495035-1351086&detailFilters=17%7C1%7E17%7E1*80%7C2%7C1%7E80%7E2*29%7C1%7E29%7E1%7C2&hotelType=normal&display=incavg&subStamp=714&isCT=true&isFlexible=F&locale=ko-KR"

def extract_reviews_from_json(next_data):
    """
    Trip.com의 __NEXT_DATA__ JSON에서 리뷰(제목, 내용, 평점)를 추출합니다.
    """
    reviews = []
    # 데이터 구조 탐색 (트립닷컴의 내부 구조에 따라 달라질 수 있음)
    # 보통 props -> pageProps -> initialState 내에 존재
    try:
        # 안전한 탐색을 위해 재귀 함수로 리뷰 리스트로 추정되는 객체를 찾습니다.
        def find_review_list(obj):
            if isinstance(obj, dict):
                for k, v in obj.items():
                    if k in ['reviewList', 'comments', 'reviewItems', 'hotelReviews']:
                        if isinstance(v, list) and len(v) > 0:
                            return v
                    res = find_review_list(v)
                    if res: return res
            elif isinstance(obj, list):
                for item in obj:
                    res = find_review_list(item)
                    if res: return res
            return None

        review_list = find_review_list(next_data)
        if review_list:
            for item in review_list:
                # 일반적인 키 값 시도
                title = item.get('title', '') or item.get('reviewTitle', '')
                content = item.get('content', '') or item.get('reviewContent', '')
                score = item.get('rating', '') or item.get('score', '') or item.get('ratingPoint', '')
                
                # HTML 태그 제거
                title = re.sub(r'<[^>]+>', '', str(title)).strip()
                content = re.sub(r'<[^>]+>', '', str(content)).strip()
                
                if content:
                    reviews.append({
                        "제목": title,
                        "내용": content,
                        "별점": str(score)
                    })
    except Exception as e:
        print(f"JSON 파싱 중 에러 발생: {e}")
        
    return reviews

def scrape_all_reviews():
    print("브라우저를 실행합니다 (봇 방지/로그인 요구 시 수동으로 우회해주세요)...")
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        context = browser.new_context(user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36")
        page = context.new_page()
        Stealth().apply_stealth_sync(page)
        page.goto(URL)
        
        print("페이지 로딩 중... (수동 개입이 필요할 수 있습니다)")
        time.sleep(10)
        
        all_reviews = {} # content를 키로 사용하여 중복 제거
        
        # 전체 리뷰 수집 루프 (스크롤 및 더보기 등)
        last_height = 0
        scroll_attempts = 0
        max_attempts = 30 # 최대 스크롤/수집 횟수
        
        print("전체 리뷰 수집을 시작합니다...")
        for i in range(max_attempts):
            html = page.content()
            response = Selector(html)
            
            # Scrapling을 이용한 추출
            review_elements = response.css('div.reviewCard, div.review-card, div[class*="review_item"], div[class*="reviewItem"]')
            if not review_elements:
                 review_elements = response.css('.comment-item, .review-container', adaptive=True)
                 
            new_count = 0
            for el in review_elements:
                title = el.css('h3, .review-title, div[class*="title"]').extract_first() or ""
                content_texts = el.css('p, .review-content, div[class*="content"], div[class*="text"]').xpath('.//text()').getall()
                content = " ".join(t.strip() for t in content_texts if t.strip())
                score = el.css('.score, .rating, span[class*="score"]').extract_first() or ""
                
                title = re.sub(r'<[^>]+>', '', title).strip()
                content = re.sub(r'<[^>]+>', '', content).strip()
                score = re.sub(r'<[^>]+>', '', score).strip()
                
                if content and content not in all_reviews:
                    all_reviews[content] = {
                        "제목": title,
                        "내용": content,
                        "별점": score
                    }
                    new_count += 1
            
            print(f"[{i+1}/{max_attempts}] 추출된 새로운 리뷰: {new_count}건 (누적: {len(all_reviews)}건)")
            
            # 페이지 스크롤 또는 다음 페이지 이동
            # "다음 페이지" 버튼 클릭 시도 (있는 경우)
            next_button_js = '''() => {
                var nextBtn = document.querySelector('button.btn-next, .pagination-next, li[class*="next"]');
                if (nextBtn && !nextBtn.disabled && nextBtn.style.display !== "none") {
                    nextBtn.click();
                    return true;
                }
                return false;
            }'''
            clicked_next = page.evaluate(next_button_js)
            
            if clicked_next:
                time.sleep(3) # 다음 페이지 로딩 대기
            else:
                # 다음 버튼이 없으면 스크롤 다운
                page.evaluate("window.scrollBy(0, 1500);")
                time.sleep(2)
                new_height = page.evaluate("document.body.scrollHeight")
                if new_height == last_height and new_count == 0:
                    scroll_attempts += 1
                    if scroll_attempts >= 3:
                        print("더 이상 새로운 리뷰가 로드되지 않아 수집을 종료합니다.")
                        break
                else:
                    scroll_attempts = 0
                last_height = new_height

        browser.close()
                
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)
    out_path = os.path.join(data_dir, "reviews_all.csv")
    
    reviews_list = list(all_reviews.values())
    if reviews_list:
        df = pd.DataFrame(reviews_list)
        df.to_csv(out_path, index=False, encoding='utf-8-sig')
        print(f"성공: 전체 리뷰 {len(reviews_list)}건을 수집하여 {out_path}에 저장했습니다.")
    else:
        print("경고: 추출된 리뷰 데이터가 없습니다.")

if __name__ == "__main__":
    scrape_all_reviews()
