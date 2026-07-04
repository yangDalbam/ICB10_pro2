"""
이 모듈은 Folium의 Choropleth 기능을 사용하여 GeoJSON 행정구역 경계 데이터 위에
버거지수를 단계구분도로 시각화하는 Streamlit 페이지입니다.
"""

import streamlit as st
import pandas as pd
import folium
import requests
from streamlit_folium import st_folium

st.set_page_config(page_title="행정구역 지도", page_icon="🗺️", layout="wide")
st.title("🗺️ 행정구역별 버거지수 지도 (Choropleth)")
st.markdown("2018년 기준 통계청 행정구역 GeoJSON을 바탕으로 시군구별 버거지수를 단계구분도로 표현합니다.")

@st.cache_data
def load_data():
    df = pd.read_csv('burger_index/report/sigungu_crosstab.csv')
    return df

@st.cache_data
def load_geojson():
    # 제공된 southkorea-maps GeoJSON URL (2018 Kostat)
    url = 'https://raw.githubusercontent.com/southkorea/southkorea-maps/master/kostat/2018/json/skorea-municipalities-2018-geo.json'
    r = requests.get(url)
    geo_data = r.json()
    
    # 앞 2자리 code에 따른 시도명 매핑
    sido_map = {
        '11': '서울특별시', '21': '부산광역시', '22': '대구광역시', '23': '인천광역시',
        '24': '광주광역시', '25': '대전광역시', '26': '울산광역시', '29': '세종특별자치시',
        '31': '경기도', '32': '강원특별자치도', '33': '충청북도', '34': '충청남도',
        '35': '전북특별자치도', '36': '전라남도', '37': '경상북도', '38': '경상남도',
        '39': '제주특별자치도'
    }
    
    # 원본 GeoJSON의 속성에 매핑용 'sido_sigungu' 키 추가
    for f in geo_data['features']:
        code2 = f['properties']['code'][:2]
        sido = sido_map.get(code2, '')
        name = f['properties']['name']
        f['properties']['sido_sigungu'] = f"{sido} {name}"
        
    return geo_data

df = load_data()
geo_data = load_geojson()

m = folium.Map(location=[36.5, 127.5], zoom_start=7, tiles='CartoDB positron')

# 결측치나 inf 방지 (안전하게 0 등으로 채우거나 제외)
import numpy as np
df_clean = df.replace([np.inf, -np.inf], np.nan).dropna(subset=['버거지수'])

folium.Choropleth(
    geo_data=geo_data,
    data=df_clean,
    columns=['시도시군구명', '버거지수'],
    key_on='feature.properties.sido_sigungu',
    fill_color='YlOrRd',
    fill_opacity=0.7,
    line_opacity=0.2,
    legend_name='Burger Index',
    nan_fill_color='lightgray'
).add_to(m)

st_folium(m, width=1000, height=700)
