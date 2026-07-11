"""
이 스크립트는 여러 OTA 플랫폼(kkday, klook, getyourguide)의 SQLite DB 데이터를 통합하여 
하나의 ota_data.csv 파일로 추출하는 데이터 전처리 모듈입니다.
"""

import sqlite3
import pandas as pd
import os

def fetch_ota_data():
    project_root = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    dbs = [
        (os.path.join(project_root, 'kkday', 'data', 'kkday_products.db'), 'kkday_products', 'KKday'),
        (os.path.join(project_root, 'klook', 'data', 'klook_data.db'), 'activities', 'Klook'),
        (os.path.join(project_root, 'getyourguide', 'data', 'getyourguide.db'), 'activities', 'GetYourGuide')
    ]

    dfs = []
    for db_path, table, platform_name in dbs:
        if os.path.exists(db_path):
            try:
                conn = sqlite3.connect(db_path)
                df = pd.read_sql(f'SELECT * FROM "{table}"', conn)
                df['platform'] = platform_name
                dfs.append(df)
                conn.close()
                print(f"[{platform_name}] {len(df)}건 데이터 수집 완료")
            except Exception as e:
                print(f"[{platform_name}] 데이터 로드 실패: {e}")
        else:
            print(f"[{platform_name}] DB 파일을 찾을 수 없습니다: {db_path}")

    if dfs:
        df_all = pd.concat(dfs, ignore_index=True)
        out_dir = os.path.join(project_root, 'korea-trip-data', 'data')
        os.makedirs(out_dir, exist_ok=True)
        out_path = os.path.join(out_dir, 'ota_data.csv')
        df_all.to_csv(out_path, index=False, encoding='utf-8')
        print(f"\n[성공] 총 {len(df_all)}건의 통합 데이터를 {out_path}에 저장했습니다.")
    else:
        print("수집된 데이터가 없습니다.")

if __name__ == '__main__':
    fetch_ota_data()
