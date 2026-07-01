"""
이 모듈은 KKDay DB에서 특정 지역명('서울', '부산', '제주')이 포함된 데이터를 삭제하는 스크립트입니다.
"""
import sqlite3
import os

db_path = os.path.join('c:\\Users\\user1\\Downloads\\ICB10_proj2\\kkday\\data', 'kkday_experiences.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 삭제 전 전체 데이터 개수 확인
cursor.execute("SELECT count(*) FROM experiences")
initial_count = cursor.fetchone()[0]
print(f"삭제 전 전체 데이터 개수: {initial_count}")

# '서울', '부산', '제주'가 포함된 행 삭제 (이번에는 title 기준)
cursor.execute('''
    DELETE FROM experiences 
    WHERE title LIKE '%서울%' 
       OR title LIKE '%부산%' 
       OR title LIKE '%제주%'
''')

deleted_count = cursor.rowcount
print(f"삭제된 데이터 개수: {deleted_count}")

conn.commit()

# 삭제 후 남은 데이터 개수 확인
cursor.execute("SELECT count(*) FROM experiences")
final_count = cursor.fetchone()[0]
print(f"삭제 후 남은 데이터 개수: {final_count}")

conn.close()
