"""
이 모듈은 KKDay DB의 제목과 지역명 데이터를 분석하기 위해 출력하는 스크립트입니다.
"""
import sqlite3
import os

db_path = os.path.join('c:\\Users\\user1\\Downloads\\ICB10_proj2\\kkday\\data', 'kkday_experiences.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

cursor.execute("SELECT id, title, region FROM experiences")
rows = cursor.fetchall()

with open("titles.txt", "w", encoding="utf-8") as f:
    f.write(f"Total rows: {len(rows)}\n")
    f.write("Sample titles and regions:\n")
    for r in rows:
        f.write(f"ID: {r[0]} | Region: {r[2]} | Title: {r[1]}\n")

conn.close()
