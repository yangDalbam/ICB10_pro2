import os

file_path = 'korea-trip-data/src/views/demand_analysis.py'
with open(file_path, 'r', encoding='utf-8') as f:
    lines = f.readlines()

# find indices
corr_start = -1
corr_end = -1
pub_start = -1
pub_end = -1

for i, line in enumerate(lines):
    if 'st.markdown("### 🔍 지역 인프라와 방문 규모 상관관계 분석")' in line:
        corr_start = i
    if '# --- 문화공공데이터광장 추천 여행지 분석 추가 ---' in line:
        corr_end = i
        pub_start = i

pub_end = len(lines)

if corr_start != -1 and pub_start != -1:
    top_part = lines[:corr_start]
    corr_part = lines[corr_start:corr_end]
    pub_part = lines[pub_start:pub_end]
    
    # Change headers to match the flow
    # Optional: rename "3. 문화공공데이터광장 추천 여행지 분석" -> "3. 문화공공데이터광장 추천 여행지 분석"
    # Rename "### 🔍 지역 인프라와 방문 규모 상관관계 분석" -> "---" + "### 4. 🔍 지역 인프라와 방문 규모 상관관계 분석"
    
    # We want top_part + pub_part + corr_part
    # Let's adjust separators
    
    new_lines = top_part + pub_part + ["\\n        st.markdown('---')\\n"] + corr_part
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.writelines(new_lines)
    print("Swapped successfully")
else:
    print("Could not find sections")
