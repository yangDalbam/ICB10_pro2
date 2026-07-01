"""
이 모듈은 KKDay DB를 확인하는 스크립트입니다.
"""
import sqlite3
import os

db2 = 'c:\\Users\\user1\\Downloads\\ICB10_proj2\\kkday\\data\\kkday_experiences.db'

conn = sqlite3.connect(db2)
cursor = conn.cursor()
cursor.execute("SELECT count(*) FROM experiences")
print(f"Total rows: {cursor.fetchone()[0]}")
cursor.execute("SELECT id, title, price FROM experiences LIMIT 5")
for r in cursor.fetchall():
    print(r)


