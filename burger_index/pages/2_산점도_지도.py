"""
이 모듈은 Folium을 사용하여 시군구별 위/경도 중심점에 버거지수에 비례하는
산점도(CircleMarker)를 시각화하는 Streamlit 페이지입니다.
"""

import streamlit as st
import pandas as pd
import numpy as np
import folium
from streamlit_folium import st_folium

st.set_page_config(page_title="산점도 지도", page_icon="🗺️", layout="wide")
st.title("🗺️ 버거지수 산점도 지도")
st.markdown("Folium을 활용하여 각 지역의 중심점에 버거지수에 비례하는 원을 그린 산점도입니다.")

@st.cache_data
def load_data():
    df = pd.read_csv('burger_index/report/sigungu_crosstab.csv')
    df = df.dropna(subset=['위도', '경도', '버거지수'])
    return df

df = load_data()

# 지도 중심 설정 (대한민국)
center_lat, center_lon = 36.5, 127.5
m = folium.Map(location=[center_lat, center_lon], zoom_start=7, tiles='CartoDB positron')

# 컬러맵 정의 (버거지수 값에 따라 색상 변화)
import branca.colormap as cm
# 데이터의 최소/최대값에 맞춰 컬러맵 범위 지정
min_idx = df['버거지수'].min()
max_idx = df['버거지수'].max()

# 버거지수가 높은 곳은 진한 빨간색, 낮은 곳은 연한 노란색/주황색
colormap = cm.LinearColormap(colors=['#ffeda0', '#feb24c', '#f03b20', '#bd0026'], vmin=min_idx, vmax=max_idx)
colormap.caption = 'Burger Index'
colormap.add_to(m)

for idx, row in df.iterrows():
    lat = row['위도']
    lon = row['경도']
    b_index = row['버거지수']
    name = row['시도시군구명']
    
    # 원의 크기 설정 (지수가 0인 경우 최소 크기 부여)
    radius = (b_index + 0.1) * 8
    color = colormap(b_index)
    
    folium.CircleMarker(
        location=[lat, lon],
        radius=radius,
        color=color,
        fill=True,
        fill_color=color,
        fill_opacity=0.7,
        tooltip=f"{name} (버거지수: {b_index:.2f})"
    ).add_to(m)

st_folium(m, width=1000, height=700)
