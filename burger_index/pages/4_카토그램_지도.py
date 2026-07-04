"""
이 모듈은 카토그램(블록맵) 형태로 대한민국의 시군구별 버거지수를 시각화하는 Streamlit 페이지입니다.
"""

import streamlit as st
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import koreanize_matplotlib
import matplotlib.patches as patches

st.set_page_config(page_title="카토그램 지도", page_icon="🧩", layout="wide")
st.title("🧩 버거지수 카토그램 (블록맵)")
st.markdown("전국 시군구를 격자 형태로 단순화한 카토그램(Cartogram)을 통해 버거지수 분포를 직관적으로 확인합니다.")

@st.cache_data
def load_and_merge_data():
    df_map = pd.read_csv('burger_index/data/data_draw_korea.csv', index_col=0)
    df_map['매핑명'] = df_map['광역시도'] + ' ' + df_map['행정구역']
    
    df_burger = pd.read_csv('burger_index/report/sigungu_crosstab.csv')
    
    # 최근 행정구역 명칭 변경 대응
    sido_mapping = {
        '강원특별자치도': '강원도',
        '전북특별자치도': '전라북도'
    }
    def apply_mapping(x):
        for k, v in sido_mapping.items():
            if str(x).startswith(k):
                return x.replace(k, v)
        return x
        
    df_burger['매핑명'] = df_burger['시도시군구명'].apply(apply_mapping)
    
    # 데이터 병합 (카토그램 그리드 우선)
    merged = pd.merge(df_map, df_burger, on='매핑명', how='left')
    
    # 버거지수가 없는 지역은 0으로 처리 (회색 또는 가장 연한 색으로 표기됨)
    merged['버거지수'] = merged['버거지수'].fillna(0)
    return merged

df = load_and_merge_data()

# 카토그램 그리기
fig, ax = plt.subplots(figsize=(10, 14))
ax.set_facecolor('#ffffff')
ax.axis('off')

# 색상 매핑 설정 (Blues 컬러맵 적용)
cmap = plt.get_cmap('Blues')
# 0을 제외한 유효 데이터 범위 추출
valid_data = df[df['버거지수'] > 0]['버거지수']
vmin = valid_data.min() if not valid_data.empty else 0
vmax = valid_data.max() if not valid_data.empty else 1

for idx, row in df.iterrows():
    x = row['x']
    y = row['y']
    b_idx = row['버거지수']
    name = str(row['shortName'])
    
    # 색상 계산 (데이터가 없거나 0이면 연한 회색)
    if b_idx > 0:
        norm = (b_idx - vmin) / (vmax - vmin) if vmax > vmin else 0.5
        color = cmap(norm)
    else:
        color = '#f5f5f5' # 데이터 없음
        norm = 0
    
    # 사각형(블록) 그리기
    rect = patches.Rectangle((x - 0.5, y - 0.5), 1, 1, linewidth=0.5, edgecolor='darkgray', facecolor=color)
    ax.add_patch(rect)
    
    # 지역명 텍스트 추가 (배경이 진할 경우 글씨를 흰색으로)
    font_color = 'white' if norm > 0.6 and b_idx > 0 else 'black'
    
    # 두 글자 이상인 경우 줄바꿈 처리 (예: 남양주 -> 남양\n주)
    if len(name) > 2:
        display_name = name[:2] + '\n' + name[2:]
    else:
        display_name = name
        
    ax.text(x, y, display_name, ha='center', va='center', fontsize=9, color=font_color)

# 축 설정 (y축 뒤집기: 0이 위로 가도록)
ax.invert_yaxis()
ax.set_xlim(df['x'].min() - 1, df['x'].max() + 1)
ax.set_ylim(df['y'].max() + 1, df['y'].min() - 1)

# 컬러바 추가
sm = plt.cm.ScalarMappable(cmap=cmap, norm=plt.Normalize(vmin=vmin, vmax=vmax))
cbar = plt.colorbar(sm, ax=ax, shrink=0.5, aspect=20, pad=0.05)
cbar.set_label('버거지수', fontsize=12)

st.pyplot(fig)
