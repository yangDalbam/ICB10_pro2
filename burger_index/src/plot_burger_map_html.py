"""
이 모듈은 시군구별 위도 및 경도 중간값과 버거지수를 활용하여
대한민국 지도 위에 Plotly Scatter Mapbox를 통한 인터랙티브 HTML 지도를 생성합니다.
"""

import pandas as pd
import plotly.express as px

# 데이터 로드
file_path = 'burger_index/report/sigungu_crosstab.csv'
df = pd.read_csv(file_path)

# 결측치 제거 (위도, 경도 없는 데이터)
df = df.dropna(subset=['위도', '경도', '버거지수'])

# 버거지수가 0인 경우를 대비해 약간의 기본 크기를 더해줌
df['marker_size'] = (df['버거지수'] + 0.1) * 10

# Plotly Scatter Mapbox 생성
fig = px.scatter_mapbox(
    df,
    lat='위도',
    lon='경도',
    size='marker_size',
    color='버거지수',
    color_continuous_scale='Reds',
    size_max=30,
    zoom=6.2,
    center={'lat': 35.9, 'lon': 127.8},
    mapbox_style='open-street-map',
    hover_name='시도시군구명',
    hover_data={
        '버거지수': ':.2f',
        'KFC': True,
        '롯데리아': True,
        '맥도날드': True,
        '버거킹': True,
        '위도': False,
        '경도': False,
        'marker_size': False
    },
    title='대한민국 시군구별 버거지수 분포'
)

# 레이아웃 설정
fig.update_layout(
    title_text='<b>대한민국 시군구별 버거지수 분포</b>',
    title_x=0.5,
    title_font_size=20,
    margin={'r': 10, 't': 60, 'l': 10, 'b': 10},
)

# HTML 파일로 저장
html_path = 'burger_index/report/burger_index_map.html'
fig.write_html(html_path)
print(f"인터랙티브 HTML 지도를 {html_path} 로 저장했습니다.")
