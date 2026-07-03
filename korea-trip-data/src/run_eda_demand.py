"""
이 모듈은 방한 외국인의 관광 수요 및 관심도 데이터(검색건수, SNS 관심도 등)를 탐색적 데이터 분석(EDA)하는 스크립트입니다.
주요 기능:
- 시간 흐름에 따른 국내관광 관심도 추이 시각화
- 서울, 부산, 제주를 제외한 핵심 거점 광역지자체(시/도) 목적지 검색건수 Top 5 분석
- 결과값을 JSON 및 마크다운 리포트로 자동 생성
"""

import os
import json
import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib

def ensure_dir(path):
    if not os.path.exists(path):
        os.makedirs(path)

def load_csv_safe(file_path):
    try:
        return pd.read_csv(file_path, encoding='utf-8')
    except:
        return pd.read_csv(file_path, encoding='cp949')

def main():
    base_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(base_dir, 'data')
    image_dir = os.path.join(base_dir, 'images')
    ensure_dir(image_dir)

    # 1. 데이터 로드
    df_interest = load_csv_safe(os.path.join(data_dir, '20260702202543_국내관광 관심도 추이.csv'))
    df_dest = load_csv_safe(os.path.join(data_dir, '20260702202516_목적지검색건수.csv'))
    
    out_json = {}
    
    # 2. 국내관광 관심도 추이 분석
    # 기준년(월) 전처리
    df_interest['기준년(월)'] = df_interest['기준년(월)'].astype(str).apply(lambda x: f"{x[:4]}-{x[4:]}")
    
    plt.figure(figsize=(10, 5))
    plt.plot(df_interest['기준년(월)'], df_interest['관심도'], marker='o', color='purple', linewidth=2)
    plt.title('국내관광 관심도 월별 추이')
    plt.xlabel('연월')
    plt.ylabel('관심도 지수')
    plt.xticks(rotation=45)
    plt.grid(True, linestyle='--', alpha=0.6)
    plt.tight_layout()
    plot21_path = os.path.join(image_dir, 'plot21_interest_trend.png')
    plt.savefig(plot21_path, dpi=300)
    plt.close()
    
    out_json['interest_trend'] = {
        'months': df_interest['기준년(월)'].tolist(),
        'interest': df_interest['관심도'].tolist(),
        'max_interest_month': df_interest.loc[df_interest['관심도'].idxmax(), '기준년(월)'],
        'max_interest_val': df_interest['관심도'].max()
    }
    
    # 3. 광역지자체별 검색건수 Top 5 분석 (서울, 부산, 제주 제외)
    # df_dest 컬럼: 시도명, 검색건수
    excludes = ['서울', '부산', '제주']
    df_dest_filtered = df_dest[~df_dest['시도명'].str.contains('|'.join(excludes))].copy()
    
    df_top5_dest = df_dest_filtered.sort_values(by='검색건수', ascending=False).head(5)
    
    plt.figure(figsize=(10, 5))
    bars = plt.bar(df_top5_dest['시도명'], df_top5_dest['검색건수'], color='teal')
    plt.title('광역지자체 목적지 검색건수 Top 5 (서울, 부산, 제주 제외)')
    plt.xlabel('광역지자체')
    plt.ylabel('검색건수(단위: 천만)')
    # y축 단위를 억/천만 등으로 보이게 하려면 그냥 그대로 두고 tick formatter를 써도 되지만 기본 포맷 사용
    
    # 막대 위에 수치 표시
    for bar in bars:
        yval = bar.get_height()
        plt.text(bar.get_x() + bar.get_width()/2, yval, f"{int(yval):,}", ha='center', va='bottom', fontsize=10)
        
    plt.tight_layout()
    plot22_path = os.path.join(image_dir, 'plot22_top5_dest_search.png')
    plt.savefig(plot22_path, dpi=300)
    plt.close()
    
    out_json['top5_dest_search'] = df_top5_dest.to_dict(orient='records')
    
    # 4. 전체 시도별 검색건수 파이 차트 (관광 다변화 파악용)
    plt.figure(figsize=(8, 8))
    # 서울, 부산, 제주 포함 전체 대비 Top 5의 비중을 살펴봄
    plt.pie(df_dest['검색건수'], labels=df_dest['시도명'], autopct='%1.1f%%', startangle=140, colors=plt.cm.Set3.colors)
    plt.title('전국 목적지 검색건수 시도별 비중')
    plt.tight_layout()
    plot23_path = os.path.join(image_dir, 'plot23_dest_pie.png')
    plt.savefig(plot23_path, dpi=300)
    plt.close()
    
    # 결과 JSON 저장
    with open(os.path.join(base_dir, 'report_demand_data.json'), 'w', encoding='utf-8') as f:
        json.dump(out_json, f, ensure_ascii=False, indent=4)
        
    print("수요 분석 EDA 1차 완료 및 시각화 저장 성공!")

    # 5. 지역별 검색건수 (기초지자체 심층 분석)
    df_regional = load_csv_safe(os.path.join(data_dir, '20260702210628_지역별 검색건수.csv'))
    
    # 서울, 부산, 제주 제외
    excludes = ['서울', '부산', '제주']
    df_regional_filtered = df_regional[~df_regional['광역지자체'].str.contains('|'.join(excludes))].copy()
    
    # 전국 기초지자체 중 검색건수 상위 5개 추출
    top_kicho = df_regional_filtered.sort_values(by='기초지자체 검색건수', ascending=False).head(5)
    
    import numpy as np
    
    plt.figure(figsize=(10, 6))
    x_positions = np.arange(len(top_kicho))
    
    bars = plt.bar(x_positions, top_kicho['기초지자체 검색건수'], color='royalblue')
    
    labels = [f"{row['광역지자체']}\n{row['기초지자체']}" for _, row in top_kicho.iterrows()]
    plt.xticks(x_positions, labels, rotation=0)
    
    plt.title('전국 기초지자체 목적지 검색건수 Top 5 (서울, 부산, 제주 제외)')
    plt.xlabel('지역명')
    plt.ylabel('검색건수(단위: 천만)')
    
    plt.tight_layout()
    plot24_path = os.path.join(image_dir, 'plot24_top_kicho_search.png')
    plt.savefig(plot24_path, dpi=300)
    plt.close()
    
    print("기초지자체 심층 분석 시각화 완료!")

if __name__ == '__main__':
    main()
