import sqlite3
import os

db_path = r"C:\Users\user1\Downloads\ICB10_proj2\getyourguide\data\getyourguide.db"

if not os.path.exists(db_path):
    print("DB file not found:", db_path)
else:
    conn = sqlite3.connect(db_path)
    cursor = conn.cursor()
    cursor.execute("SELECT name FROM sqlite_master WHERE type='table';")
    tables = cursor.fetchall()
    
    for table_name in tables:
        table_name = table_name[0]
        print(f"Table: {table_name}")
        cursor.execute(f"PRAGMA table_info({table_name});")
        columns = cursor.fetchall()
        for col in columns:
            print(f"  {col[1]} ({col[2]})")
            
    conn.close()
