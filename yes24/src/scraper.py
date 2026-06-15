"""
이 모듈은 YES24의 베스트셀러 도서 목록을 스크래핑하여 CSV 파일로 저장하는 스크립트입니다.
주요 기능:
- 베스트셀러 페이지 목록 순회
- 각 페이지의 도서 정보(상품번호, 상품명, 저자, 출판사, 가격 등) 추출
- 수집된 데이터를 CSV 파일로 저장
"""

import requests
from bs4 import BeautifulSoup
import pandas as pd
import time
import os

def scrape_page(page_number):
    url = "https://www.yes24.com/product/category/BestSellerContents"
    
    params = {
        "categoryNumber": "001001003",
        "sumGb": "06",
        "sex": "A",
        "age": "255",
        "goodsTp": "0",
        "addOptionTp": "0",
        "excludeTp": "2",
        "pageNumber": str(page_number),
        "pageSize": "24",
        "goodsStatGb": "06",
        "eBookTp": "0",
        "bestType": "YES24_BESTSELLER",
        "type": "",
        "saleYear": "0",
        "saleMonth": "0",
        "weekNo": "0",
        "saleDts": "",
        "viewMode": "",
        "freeYn": ""
    }
    
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36"
    }
    
    response = requests.get(url, params=params, headers=headers)
    response.raise_for_status()
    
    soup = BeautifulSoup(response.text, 'html.parser')
    items = soup.find_all('li', {'data-goods-no': True})
    
    data = []
    for item in items:
        goods_no = item.get('data-goods-no', '')
        
        # 상품명
        title_elem = item.select_one('a.gd_name')
        title = title_elem.text.strip() if title_elem else ''
        
        # 부제 (Sub title)
        subtitle_elem = item.select_one('span.gd_nameE')
        subtitle = subtitle_elem.text.strip() if subtitle_elem else ''
        
        # 저자
        author_elem = item.select_one('span.info_auth a')
        if not author_elem:
            author_elem = item.select_one('span.info_auth')
        author = author_elem.text.strip() if author_elem else ''
        
        # 출판사
        pub_elem = item.select_one('span.info_pub a')
        if not pub_elem:
            pub_elem = item.select_one('span.info_pub')
        pub = pub_elem.text.strip() if pub_elem else ''
        
        # 출간일
        date_elem = item.select_one('span.info_date')
        pub_date = date_elem.text.strip() if date_elem else ''
        
        # 할인가
        sale_price_elem = item.select_one('strong.txt_num em.yes_b')
        sale_price = sale_price_elem.text.strip() if sale_price_elem else ''
        
        # 정가
        orig_price_elem = item.select_one('span.txt_num.dash em.yes_m')
        orig_price = orig_price_elem.text.strip() if orig_price_elem else ''
        
        # 판매지수
        sale_num_elem = item.select_one('span.saleNum')
        sale_index = sale_num_elem.text.strip().replace('판매지수', '').strip() if sale_num_elem else ''
        
        # 회원리뷰 수
        review_count_elem = item.select_one('span.rating_rvCount em.txC_blue')
        review_count = review_count_elem.text.strip() if review_count_elem else '0'
        
        # 리뷰 총점
        rating_elem = item.select_one('span.rating_grade em.yes_b')
        rating = rating_elem.text.strip() if rating_elem else ''
        
        # 태그
        tags = []
        tag_elems = item.select('span.tag a')
        for t in tag_elems:
            tags.append(t.text.strip())
        tags_str = ', '.join(tags)
        
        data.append({
            '상품번호': goods_no,
            '상품명': title,
            '부제': subtitle,
            '저자': author,
            '출판사': pub,
            '출간일': pub_date,
            '할인가': sale_price,
            '정가': orig_price,
            '판매지수': sale_index,
            '리뷰수': review_count,
            '평점': rating,
            '태그': tags_str
        })
        
    return data

def main():
    all_data = []
    page = 1
    
    print(f"[{page}페이지] 수집 테스트 중...")
    page_data = scrape_page(page)
    
    if not page_data:
        print("첫 페이지 수집 실패 또는 데이터가 없습니다.")
        return
        
    print(f"첫 페이지 성공: {len(page_data)}개 상품 수집됨.")
    all_data.extend(page_data)
    
    # 계속해서 나머지 페이지 수집
    while True:
        page += 1
        print(f"[{page}페이지] 수집 중...")
        try:
            page_data = scrape_page(page)
            if not page_data:
                print(f"{page}페이지에 더 이상 데이터가 없습니다. 수집 종료.")
                break
            
            all_data.extend(page_data)
            time.sleep(1) # 서버 부하 방지
        except Exception as e:
            print(f"오류 발생 ({page}페이지): {e}")
            break
            
    df = pd.DataFrame(all_data)
    
    # 폴더가 없으면 생성
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_dir = os.path.join(base_dir, 'data')
    os.makedirs(data_dir, exist_ok=True)
    save_path = os.path.join(data_dir, 'yes24_bestseller.csv')
    df.to_csv(save_path, index=False, encoding='utf-8-sig')
    print(f"\n총 {len(df)}개의 데이터 수집 완료. '{save_path}'에 저장되었습니다.")

if __name__ == "__main__":
    main()
