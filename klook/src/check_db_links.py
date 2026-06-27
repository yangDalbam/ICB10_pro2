import sqlite3
import pandas as pd

conn = sqlite3.connect('C:/Users/user1/Downloads/ICB10_proj2/klook/data/klook_data.db')
df = pd.read_sql_query("SELECT `data.deep_link`, `data.seo.url`, `track_info.object_id` FROM search_results LIMIT 5", conn)
print(df)
conn.close()
