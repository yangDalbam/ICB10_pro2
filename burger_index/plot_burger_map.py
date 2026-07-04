"""
이 모듈은 시군구별 위도 및 경도 중간값과 버거지수를 활용하여
대한민국 지도 위에 산점도를 Matplotlib을 통해 시각화합니다.
"""

import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib
import mplcursors
import matplotlib

# 데이터 로드
file_path = 'burger_index/report/sigungu_crosstab.csv'
df = pd.read_csv(file_path)

# 결측치 제거 (위도, 경도 없는 데이터)
df = df.dropna(subset=['위도', '경도', '버거지수'])

# 산점도 그리기 설정
fig, ax = plt.subplots(figsize=(10, 12))

# x축: 경도, y축: 위도, 크기: 버거지수 비례, 색상: 버거지수에 따른 변화
# 버거지수가 0인 경우를 대비해 약간의 기본 크기를 더해줌
sizes = (df['버거지수'] + 0.1) * 150 

scatter = ax.scatter(
    df['경도'], 
    df['위도'], 
    s=sizes, 
    c=df['버거지수'], 
    cmap='Reds', # 버거지수가 클수록 진한 붉은색
    alpha=0.8, 
    edgecolors='w', 
    linewidth=0.5
)

# 제목 및 축 레이블 설정
ax.set_title('대한민국 시군구별 버거지수 분포', fontsize=16, pad=15)
ax.set_xlabel('경도', fontsize=12)
ax.set_ylabel('위도', fontsize=12)

# 범례(colorbar) 추가
cbar = plt.colorbar(scatter, ax=ax)
cbar.set_label('버거지수 (크기 및 색상 기준)', fontsize=12)

# 배경을 연한 회색으로 하여 점들이 돋보이게 함
ax.set_facecolor('#f4f4f4')
ax.grid(True, linestyle='--', alpha=0.5)

# 마우스 오버 시 표시할 내용 설정 (mplcursors 활용)
cursor = mplcursors.cursor(scatter, hover=True)
@cursor.connect("add")
def on_add(sel):
    idx = sel.index
    row = df.iloc[idx]
    sigungu = row['시도시군구명']
    burger_idx = row['버거지수']
    
    text = f"{sigungu}\n버거지수: {burger_idx:.2f}"
    sel.annotation.set_text(text)
    sel.annotation.get_bbox_patch().set(fc="white", alpha=0.9)

# 레이아웃 조정 및 이미지 저장
plt.tight_layout()
image_path = 'burger_index/images/burger_index_map_scatter.png'
plt.savefig(image_path, dpi=300)
print(f"산점도 이미지를 {image_path} 로 저장했습니다.")