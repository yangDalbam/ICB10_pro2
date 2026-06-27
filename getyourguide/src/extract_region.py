"""
이 모듈은 데이터베이스의 상품 제목을 분석하여 실제 여행지(지역명)를 추출하고 DB와 CSV를 업데이트합니다.
"""
import sqlite3
import pandas as pd
import os

def extract_region(title):
    # 주요 지역명 키워드 목록 (우선순위에 따라 정렬, ex: '수원'이 '서울'보다 실제 목적지일 확률이 높음)
    keywords = [
        '수원', '남이섬', '가평', '경주', '전주', '제주', '파주', '강릉', '속초', 
        '여수', '평창', '용인', '춘천', '에버랜드', '남이', '알파카', '레고랜드', 
        '설악산', '안동', '포항', 'DMZ', '제3땅굴', '판문점', '인천', '부산', '서울'
    ]
    
    # '출발지: 목적지 설명' 형태인 경우 콜론 뒤의 텍스트를 주로 탐색
    search_text = title
    if ':' in title:
        parts = title.split(':', 1)
        # 콜론 앞이 출발지, 뒤가 설명인 경우가 많음
        search_text = parts[1]
    
    # 먼저 설명(search_text) 부분에서 지역 키워드를 찾습니다.
    for kw in keywords:
        if kw in search_text:
            if kw == '남이' or kw == '남이섬': return '춘천'
            if kw == '에버랜드': return '용인'
            if kw == '제3땅굴' or kw == '판문점': return 'DMZ'
            if kw == '알파카' or kw == '레고랜드': return '춘천'
            return kw
            
    # 설명 부분에서 못 찾았다면, 전체 제목에서 찾습니다.
    for kw in keywords:
        if kw in title:
            if kw == '남이' or kw == '남이섬': return '춘천'
            if kw == '에버랜드': return '용인'
            if kw == '제3땅굴' or kw == '판문점': return 'DMZ'
            if kw == '알파카' or kw == '레고랜드': return '춘천'
            return kw
            
    return '기타' # 찾지 못한 경우

def main():
    db_path = os.path.join('getyourguide', 'data', 'getyourguide.db')
    csv_path = os.path.join('getyourguide', 'data', 'getyourguide.csv')
    
    # DB 연결
    conn = sqlite3.connect(db_path)
    
    # region 컬럼이 있는지 확인하고 없으면 추가
    cursor = conn.cursor()
    cursor.execute("PRAGMA table_info(activities)")
    columns = [info[1] for info in cursor.fetchall()]
    
    if 'region' not in columns:
        cursor.execute("ALTER TABLE activities ADD COLUMN region TEXT")
        conn.commit()
    
    # 데이터 읽기
    df = pd.read_sql_query("SELECT * FROM activities", conn)
    
    # region 추출
    df['region'] = df['title'].apply(extract_region)
    
    # DB 업데이트
    for index, row in df.iterrows():
        cursor.execute("UPDATE activities SET region = ? WHERE id = ?", (row['region'], row['id']))
    conn.commit()
    conn.close()
    
    # CSV 저장 (id 제외하고 저장, 기존 포맷 유지)
    csv_cols = ['title', 'duration', 'rating', 'reviews', 'price', 'page', 'region']
    
    # 열 이름을 첫 글자 대문자로 변경 (기존 CSV 헤더와 맞춤)
    rename_dict = {
        'title': 'Title',
        'duration': 'Duration',
        'rating': 'Rating',
        'reviews': 'Reviews',
        'price': 'Price',
        'page': 'Page',
        'region': 'Region'
    }
    df_csv = df[csv_cols].rename(columns=rename_dict)
    df_csv.to_csv(csv_path, index=False, encoding='utf-8-sig')
    
    print("지역명 추출 및 업데이트 완료!")
    print(df['region'].value_counts())

if __name__ == "__main__":
    main()
