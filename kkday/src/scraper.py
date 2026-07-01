"""
이 모듈은 kkday API를 호출하여 전체 페이지의 상품 목록을 추출하고 CSV 파일로 저장하는 기능을 수행합니다.
주요 기능:
- kkday API 반복 호출 (1페이지부터 마지막 페이지까지)
- id, title, duration, rating, reviews, price, page, region 데이터 추출
- 금액 정보를 KRW(원) 단위로 변환
- 상품 제목(title)을 한국어로 번역 (deep-translator 활용)
- 추출된 데이터를 csv 파일로 저장
"""

import requests
import json
import csv
import os
import time
from deep_translator import GoogleTranslator

def get_exchange_rate(base="TWD", target="KRW"):
    """환율 정보를 가져옵니다. 기본적으로 TWD에서 KRW로 변환합니다."""
    try:
        url = f"https://api.exchangerate-api.com/v4/latest/{base}"
        response = requests.get(url, timeout=10)
        if response.status_code == 200:
            data = response.json()
            return data.get("rates", {}).get(target, 42.0)
    except Exception as e:
        print(f"환율 정보를 가져오는데 실패했습니다: {e}")
    return 42.0

def main():
    url = "https://www.kkday.com/api/_nuxt/category/get-search-products"
    csrf_token = "410730b3-5977-4246-8966-fec4214f0a5a"

    headers = {
        "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
        "referer": "https://www.kkday.com/ko/category/kr-south-korea/experiences/list?currency=KRW",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "x-csrf-token": csrf_token,
        "content-type": "application/json"
    }

    cookies = {
        "csrf_token": csrf_token
    }

    # 번역기 초기화
    translator = GoogleTranslator(source='auto', target='ko')

    current_page = 1
    total_pages = 1
    exchange_rate = None
    results = []

    print("전체 페이지 데이터 수집을 시작합니다...")

    while current_page <= total_pages:
        payload = {
            "productCategory": "CATEGORY_018",
            "destination": "D-KR-120",
            "keyword": "",
            "filters": {},
            "sort": "prec",
            "page": current_page,
            "count": 10
        }

        try:
            response = requests.post(url, headers=headers, cookies=cookies, json=payload, timeout=10)
        except Exception as e:
            print(f"[{current_page}페이지] 요청 에러: {e}")
            break

        if response.status_code != 200:
            print(f"[{current_page}페이지] API 호출 실패 (상태 코드: {response.status_code})")
            break

        data = response.json()
        
        if current_page == 1:
            total_pages = data.get("totalPages", 1)
            print(f"총 페이지 수: {total_pages}")
            
        products = data.get("products", [])
        if not products:
            break

        # 첫 페이지에서 환율 한 번만 가져오기
        if exchange_rate is None and products:
            base_currency = products[0].get("currency", "TWD")
            if base_currency != "KRW":
                exchange_rate = get_exchange_rate(base_currency, "KRW")
                print(f"환율 적용: 1 {base_currency} = {exchange_rate} KRW")
            else:
                exchange_rate = 1.0

        print(f"[{current_page}/{total_pages}페이지] {len(products)}개 상품 처리 중...")

        for p in products:
            prod_id = p.get("prod_oid") or p.get("prod_mid", "")
            original_title = p.get("name", "")
            
            # 제목 한국어 번역
            translated_title = original_title
            if original_title:
                try:
                    translated_title = translator.translate(original_title)
                except Exception as e:
                    print(f"  - 번역 실패 ({prod_id}): {e}")

            duration = p.get("duration", "")
            rating = p.get("rating_star", 0.0)
            reviews = p.get("rating_count", 0)
            
            # 가격 변환
            min_price = p.get("min_price", 0)
            price_krw = round(min_price * (exchange_rate or 1.0))
            
            destinations = p.get("destinations", [])
            region = destinations[0].get("name", "") if destinations else ""

            results.append({
                "id": prod_id,
                "title": translated_title,
                "duration": duration,
                "rating": rating,
                "reviews": reviews,
                "price": price_krw,
                "page": current_page,
                "region": region
            })
            
        current_page += 1
        time.sleep(1)  # 서버 부하 방지용 딜레이

    # CSV 파일 저장
    output_dir = os.path.join(os.path.dirname(__file__), "..", "data")
    os.makedirs(output_dir, exist_ok=True)
    output_file = os.path.join(output_dir, "kkday_products.csv")

    if results:
        fieldnames = ["id", "title", "duration", "rating", "reviews", "price", "page", "region"]
        with open(output_file, "w", encoding="utf-8-sig", newline="") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames)
            writer.writeheader()
            writer.writerows(results)
        print(f"데이터 수집 완료: 총 {len(results)}개 상품 저장됨 -> {output_file}")
    else:
        print("저장할 데이터가 없습니다.")

if __name__ == "__main__":
    main()
