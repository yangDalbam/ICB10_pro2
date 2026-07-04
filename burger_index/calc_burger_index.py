"""
이 모듈은 시군구별 버거킹, 맥도날드, KFC, 롯데리아 점포수 데이터를 기반으로
버거지수((버거킹 + 맥도날드 + KFC) / 롯데리아) 파생변수를 계산하고 결과를 저장합니다.
"""

import pandas as pd
import numpy as np

file_path = 'burger_index/report/sigungu_crosstab.csv'
df = pd.read_csv(file_path)

# 버거지수 계산: (버거킹 + 맥도날드 + KFC) / 롯데리아
# 롯데리아 점포수가 0인 경우 inf가 발생하는 것을 방지하기 위해 예외처리 (0으로 설정)
df['버거지수'] = np.where(df['롯데리아'] == 0, 0, (df['버거킹'] + df['맥도날드'] + df['KFC']) / df['롯데리아'])

# 파일 저장 (한글 깨짐 방지를 위해 utf-8-sig 사용)
df.to_csv(file_path, index=False, encoding='utf-8-sig')

print("버거지수 계산이 완료되었고 파일이 업데이트되었습니다.")
