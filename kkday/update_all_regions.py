"""
이 모듈은 KKDay DB의 지역명을 상품 타이틀을 기반으로 일괄 변경하는 스크립트입니다.
주요 기능:
- 대괄호 시작 타이틀: 대괄호 안의 첫 번째 단어 추출
- 일반 타이틀: 첫 번째 띄어쓰기 이전 단어 추출
- 특정 예외 룰 반영 및 DB 업데이트
"""
import sqlite3
import os
import re

db_path = os.path.join('c:\\Users\\user1\\Downloads\\ICB10_proj2\\kkday\\data', 'kkday_experiences.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

def extract_region(title, p_id):
    # 예외 처리
    if str(p_id) == "119655":
        return "용인"
    if str(p_id) == "134684":
        return "부산"
        
    title = title.strip()
    if title.startswith('['):
        # 대괄호 안의 텍스트 추출
        end_idx = title.find(']')
        if end_idx != -1:
            bracket_text = title[1:end_idx]
            # 공백, 슬래시, 파이프 등으로 분리
            parts = re.split(r'[\s/|]', bracket_text)
            for p in parts:
                if p.strip():
                    return p.strip()
                    
    # 대괄호가 없거나, 추출하지 못한 경우 첫 번째 띄어쓰기 기준 앞 단어
    parts = title.split(' ')
    for p in parts:
        if p.strip():
            return p.strip()
            
    return ""

cursor.execute("SELECT id, title FROM experiences")
rows = cursor.fetchall()

update_count = 0
for r in rows:
    p_id = r[0]
    title = r[1]
    new_region = extract_region(title, p_id)
    
    cursor.execute("UPDATE experiences SET region = ? WHERE id = ?", (new_region, p_id))
    update_count += 1

conn.commit()

print(f"Total {update_count} rows updated.")
with open("update_log.txt", "w", encoding="utf-8") as f:
    cursor.execute("SELECT id, region, title FROM experiences LIMIT 20")
    for r in cursor.fetchall():
        f.write(f"ID: {r[0]} | Reg: {r[1]} | Title: {r[2]}\n")

conn.close()
