import os
import json
import pandas as pd

files = os.listdir('korea-trip-data/data')
with open('scratch/files.json', 'w', encoding='utf-8') as f:
    json.dump(files, f, ensure_ascii=False)

def check_csv(keyword, encoding='utf-8'):
    matched = [f for f in files if keyword in f]
    res = {}
    for mf in matched:
        try:
            df = pd.read_csv('korea-trip-data/data/' + mf, encoding=encoding)
            res[mf] = list(df.columns)
        except Exception as e:
            res[mf] = f"Error: {e}"
    return res

res = {
    'spend': check_csv('소비', 'utf-8'),
    'intl': check_csv('외국인', 'utf-8')
}
with open('scratch/csv_cols.json', 'w', encoding='utf-8') as f:
    json.dump(res, f, ensure_ascii=False, indent=2)
