"""
Klook 상세 페이지 수집 데이터와 원본 검색 데이터 조인 확인용 스크립트
"""
import sqlite3
import pandas as pd

def main():
    conn = sqlite3.connect('C:/Users/user1/Downloads/ICB10_proj2/klook/data/klook_data.db')
    
    query = '''
        SELECT 
            s.`track_info.object_id` AS object_id,
            s.`data.title` AS search_title,
            s.`data.price.selling_price` AS price,
            d.detail_title,
            d.description,
            d.package_options,
            d.price_info,
            d.location_info,
            d.url
        FROM detail_results d
        LEFT JOIN search_results s ON s.`track_info.object_id` = d.object_id
    '''
    
    try:
        df = pd.read_sql(query, conn)
        # cp949 인코딩 오류를 피하기 위해 파일로 출력하거나 일부만 출력
        output_file = 'C:/Users/user1/Downloads/ICB10_proj2/klook/data/join_result_sample.csv'
        df.to_csv(output_file, index=False, encoding='utf-8-sig')
        print(f"조인 결과 {len(df)}건을 {output_file} 에 저장했습니다.")
        
        # 간단히 정보 출력
        for i, row in df.iterrows():
            print(f"ID: {row['object_id']}")
            print(f"  검색제목: {row['search_title'][:30] if pd.notna(row['search_title']) else 'N/A'}")
            print(f"  상세제목: {row['detail_title'][:30] if pd.notna(row['detail_title']) else 'N/A'}")
            print(f"  상세가격: {row['price_info']}")
            print(f"  지역정보: {row['location_info']}")
            print(f"  설명길이: {len(str(row['description']))}자")
            print("-" * 40)
            if i >= 4: # 5개만 출력
                break
                
    except Exception as e:
        print(f"오류 발생: {e}")
    finally:
        conn.close()

if __name__ == "__main__":
    main()
