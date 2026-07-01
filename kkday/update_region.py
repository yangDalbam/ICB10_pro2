"""
이 모듈은 KKDay DB의 특정 ID에 대한 지역명을 업데이트하는 스크립트입니다.
"""
import sqlite3
import os

db_path = os.path.join('c:\\Users\\user1\\Downloads\\ICB10_proj2\\kkday\\data', 'kkday_experiences.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 업데이트 규칙
updates = {
    "119655": "경기도 용인",
    "134684": "부산"
}

for p_id, new_region in updates.items():
    cursor.execute("UPDATE experiences SET region = ? WHERE id = ?", (new_region, p_id))
    print(f"Updated ID {p_id} to region {new_region}. Rows affected: {cursor.rowcount}")

conn.commit()
conn.close()
print("지역명 업데이트가 완료되었습니다.")
