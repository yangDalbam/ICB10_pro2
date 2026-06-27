import sqlite3
import pandas as pd

def main():
    conn = sqlite3.connect('C:/Users/user1/Downloads/ICB10_proj2/klook/data/klook_data.db')
    df = pd.read_sql('SELECT object_id, detail_title, price_info FROM detail_results WHERE price_info IS NOT NULL AND price_info != ""', conn)
    for i, row in df.iterrows():
        print(f"ID: {row['object_id']}")
        print(f"제목: {row['detail_title']}")
        print(f"가격: {row['price_info']}")
        print('-'*20)
    conn.close()

if __name__ == '__main__':
    main()
