import pandas as pd
import os

file_path = 'korea-trip-data/data/ota_data.csv'
df = pd.read_csv(file_path)

# 1. 삭제할 인덱스
drop_indices = [137, 138]
df = df.drop(index=drop_indices)

# 2. 업데이트할 지역명 매핑 (인덱스: 새로운 지역명)
update_mapping = {
    146: "인천광역시 영종구",
    154: "인천광역시 영종구",
    160: "인천광역시 중구",
    172: "인천광역시 중구",
    193: "인천광역시 중구",
    197: "인천광역시 영종구",
    198: "인천광역시 중구",
    199: "인천광역시 미추홀구",
    202: "인천광역시 중구",
    206: "인천광역시 연수구",
    230: "인천광역시 중구",
    238: "경기도 이천시"
}

for idx, new_region in update_mapping.items():
    if idx in df.index:
        df.at[idx, 'region'] = new_region

# 결과를 다시 저장
df.to_csv(file_path, index=False, encoding='utf-8')
print("Data successfully updated!")
