"""
이 모듈은 Klook API를 호출하여 전체 검색 결과를 페이지별로 수집하고 SQLite DB에 저장하는 기능을 수행합니다.
주요 기능:
- Klook API HTTP GET 요청 (페이징 처리)
- 0.1~1초 랜덤 딜레이 적용
- 추출된 데이터를 SQLite DB에 페이지 단위로 추가 (append)
"""

import requests
import pandas as pd
import json
import time
import random
import sqlite3
import traceback
from urllib.parse import urlparse, parse_qsl, urlencode, urlunparse

def get_url_for_page(base_url, page):
    parsed = urlparse(base_url)
    query_params = dict(parse_qsl(parsed.query))
    query_params['start'] = str(page)
    new_query = urlencode(query_params)
    return urlunparse(parsed._replace(query=new_query))

def main():
    base_url = "https://www.klook.com/v1/cardinfocenterservicesrv/search/platform/complete_search_v3?location=158%2C157%2C156%2C5031%2C8928%2C24975%2C28741%2C545%2C6166%2C6268%2C703649%2C703648%2C705582%2C6955%2C15088%2C701102%2C16467%2C707516%2C26374%2C7204%2C20296%2C28785%2C28972%2C8898%2C23546%2C30633%2C15378%2C16365%2C28742%2C10956%2C26961%2C10093%2C16560%2C25178%2C7741%2C11925%2C24865%2C25140%2C30570%2C7030%2C707332%2C7558%2C8989%2C10706%2C11364%2C11745%2C13523%2C14446%2C15281%2C15603%2C16655%2C18214%2C18323%2C20392%2C22390%2C22675%2C23237%2C24520%2C24762%2C25060%2C26454%2C27895%2C29136%2C29872%2C30051%2C30265%2C30376%2C30466%2C31247%2C705101%2C9079&sort=most_relevant&tab_key=0&start=1&query=%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD&size=15&search_scope=main_search&k_lang=ko_KR&k_currency=KRW"

    headers = {
        "_pt": "a80497bc-a595-467b-b5be-2e3f24c643a5",
        "accept": "application/json, text/plain, */*",
        "accept-encoding": "gzip, deflate, br, zstd",
        "accept-language": "ko_KR",
        "baggage": "sentry-environment=production,sentry-release=web_ssr-platform_20260623_7acde2fb,sentry-public_key=919ae3dd598137e1aa2a88c31e161bb3,sentry-trace_id=f58bdd1f067f452e9a7de0055c9a2c4f,sentry-transaction=SearchResult,sentry-sampled=false,sentry-sample_rand=0.5150356711438143,sentry-sample_rate=0",
        "cache-control": "no-cache",
        "priority": "u=1, i",
        "referer": "https://www.klook.com/ko/search/result/?query=%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD&search_scope=main_search&location=158,157,156,5031,8928,24975,28741,545,6166,6268,703649,703648,705582,6955,15088,701102,16467,707516,26374,7204,20296,28785,28972,8898,23546,30633,15378,16365,28742,10956,26961,10093,16560,25178,7741,11925,24865,25140,30570,7030,707332,7558,8989,10706,11364,11745,13523,14446,15281,15603,16655,18214,18323,20392,22390,22675,23237,24520,24762,25060,26454,27895,29136,29872,30051,30265,30376,30466,31247,705101,9079&sort=most_relevant&tab_key=0&start=2",
        "sec-ch-device-memory": "16",
        "sec-ch-ua": '"Google Chrome";v="149", "Chromium";v="149", "Not)A;Brand";v="24"',
        "sec-ch-ua-arch": '"x86"',
        "sec-ch-ua-full-version-list": '"Google Chrome";v="149.0.7827.116", "Chromium";v="149.0.7827.116", "Not)A;Brand";v="24.0.0.0"',
        "sec-ch-ua-mobile": "?0",
        "sec-ch-ua-model": '""',
        "sec-ch-ua-platform": '"Windows"',
        "sec-fetch-dest": "empty",
        "sec-fetch-mode": "cors",
        "sec-fetch-site": "same-origin",
        "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        "x-klook-channel-level-one": "Direct",
        "x-klook-host": "www.klook.com",
        "x-klook-market": "global",
        "x-klook-user-residence": "10_KR",
        "x-platform": "desktop",
        "x-requested-with": "XMLHttpRequest"
    }

    db_path = "klook/data/klook_data.db"
    conn = sqlite3.connect(db_path)
    
    page = 1
    total_items = None
    collected = 0

    while True:
        url = get_url_for_page(base_url, page)
        print(f"Requesting page {page}...")
        
        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
            data = response.json()
            
            if data.get("success"):
                search_result = data.get("result", {}).get("search_result", {})
                cards = search_result.get("cards", [])
                
                if total_items is None:
                    total_items = search_result.get("total", 0)
                    print(f"Total items to collect: {total_items}")

                if not cards:
                    print("No more items found. Ending collection.")
                    break
                
                # Convert list of dicts to DataFrame and handle nested JSON if needed
                # To save cleanly to SQLite, convert complex types to string
                df = pd.json_normalize(cards)
                for col in df.columns:
                    if df[col].apply(lambda x: isinstance(x, (list, dict))).any():
                        df[col] = df[col].apply(json.dumps, ensure_ascii=False)
                
                # Append to sqlite table with schema check
                cursor = conn.cursor()
                cursor.execute("SELECT name FROM sqlite_master WHERE type='table' AND name='search_results'")
                if cursor.fetchone() is None:
                    # First time
                    df.to_sql('search_results', conn, if_exists='append', index=False)
                else:
                    existing_cols = [row[1] for row in cursor.execute("PRAGMA table_info('search_results')")]
                    for col in df.columns:
                        if col not in existing_cols:
                            cursor.execute(f'ALTER TABLE search_results ADD COLUMN "{col}" TEXT')
                    df.to_sql('search_results', conn, if_exists='append', index=False)
                
                collected += len(cards)
                print(f"Page {page} collected: {len(cards)} items. (Total collected: {collected}/{total_items})")
                
                if collected >= total_items:
                    print("All items collected.")
                    break
                
                page += 1
                
                # Random delay between 0.1 and 1 second
                sleep_time = random.uniform(0.1, 1.0)
                time.sleep(sleep_time)
            else:
                print(f"API returned success=false on page {page}")
                print(data.get("error"))
                break

        except Exception as e:
            print(f"Error on page {page}: {e}")
            traceback.print_exc()
            break

    conn.close()
    print("Data collection completed.")

if __name__ == "__main__":
    main()
