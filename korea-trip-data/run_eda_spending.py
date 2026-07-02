"""
이 스크립트는 관광 소비/지출 관련 4개의 CSV 파일을 읽어 분석하고 시각화합니다.
서울, 부산, 제주를 제외한 관광 총 소비 규모 Top 5 지역을 도출하고 10종의 시각화를 생성합니다.
"""

import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib
import os
import json
import io

BASE_DIR = r"c:\Users\user1\Downloads\ICB10_proj2\korea-trip-data"
DATA_DIR = os.path.join(BASE_DIR, "data")
IMG_DIR = os.path.join(BASE_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

files = {
    "신용카드": os.path.join(DATA_DIR, "20260702202129_전체 외국인 신용카드 관광소비액 및 증감률 CSV 다운로드.csv"),
    "간편결제": os.path.join(DATA_DIR, "20260702202154_관광객 간편결제 업종별 관광소비 추이.csv"),
    "지출액": os.path.join(DATA_DIR, "20260702202516_관광지출액.csv"),
    "지역방문자지출": os.path.join(DATA_DIR, "20260702202616_지역 방문자수_관광지출액 추세.csv")
}

def load_data():
    data = {}
    for key, path in files.items():
        try:
            df = pd.read_csv(path, encoding='utf-8')
        except:
            df = pd.read_csv(path, encoding='cp949')
        data[key] = df
    return data

def get_df_info(df):
    buf = io.StringIO()
    df.info(buf=buf)
    return buf.getvalue()

def process_eda(data):
    results = {}
    
    for key, df in data.items():
        info = get_df_info(df)
        shape = list(df.shape)
        duplicates = int(df.duplicated().sum())
        head = df.head(5).to_dict(orient='records')
        tail = df.tail(5).to_dict(orient='records')
        
        desc_num = df.describe().to_dict() if not df.select_dtypes(include='number').empty else {}
        desc_cat = df.describe(include=['object', 'category']).to_dict() if not df.select_dtypes(include=['object', 'category']).empty else {}
        
        results[key] = {
            "info": info,
            "shape": shape,
            "duplicates": duplicates,
            "head": head,
            "tail": tail,
            "desc_num": desc_num,
            "desc_cat": desc_cat,
        }
        
    # 특별 필터링 로직: 서울, 부산, 제주 제외하고 Top 5 지역 추출
    df_spend = data['지출액'].copy()
    excludes = ['서울', '부산', '제주']
    df_spend_filtered = df_spend[~df_spend['시도명'].str.contains('|'.join(excludes))]
    
    top5_spend = df_spend_filtered.sort_values('관광지출액', ascending=False).head(5)
    results['top5_spend'] = top5_spend.to_dict(orient='records')
    
    return results

def generate_visualizations(data):
    plt.rc('font', family='Malgun Gothic')
    plt.rcParams['axes.unicode_minus'] = False
    
    plots = []
    
    # 1. 월별 신용카드 전체 소비액 추이 (선 그래프)
    df_credit = data['신용카드'].copy()
    df_credit['기준년월'] = df_credit['기준년월'].astype(str).str[:4] + '-' + df_credit['기준년월'].astype(str).str[4:]
    df_credit = df_credit.sort_values('기준년월')
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df_credit['기준년월'], df_credit['조회기간 소비액'], marker='o', color='teal', label='소비액')
    ax.set_title('월별 신용카드 전체 소비액 추이')
    ax.set_xlabel('기준년월')
    ax.set_ylabel('조회기간 소비액')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    img_path = 'images/plot11_credit_trend.png'
    plt.savefig(os.path.join(BASE_DIR, img_path), bbox_inches='tight')
    plt.close()
    plots.append({"id": 11, "path": img_path, "type": "선 그래프", "title": "월별 신용카드 소비액 추이"})

    # 2. 월별 신용카드 소비액 전년 대비 증감률 (막대 그래프)
    fig, ax = plt.subplots(figsize=(10, 6))
    colors = ['crimson' if x > 0 else 'cornflowerblue' for x in df_credit['전년대비 증감 비율']]
    ax.bar(df_credit['기준년월'], df_credit['전년대비 증감 비율'], color=colors)
    ax.set_title('월별 신용카드 소비액 전년 대비 증감률(%)')
    ax.set_xlabel('기준년월')
    ax.set_ylabel('전년대비 증감 비율(%)')
    plt.xticks(rotation=45)
    img_path = 'images/plot12_credit_growth.png'
    plt.savefig(os.path.join(BASE_DIR, img_path), bbox_inches='tight')
    plt.close()
    plots.append({"id": 12, "path": img_path, "type": "막대 그래프", "title": "월별 신용카드 소비액 증감률"})

    # 3. 간편결제 업종별 관광소비 비중 (파이 차트)
    df_easy = data['간편결제'].copy()
    df_easy = df_easy[df_easy['업종'] != '전체']
    df_easy_total = df_easy.groupby('업종')['소비금액(천원)'].sum().reset_index()
    
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(df_easy_total['소비금액(천원)'], labels=df_easy_total['업종'], autopct='%1.1f%%', startangle=90, colors=plt.cm.Pastel1.colors)
    ax.set_title('간편결제 업종별 관광소비 비중')
    img_path = 'images/plot13_easy_pay_pie.png'
    plt.savefig(os.path.join(BASE_DIR, img_path), bbox_inches='tight')
    plt.close()
    plots.append({"id": 13, "path": img_path, "type": "파이 차트", "title": "간편결제 업종별 관광소비 비중"})

    # 4. 업종별 간편결제 소비 추이 비교 (다중 선 그래프)
    df_easy['기준년월'] = df_easy['기준년월'].astype(str).str[:4] + '-' + df_easy['기준년월'].astype(str).str[4:]
    fig, ax = plt.subplots(figsize=(12, 6))
    for category in df_easy['업종'].unique():
        subset = df_easy[df_easy['업종'] == category].sort_values('기준년월')
        ax.plot(subset['기준년월'], subset['소비금액(천원)'], marker='s', label=category)
    ax.set_title('업종별 간편결제 소비 추이 비교')
    ax.set_xlabel('기준년월')
    ax.set_ylabel('소비금액(천원)')
    plt.xticks(rotation=45)
    ax.legend(title='업종', bbox_to_anchor=(1.05, 1), loc='upper left')
    plt.grid(True, alpha=0.3)
    img_path = 'images/plot14_easy_pay_trend.png'
    plt.savefig(os.path.join(BASE_DIR, img_path), bbox_inches='tight')
    plt.close()
    plots.append({"id": 14, "path": img_path, "type": "다중 선 그래프", "title": "업종별 간편결제 소비 추이"})

    # 5. 서울/부산/제주 제외 관광지출액 Top 5 지역 (가로 막대 그래프)
    df_spend = data['지출액'].copy()
    excludes = ['서울', '부산', '제주']
    df_spend_filtered = df_spend[~df_spend['시도명'].str.contains('|'.join(excludes))]
    top5_spend = df_spend_filtered.sort_values('관광지출액', ascending=False).head(5).sort_values('관광지출액', ascending=True)
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.barh(top5_spend['시도명'], top5_spend['관광지출액'], color='mediumpurple')
    ax.set_title('관광지출액 Top 5 지역 (서울, 부산, 제주 제외)')
    ax.set_xlabel('관광지출액')
    img_path = 'images/plot15_top5_regions.png'
    plt.savefig(os.path.join(BASE_DIR, img_path), bbox_inches='tight')
    plt.close()
    plots.append({"id": 15, "path": img_path, "type": "가로 막대 그래프", "title": "관광지출액 Top 5 지역 (주요 3개 시도 제외)"})

    # 6. Top 5 지역의 전년 대비 관광지출액 비교 (그룹 막대 그래프)
    top5_compare = top5_spend.set_index('시도명')[['관광지출액', '전년도 관광지출액']]
    fig, ax = plt.subplots(figsize=(10, 6))
    top5_compare.plot(kind='bar', ax=ax, color=['mediumpurple', 'lightgrey'])
    ax.set_title('Top 5 지역 전년 대비 관광지출액 비교')
    ax.set_ylabel('지출액')
    plt.xticks(rotation=0)
    img_path = 'images/plot16_top5_growth.png'
    plt.savefig(os.path.join(BASE_DIR, img_path), bbox_inches='tight')
    plt.close()
    plots.append({"id": 16, "path": img_path, "type": "그룹 막대 그래프", "title": "Top 5 지역 전년비 지출액 비교"})

    # 7. 방문자수 대비 관광지출액 산점도 (지역방문자지출)
    df_region = data['지역방문자지출'].copy()
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(df_region['방문자수'], df_region['관광지출액'], color='coral', alpha=0.6, edgecolors='w', s=80)
    ax.set_title('방문자수 대비 관광지출액 산점도')
    ax.set_xlabel('방문자수')
    ax.set_ylabel('관광지출액')
    img_path = 'images/plot17_scatter_visit_spend.png'
    plt.savefig(os.path.join(BASE_DIR, img_path), bbox_inches='tight')
    plt.close()
    plots.append({"id": 17, "path": img_path, "type": "산점도", "title": "방문자수 vs 관광지출액 산점도"})

    # 8. 지역별 관광지출액 비중 (Top 5 내) (도넛 차트)
    fig, ax = plt.subplots(figsize=(8, 8))
    wedges, texts, autotexts = ax.pie(top5_spend['관광지출액'], labels=top5_spend['시도명'], autopct='%1.1f%%', 
                                      startangle=90, pctdistance=0.85, colors=plt.cm.Set3.colors)
    centre_circle = plt.Circle((0,0),0.70,fc='white')
    fig.gca().add_artist(centre_circle)
    ax.set_title('Top 5 지역 내 관광지출액 비중 (도넛 차트)')
    img_path = 'images/plot18_top5_pie.png'
    plt.savefig(os.path.join(BASE_DIR, img_path), bbox_inches='tight')
    plt.close()
    plots.append({"id": 18, "path": img_path, "type": "도넛 차트", "title": "Top 5 지역 지출액 비율"})

    # 9. 전체 지출액 및 방문자수 추이 비교 (이중 Y축 선 차트)
    df_region_grouped = df_region.groupby('기준연월')[['방문자수', '관광지출액']].sum().reset_index()
    df_region_grouped['기준연월'] = df_region_grouped['기준연월'].astype(str).str[:4] + '-' + df_region_grouped['기준연월'].astype(str).str[4:]
    df_region_grouped = df_region_grouped.sort_values('기준연월')
    
    fig, ax1 = plt.subplots(figsize=(10, 6))
    color1 = 'tab:blue'
    ax1.set_xlabel('기준연월')
    ax1.set_ylabel('총 방문자수', color=color1)
    ax1.plot(df_region_grouped['기준연월'], df_region_grouped['방문자수'], color=color1, marker='o', label='방문자수')
    ax1.tick_params(axis='y', labelcolor=color1)
    
    ax2 = ax1.twinx()
    color2 = 'tab:red'
    ax2.set_ylabel('총 관광지출액', color=color2)
    ax2.plot(df_region_grouped['기준연월'], df_region_grouped['관광지출액'], color=color2, marker='^', linestyle='dashed', label='관광지출액')
    ax2.tick_params(axis='y', labelcolor=color2)
    
    fig.tight_layout()
    plt.title('전체 지출액 및 방문자수 추이 비교 (이중 Y축)')
    img_path = 'images/plot19_total_spend_visit.png'
    plt.savefig(os.path.join(BASE_DIR, img_path), bbox_inches='tight')
    plt.close()
    plots.append({"id": 19, "path": img_path, "type": "이중 Y축 선 차트", "title": "방문자수 및 지출액 시계열 비교"})

    # 10. 방문자수 증감률 분포 (히스토그램)
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.hist(df_region['방문자수 증감률'].dropna(), bins=20, color='gold', edgecolor='black')
    ax.set_title('지역별 방문자수 증감률 분포')
    ax.set_xlabel('방문자수 증감률(%)')
    ax.set_ylabel('빈도')
    img_path = 'images/plot20_visit_growth_hist.png'
    plt.savefig(os.path.join(BASE_DIR, img_path), bbox_inches='tight')
    plt.close()
    plots.append({"id": 20, "path": img_path, "type": "히스토그램", "title": "방문자수 증감률 빈도 분포"})

    return plots

def main():
    data = load_data()
    results = process_eda(data)
    plots = generate_visualizations(data)
    
    output = {
        "dataset_stats": results,
        "plots": plots
    }
    
    with open(os.path.join(BASE_DIR, "report_spending_data.json"), "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
