"""
이 모듈은 사용자가 수동으로 매핑한 규칙에 따라 지역명을 업데이트하고,
'서울' 또는 '삭제'로 분류된 항목을 DB에서 제거하는 스크립트입니다.
"""
import sqlite3
import os

db_path = os.path.join('c:\\Users\\user1\\Downloads\\ICB10_proj2\\kkday\\data', 'kkday_experiences.db')
conn = sqlite3.connect(db_path)
cursor = conn.cursor()

# 삭제할 지역명 목록 (사용자가 '서울' 또는 '삭제'라고 코멘트한 항목)
to_delete = [
    "ASHU", "MSC", "【체험", "개인", "고즈넉한", "깜짝", "나만의", 
    "더설하", "롯데월드", "루루", "비브로우", "아드레포", "아몽하르", 
    "전문", "정관장", "코스타", "코코리아", "킹스", "피트니스", "한국"
]

# 업데이트할 지역명 매핑
mappings = {
    "2박": "단양",
    "BTO": "울산",
    "K-웰니스": "경기 양평",
    "KKday": "DMZ",
    "Mt.": "정읍",
    "감성교복": "대구",
    "반려동물과": "춘천",
    "북한의": "DMZ",
    "아쿠아필드": "경기 고양",
    "얼리버드": "홍천",
    "에버랜드": "경기 용인",
    "에버랜드/캐리비안베이": "경기 용인",
    "여름": "경기 가평",
    "인더숲": "평창",
    "체험": "춘천",
    "파라다이스": "인천",
    "한류": "속초",
    "화려한": "용인"
}

deleted_count = 0
for region_str in to_delete:
    cursor.execute("DELETE FROM experiences WHERE region = ?", (region_str,))
    deleted_count += cursor.rowcount

updated_count = 0
for old_r, new_r in mappings.items():
    cursor.execute("UPDATE experiences SET region = ? WHERE region = ?", (new_r, old_r))
    updated_count += cursor.rowcount

conn.commit()

print(f"삭제된 데이터 개수: {deleted_count}")
print(f"업데이트된 데이터 개수: {updated_count}")

cursor.execute("SELECT count(*) FROM experiences")
remaining_count = cursor.fetchone()[0]
print(f"현재 남은 총 데이터 개수: {remaining_count}")

conn.close()
