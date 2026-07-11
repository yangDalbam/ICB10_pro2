import pandas as pd
df = pd.read_csv('korea-trip-data/data/ota_data.csv')
with open('scratch/incheon_regions.txt', 'w', encoding='utf-8') as f:
    f.write(str(df[df['region'].str.contains('인천', na=False)]['region'].value_counts()))
