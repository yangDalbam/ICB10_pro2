import sqlite3
import pandas as pd

def main():
    conn = sqlite3.connect('C:/Users/user1/Downloads/ICB10_proj2/klook/data/klook_data.db')
    df = pd.read_sql('SELECT `data.title`, `data.city_name`, `data.location` FROM search_results LIMIT 5', conn)
    print(df.to_string())
    conn.close()

if __name__ == '__main__':
    main()
