import pandas as pd
import sqlite3
import os

data_dir = 'korea-trip-data/data'
df_ota = pd.read_csv(os.path.join(data_dir, 'ota_data.csv'))
df_kto_demand = pd.read_csv(os.path.join(data_dir, '20260702210628_지역별 검색건수.csv'), encoding='utf-8')

conn = sqlite3.connect(os.path.join(data_dir, 'tourist_spots.db'))
df_spots = pd.read_sql('SELECT * FROM recommended_spots', conn)
conn.close()

mapping_dict = {
    "서울특별시": "서울", "부산광역시": "부산", "대구광역시": "대구", "인천광역시": "인천",
    "광주광역시": "광주", "대전광역시": "대전", "울산광역시": "울산", "세종특별자치시": "세종",
    "경기도": "경기", "강원특별자치도": "강원", "강원도": "강원", "충청북도": "충북", "충청남도": "충남",
    "전북특별자치도": "전북", "전라북도": "전북", "전라남도": "전남", "경상북도": "경북",
    "경상남도": "경남", "제주특별자치도": "제주", "제주도": "제주"
}

def normalize_region(name):
    if not isinstance(name, str): return ""
    parts = name.split()
    if len(parts) >= 2:
        sido = parts[0]
        sigungu = parts[1]
        for k, v in mapping_dict.items():
            if sido == k:
                sido = v
        # Fix for some bad data in spots (e.g. "가평군 청평면" -> "경기 가평군")
        # Just use it as is, or maybe we just merge on sigungu for now?
        # If sido ends with '시' or '군' or '구' it means Sido is missing.
        if sido.endswith(('시', '군', '구')) and sido not in mapping_dict.values() and sido not in mapping_dict.keys():
            # it's probably missing sido
            pass
        return f"{sido} {sigungu}"
    return name

# 1. OTA
def clean_region(r):
    if pd.isna(r): return "알 수 없음"
    r = str(r).strip()
    parts = r.split()
    if len(parts) >= 2: return f"{parts[0]} {parts[1]}"
    return r

df_ota['region_sigungu'] = df_ota['region'].apply(clean_region)
df_ota['norm_region'] = df_ota['region_sigungu'].apply(normalize_region)
ota_counts = df_ota[df_ota['norm_region'] != '알 수 없음'].groupby('norm_region').size().reset_index(name='ota_count')

# 2. Spots
df_spots['norm_region'] = df_spots['지역_시도시군구'].apply(normalize_region)
spot_counts = df_spots.groupby('norm_region').size().reset_index(name='spot_count')

# 3. KTO demand
df_kto_demand = df_kto_demand[~df_kto_demand["광역지자체"].str.contains("서울|부산|제주")].copy()
df_kto_demand["signguNm"] = df_kto_demand["광역지자체"] + " " + df_kto_demand["기초지자체"]
df_kto_demand['norm_region'] = df_kto_demand["signguNm"].apply(normalize_region)
visit_volume = df_kto_demand.groupby('norm_region')['기초지자체 검색건수'].sum().reset_index(name='visit_volume')

# Merge
merged = pd.merge(visit_volume, ota_counts, on='norm_region', how='left').fillna({'ota_count': 0})
merged = pd.merge(merged, spot_counts, on='norm_region', how='left').fillna({'spot_count': 0})

# min max scaling then median
from sklearn.preprocessing import MinMaxScaler
scaler = MinMaxScaler(feature_range=(0, 100))
merged[['ota_scaled', 'spot_scaled']] = scaler.fit_transform(merged[['ota_count', 'spot_count']])
merged['infra_score'] = merged[['ota_scaled', 'spot_scaled']].mean(axis=1)

corr = merged['infra_score'].corr(merged['visit_volume'])

with open('scratch/test_out2.txt', 'w', encoding='utf-8') as f:
    f.write(merged.sort_values('visit_volume', ascending=False).head(10).to_string())
    f.write(f"\\n\\nCorrelation: {corr}")
