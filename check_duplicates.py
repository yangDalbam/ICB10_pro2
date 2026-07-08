import sqlite3
import pandas as pd

# DB 연결
conn = sqlite3.connect('korea-trip-data/data/tourist_spots.db')
df = pd.read_sql('SELECT * FROM recommended_spots', conn)
conn.close()

# 중복 데이터 검사 (모든 컬럼 기준)
duplicates = df[df.duplicated(keep=False)]

print(f"총 데이터 건수: {len(df)}")
print(f"중복된 행 건수 (원본 포함): {len(duplicates)}")

if len(duplicates) > 0:
    print("\n중복된 데이터 예시:")
    print(duplicates.sort_values(by=['TITLE']).head(10).to_markdown())
else:
    print("\n중복된 데이터가 없습니다.")
