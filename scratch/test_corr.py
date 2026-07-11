import pandas as pd
import sqlite3
import os

data_dir = 'korea-trip-data/data'
df_ota = pd.read_csv(os.path.join(data_dir, 'ota_data.csv'))
df_kto_demand = pd.read_csv(os.path.join(data_dir, '20260702210628_지역별 검색건수.csv'), encoding='utf-8')

conn = sqlite3.connect(os.path.join(data_dir, 'tourist_spots.db'))
df_spots = pd.read_sql('SELECT * FROM recommended_spots', conn)
conn.close()

# 1. OTA
def clean_region(r):
    if pd.isna(r): return "알 수 없음"
    r = str(r).strip()
    parts = r.split()
    if len(parts) >= 2: return f"{parts[0]} {parts[1]}"
    return r

df_ota['region_sigungu'] = df_ota['region'].apply(clean_region)
ota_counts = df_ota[df_ota['region_sigungu'] != '알 수 없음'].groupby('region_sigungu').size().reset_index(name='ota_count')

# 2. Spots
spot_counts = df_spots.groupby('지역_시도시군구').size().reset_index(name='spot_count')

# 3. KTO demand
# Filter Seoul, Busan, Jeju
df_kto_demand = df_kto_demand[~df_kto_demand["광역지자체"].str.contains("서울|부산|제주")].copy()
df_kto_demand["signguNm"] = df_kto_demand["광역지자체"] + " " + df_kto_demand["기초지자체"]
visit_volume = df_kto_demand[['signguNm', '기초지자체 검색건수']].copy()

# Merge all three
# Note: region formats might differ slightly (e.g. '강원특별자치도 춘천시' vs '강원 춘천시')
# df_spots['지역_시도시군구'] is '인천 중구' or '인천광역시 중구'?
# df_ota['region_sigungu'] is '인천광역시 중구' or '인천 중구'?

with open('scratch/test_out.txt', 'w', encoding='utf-8') as f:
    f.write("OTA:\\n")
    f.write(ota_counts.head().to_string())
    f.write("\\n\\nSpots:\\n")
    f.write(spot_counts.head().to_string())
    f.write("\\n\\nVisit:\\n")
    f.write(visit_volume.head().to_string())
