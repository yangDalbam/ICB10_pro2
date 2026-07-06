import sqlite3
import pandas as pd

with open('schema_info.txt', 'w', encoding='utf-8') as f:
    for db_path in [r"c:\Users\user1\Downloads\ICB10_proj2\getyourguide\data\getyourguide.db", r"c:\Users\user1\Downloads\ICB10_proj2\klook\data\klook_data.db"]:
        f.write(f"=== Inspecting {db_path} ===\n")
        conn = sqlite3.connect(db_path)
        tables = pd.read_sql("SELECT name FROM sqlite_master WHERE type='table';", conn)
        for table_name in tables['name']:
            f.write(f"Table: {table_name}\n")
            df = pd.read_sql(f"SELECT * FROM {table_name} LIMIT 3;", conn)
            f.write("Schema:\n")
            f.write(str(df.dtypes) + "\n")
            f.write("Sample data:\n")
            f.write(str(df) + "\n")
            f.write("-" * 30 + "\n")
        conn.close()
