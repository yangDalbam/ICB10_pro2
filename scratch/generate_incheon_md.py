import pandas as pd
import os

df = pd.read_csv('korea-trip-data/data/ota_data.csv')
incheon_df = df[df['region'] == '인천광역시'].copy()

md_content = """# '인천광역시' 표기 OTA 상품 목록
해당 상품들은 세부 시군구 없이 '인천광역시'로만 지역이 표기된 상품들입니다. 
아래 표의 내용을 참고하셔서, 이 상품들이 실제로 속하는 올바른 시/군/구명(예: 인천광역시 중구, 인천광역시 연수구 등)을 쉼표 등으로 구분해서 알려주시거나 엑셀 등 다른 형태로 알려주시면, 데이터를 수정하여 다시 대시보드를 업데이트해 드릴 수 있습니다.

| 인덱스(순번) | 플랫폼 | 상품명 (Title) | 가격 |
|---|---|---|---|
"""

for idx, row in incheon_df.iterrows():
    # 이스케이프 처리
    title_clean = str(row['title']).replace('|', '\|')
    md_content += f"| {idx} | {row['platform']} | {title_clean} | {row['price']} |\n"

with open(r'c:\Users\user1\.gemini\antigravity-ide\brain\e6840d0d-783d-431d-8224-46625383d4db\incheon_ota_products.md', 'w', encoding='utf-8') as f:
    f.write(md_content)

print("Markdown generated.")
