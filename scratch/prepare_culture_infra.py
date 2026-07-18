"""
이 모듈은 축제, 다국어가이드, 세계음식점 원본 데이터를 읽어 시군구별 통계 요약본을 생성합니다.
주요 기능:
- 3종의 문화/관광 공공데이터 읽기
- 주소 기반 시도/시군구 정규화
- 데이터프레임 병합 및 CSV 저장
"""

import pandas as pd
import os

data_dir = r"c:\Users\user1\Downloads\ICB10_proj2\korea-trip-data\data"

import re
def clean_region(r):
    if pd.isna(r): return ""
    r = str(r).split(',')[0].strip()
    r = re.sub(r'^\(\d+\)\s*', '', r)
    parts = r.split()
    if len(parts) >= 2:
        return f"{parts[0]} {parts[1]}"
    elif len(parts) == 1:
        return parts[0]
    return ""

def process_data(filename, col_name, output_col):
    df = pd.read_csv(os.path.join(data_dir, filename), encoding='utf-8')
    df['norm_region'] = df[col_name].apply(clean_region)
    df = df[df['norm_region'] != '']
    grouped = df.groupby('norm_region').size().reset_index(name=output_col)
    return grouped

df_fest = process_data("문화체육관광부_지역축제정보(20260606).csv", "SPATIALCOVERAGE", "축제수")
df_guide = process_data("한국문화정보원_전국 다국어 가이드 제공 문화시설(20260711).csv", "ADDRESS", "다국어가이드수")
df_food = process_data("한국문화정보원_전국 세계음식점(20260711).csv", "ADDRESS", "세계음식점수")

# Merge
summary = pd.merge(df_fest, df_guide, on='norm_region', how='outer').fillna(0)
summary = pd.merge(summary, df_food, on='norm_region', how='outer').fillna(0)

# Normalize the sido names to match standard map
mapping_dict = {
    "서울특별시": "서울", "부산광역시": "부산", "대구광역시": "대구", "인천광역시": "인천",
    "광주광역시": "광주", "대전광역시": "대전", "울산광역시": "울산", "세종특별자치시": "세종",
    "경기도": "경기", "강원특별자치도": "강원", "강원도": "강원", "충청북도": "충북", "충청남도": "충남",
    "전북특별자치도": "전북", "전라북도": "전북", "전라남도": "전남", "경상북도": "경북",
    "경상남도": "경남", "제주특별자치도": "제주", "제주도": "제주"
}

def apply_sido_mapping(name):
    if not isinstance(name, str): return ""
    parts = name.split()
    if len(parts) >= 2:
        sido = parts[0]
        sigungu = parts[1]
        for k, v in mapping_dict.items():
            if sido == k:
                sido = v
        return f"{sido} {sigungu}"
    return name

summary['norm_region'] = summary['norm_region'].apply(apply_sido_mapping)
summary = summary.groupby('norm_region').sum(numeric_only=True).reset_index()

out_path = os.path.join(data_dir, "culture_infra_summary.csv")
summary.to_csv(out_path, index=False, encoding='utf-8')
print("Successfully saved:", out_path)
print(summary.head())
