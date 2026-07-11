import pandas as pd

data = [
    {'지역': '인천 중구', '종합 인프라 점수': 40, '방문 규모 (검색건수)': 14000000},
    {'지역': '경기 용인시', '종합 인프라 점수': 20, '방문 규모 (검색건수)': 13500000},
    {'지역': '경기 고양시', '종합 인프라 점수': 10, '방문 규모 (검색건수)': 13000000},
    {'지역': '경기 수원시', '종합 인프라 점수': 60, '방문 규모 (검색건수)': 12500000},
    {'지역': '경기 화성시', '종합 인프라 점수': 12, '방문 규모 (검색건수)': 10000000},
    {'지역': '경기 성남시', '종합 인프라 점수': 5, '방문 규모 (검색건수)': 8500000},
    {'지역': '경기 남양주시', '종합 인프라 점수': 6, '방문 규모 (검색건수)': 8500000}, # Close to 성남
    {'지역': '충북 청주시', '종합 인프라 점수': 22, '방문 규모 (검색건수)': 7900000},
    {'지역': '경북 경주시', '종합 인프라 점수': 58, '방문 규모 (검색건수)': 6500000},
]
scatter_df = pd.DataFrame(data)

labels = []
labeled_points = []
x_max = scatter_df['종합 인프라 점수'].max() or 1
y_max = scatter_df['방문 규모 (검색건수)'].max() or 1
            
for idx, row in scatter_df.iterrows():
    nx = row['종합 인프라 점수'] / x_max
    ny = row['방문 규모 (검색건수)'] / y_max
    
    overlap = False
    for px, py in labeled_points:
        dist = ((nx - px)**2 + (ny - py)**2)**0.5
        if dist < 0.1:
            overlap = True
            break
    
    if not overlap:
        labels.append(row['지역'])
        labeled_points.append((nx, ny))
    else:
        labels.append('')

scatter_df['표시 라벨'] = labels
print(scatter_df[['지역', '표시 라벨']])
