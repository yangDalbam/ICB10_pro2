"""
이 모듈은 교보문고 온라인 베스트셀러 데이터를 전체 페이지에 걸쳐 수집하여 CSV 파일로 저장하는 기능을 수행합니다.
주요 기능:
- 교보문고 베스트셀러 API 페이지네이션 처리 및 전체 데이터 반복 수집
- 주요 도서 정보(순위, 도서명, 저자, 출판사, 가격 등) 추출
- 서버 부하 방지를 위한 딜레이 추가
- 추출된 데이터를 pandas DataFrame으로 변환 후 CSV 파일로 저장
"""

import requests
import pandas as pd
import os
import time

def scrape_bestseller():
    books = []
    page = 1
    
    while True:
        url = f"https://store.kyobobook.co.kr/api/gw/best/v2/best-seller/online?page={page}&per=20&saleCmdtClstCode=33&soldOutExcludeYn=N&saleCmdtDsplDvsnCode=KOR&period=002&dsplDvsnCode=001&dsplTrgtDvsnCode=004"
        
        headers = {
            "host": "store.kyobobook.co.kr",
            "referer": f"https://store.kyobobook.co.kr/category/domestic/33/best?page={page}",
            "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
            "x-api-gw-key": "eyJhbGciOiJkaXIiLCJlbmMiOiJBMjU2R0NNIn0..i35xkkCOngvXqCRx.0CqToQel6sj5d0qOS2ftoDu37jRwb0vtQwMBd1e_G1ynl7KUrTrH_qPJnygVpkc0tExt4BUX_pJ4RepB5QsxWmKLjC8tEuMELKG8SvRLEVn6ambMnSmDaJ85mLbGtHcM-zFiDBzi.3y1-RnxGHFxeLNMK2dWZoQ",
            "accept": "application/json, text/plain, */*"
        }
        
        print(f"{page}페이지 데이터 수집 중...")
        response = requests.get(url, headers=headers)
        
        if response.status_code == 200:
            data = response.json()
            best_sellers = data.get("data", {}).get("bestSeller", [])
            
            # 더 이상 수집할 데이터가 없으면 루프 종료
            if not best_sellers:
                print("마지막 페이지 도달. 데이터 수집을 종료합니다.")
                break
            
            for item in best_sellers:
                rank = item.get("prstRnkn")
                product_info = item.get("product", {}).get("productInfo", {})
                price_info = item.get("product", {}).get("priceInfo", {})
                
                book_title = product_info.get("cmdtName")
                author = product_info.get("chrcName")
                publisher = product_info.get("pbcmName")
                isbn = product_info.get("isbn")
                release_date = product_info.get("rlseDate")
                price = price_info.get("saleCmdtSapr")
                
                books.append({
                    "순위": rank,
                    "도서명": book_title,
                    "저자": author,
                    "출판사": publisher,
                    "출간일": release_date,
                    "ISBN": isbn,
                    "판매가": price
                })
            
            page += 1
            # 서버 과부하 방지를 위해 약간의 대기 시간 추가
            time.sleep(1)
            
        else:
            print(f"데이터 수집 실패. 상태 코드: {response.status_code}")
            print(response.text)
            break

    if books:
        df = pd.DataFrame(books)
        
        # 저장 경로 설정
        output_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.abspath(__file__))), "data")
        os.makedirs(output_dir, exist_ok=True)
        output_path = os.path.join(output_dir, "kyobo_bestseller.csv")
        
        # utf-8-sig로 저장해야 엑셀에서 한글이 깨지지 않음
        df.to_csv(output_path, index=False, encoding="utf-8-sig")
        print(f"총 {len(df)}건의 데이터를 성공적으로 수집하여 저장했습니다.")
        print(f"저장 경로: {output_path}")
    else:
        print("수집된 데이터가 없습니다.")

if __name__ == "__main__":
    scrape_bestseller()
