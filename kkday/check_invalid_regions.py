"""
이 모듈은 KKDay DB에서 지역명 데이터를 추출하여 파일로 저장하는 스크립트입니다.
"""
import sqlite3
import os

db_path = os.path.join('c:\\Users\\user1\\Downloads\\ICB10_proj2\\kkday\\data', 'kkday_experiences.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 남은 117개 데이터에 대해 region과 title을 모두 가져옵니다.
cursor.execute("SELECT region, title FROM experiences ORDER BY region")
rows = cursor.fetchall()

with open("invalid_regions_log.txt", "w", encoding="utf-8") as f:
    for r in rows:
        f.write(f"Region: {r[0]} | Title: {r[1]}\n")

conn.close()
