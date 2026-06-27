import sqlite3
import pandas as pd

conn = sqlite3.connect('C:/Users/user1/Downloads/ICB10_proj2/klook/data/klook_data.db')
cursor = conn.cursor()
cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
tables = cursor.fetchall()

print("Tables in database:", tables)

for table in tables:
    table_name = table[0]
    print(f"\nTable: {table_name}")
    try:
        df = pd.read_sql_query(f"SELECT * FROM {table_name} LIMIT 5", conn)
        print("Columns:", list(df.columns))
        print("Number of total rows:", pd.read_sql_query(f"SELECT COUNT(*) FROM {table_name}", conn).iloc[0, 0])
        print("Sample data:")
        print(df)
    except Exception as e:
        print(f"Error reading table {table_name}: {e}")
