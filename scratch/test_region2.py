import pandas as pd
df = pd.read_csv('korea-trip-data/data/ota_data.csv')
def clean_region_sigungu(r):
    if pd.isna(r): return "알 수 없음"
    r = str(r).strip()
    parts = r.split()
    if len(parts) >= 2: return f"{parts[0]} {parts[1]}"
    elif len(parts) == 1: return parts[0]
    return "알 수 없음"
df['region_sigungu'] = df['region'].apply(clean_region_sigungu)

df_filtered = df[~df['region_sigungu'].str.contains('제주|서울|부산')]
print(df_filtered['region_sigungu'].value_counts().head(10))
