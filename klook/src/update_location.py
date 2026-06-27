import sqlite3
import pandas as pd

def main():
    conn = sqlite3.connect('C:/Users/user1/Downloads/ICB10_proj2/klook/data/klook_data.db')
    cursor = conn.cursor()
    
    # get all detail_results
    cursor.execute('SELECT object_id, detail_title, location_info FROM detail_results')
    rows = cursor.fetchall()
    
    regions = ['경기 용인', '서울', '부산', '대구', '인천', '광주', '대전', '울산', '세종', '경기', '강원', '충북', '충남', '전북', '전남', '경북', '경남', '제주', '하남', '춘천', '용인', '대한민국']
    
    updated_count = 0
    for object_id, title, loc_info in rows:
        if not title:
            continue
            
        new_loc = None
        title_parts = title.split()
        if len(title_parts) >= 1:
            first_two_words = f"{title_parts[0]} {title_parts[1]}" if len(title_parts) >= 2 else title_parts[0]
            for r in regions:
                if r in first_two_words:
                    new_loc = r
                    break
                    
        # Special cases or fallbacks based on specific titles seen
        if '티머니' in title or 'eSIM' in title or '유심' in title:
            new_loc = '대한민국'
            
        # Update db
        if new_loc:
            cursor.execute('UPDATE detail_results SET location_info = ? WHERE object_id = ?', (new_loc, object_id))
            updated_count += 1
            print(f"ID: {object_id} | Title: {title} | Location: {new_loc}")
            
    conn.commit()
    conn.close()
    print(f"Total updated: {updated_count}")

if __name__ == '__main__':
    main()
