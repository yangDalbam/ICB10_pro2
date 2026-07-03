"""
이 스크립트는 한국 방문 외국인 현황 데이터를 읽어와서 각종 통계량을 계산하고 시각화 이미지를 생성합니다.
계산된 데이터는 JSON 파일로 저장되어 리포트 생성 시 활용됩니다.
주요 기능:
- 데이터 로드 및 정보 추출 (head, tail, info, shape, duplicate)
- 변수별 기술 통계 산출
- 10개 이상의 데이터 시각화 (matplotlib, koreanize-matplotlib 사용)
- 통계 결과 JSON 파일로 저장
"""

import pandas as pd
import matplotlib.pyplot as plt
import koreanize_matplotlib
import os
import json
import io

# 디렉토리 설정
BASE_DIR = r"c:\Users\user1\Downloads\ICB10_proj2\korea-trip-data"
DATA_DIR = os.path.join(BASE_DIR, "data")
IMG_DIR = os.path.join(BASE_DIR, "images")
os.makedirs(IMG_DIR, exist_ok=True)

# 파일 리스트
files = {
    "거주지": os.path.join(DATA_DIR, "20260620154411_외국인 방문자 거주지(국가).csv"),
    "국적별": os.path.join(DATA_DIR, "20260620155533_입국자 국적별 입국현황.csv"),
    "월별전체": os.path.join(DATA_DIR, "20260702201956_전체 외국인 방문자수 및 증감률 CSV 다운로드.csv"),
    "성연령별": os.path.join(DATA_DIR, "20260702211925_성_연령별 입국현황.csv"),
    "목적별": os.path.join(DATA_DIR, "20260702211937_목적별 입국현황.csv")
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
        # 기본 정보
        info = get_df_info(df)
        shape = list(df.shape)
        duplicates = int(df.duplicated().sum())
        head = df.head(5).to_dict(orient='records')
        tail = df.tail(5).to_dict(orient='records')
        
        # 기술 통계
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
    return results

def generate_visualizations(data):
    # matplotlib 설정
    plt.rc('font', family='Malgun Gothic')
    plt.rcParams['axes.unicode_minus'] = False
    
    plots = []
    
    # 1. 월별 방문자 수 추이 (월별전체)
    df_month = data['월별전체'].copy()
    # 기준년월 형변환 및 정렬
    df_month['기준년월'] = df_month['기준년월'].astype(str)
    df_month = df_month.sort_values('기준년월')
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.plot(df_month['기준년월'], df_month['조회기간 방문자 수'], marker='o', label='방문자 수', color='blue')
    ax.set_title('월별 외국인 방문자 수 추이')
    ax.set_xlabel('기준년월')
    ax.set_ylabel('방문자 수(명)')
    ax.ticklabel_format(style='plain', axis='y')
    plt.xticks(rotation=45)
    plt.grid(True, alpha=0.3)
    img_path = 'images/plot1_monthly_trend.png'
    plt.savefig(os.path.join(BASE_DIR, img_path), bbox_inches='tight')
    plt.close()
    plots.append({"id": 1, "path": img_path, "type": "선 그래프", "title": "월별 외국인 방문자 수 추이"})

    # 2. 월별 전년 대비 증감률 (월별전체)
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df_month['기준년월'], df_month['전년대비 증감 비율'], color='orange')
    ax.set_title('월별 전년대비 방문자 증감률(%)')
    ax.set_xlabel('기준년월')
    ax.set_ylabel('증감 비율(%)')
    plt.xticks(rotation=45)
    img_path = 'images/plot2_monthly_growth.png'
    plt.savefig(os.path.join(BASE_DIR, img_path), bbox_inches='tight')
    plt.close()
    plots.append({"id": 2, "path": img_path, "type": "막대 그래프", "title": "월별 전년대비 방문자 증감률"})

    # 3. 입국자 국적별 상위 10개국 (국적별)
    df_nat = data['국적별'].sort_values('입국자 수(명)', ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(12, 6))
    ax.bar(df_nat['입국자 국적'], df_nat['입국자 수(명)'], color='skyblue')
    ax.set_title('상위 10개국 입국자 수 현황')
    ax.set_xlabel('입국자 국적')
    ax.set_ylabel('입국자 수(명)')
    ax.ticklabel_format(style='plain', axis='y')
    img_path = 'images/plot3_top10_nationality.png'
    plt.savefig(os.path.join(BASE_DIR, img_path), bbox_inches='tight')
    plt.close()
    plots.append({"id": 3, "path": img_path, "type": "막대 그래프", "title": "상위 10개국 입국자 수 현황"})

    # 4. 거주지 기준 상위 국가 비율 파이차트 (거주지)
    df_res = data['거주지'].sort_values('비율(%)', ascending=False).head(10)
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.pie(df_res['비율(%)'], labels=df_res['국가명'], autopct='%1.1f%%', startangle=90)
    ax.set_title('외국인 방문자 거주지(국가) 상위 10개국 비율')
    img_path = 'images/plot4_residence_pie.png'
    plt.savefig(os.path.join(BASE_DIR, img_path), bbox_inches='tight')
    plt.close()
    plots.append({"id": 4, "path": img_path, "type": "파이 차트", "title": "방문자 거주지 상위 국가 비율"})

    # 5. 연령별 전체 승객 수 (성연령별)
    df_age = data['성연령별'].copy()
    df_age['총 승객 수'] = df_age['남성 승객 수(명)'] + df_age['여성 승객 수(명)']
    df_age = df_age.sort_values('연령 구분')
    
    fig, ax = plt.subplots(figsize=(10, 6))
    ax.bar(df_age['연령 구분'], df_age['총 승객 수'], color='purple', alpha=0.7)
    ax.set_title('연령대별 입국자 수')
    ax.set_xlabel('연령대')
    ax.set_ylabel('입국자 수(명)')
    ax.ticklabel_format(style='plain', axis='y')
    plt.xticks(rotation=45)
    img_path = 'images/plot5_age_total.png'
    plt.savefig(os.path.join(BASE_DIR, img_path), bbox_inches='tight')
    plt.close()
    plots.append({"id": 5, "path": img_path, "type": "막대 그래프", "title": "연령대별 입국자 수"})

    # 6. 연령대별 남녀 승객 수 그룹 막대 그래프 (성연령별)
    fig, ax = plt.subplots(figsize=(12, 6))
    x = range(len(df_age))
    width = 0.35
    ax.bar([i - width/2 for i in x], df_age['남성 승객 수(명)'], width, label='남성', color='royalblue')
    ax.bar([i + width/2 for i in x], df_age['여성 승객 수(명)'], width, label='여성', color='lightcoral')
    ax.set_title('연령대별 남녀 입국자 수 분포')
    ax.set_xticks(x)
    ax.set_xticklabels(df_age['연령 구분'], rotation=45)
    ax.legend()
    ax.ticklabel_format(style='plain', axis='y')
    img_path = 'images/plot6_age_gender_grouped.png'
    plt.savefig(os.path.join(BASE_DIR, img_path), bbox_inches='tight')
    plt.close()
    plots.append({"id": 6, "path": img_path, "type": "그룹 막대 그래프", "title": "연령대별 남녀 입국자 수 그룹별 현황"})

    # 7. 목적별 입국자 수 파이차트 (목적별)
    df_purp = data['목적별'].sort_values('방문자 수(명)', ascending=False)
    fig, ax = plt.subplots(figsize=(8, 8))
    # 상위 5개만 파이차트, 나머지는 기타 처리 가능하지만 데이터 수가 적으면 그냥 그림
    if len(df_purp) > 6:
        top_purp = df_purp.head(5).copy()
        other_sum = df_purp.iloc[5:]['방문자 수(명)'].sum()
        top_purp = pd.concat([top_purp, pd.DataFrame([{'목적 유형': '기타', '방문자 수(명)': other_sum}])], ignore_index=True)
        ax.pie(top_purp['방문자 수(명)'], labels=top_purp['목적 유형'], autopct='%1.1f%%', startangle=140)
    else:
        ax.pie(df_purp['방문자 수(명)'], labels=df_purp['목적 유형'], autopct='%1.1f%%', startangle=140)
    ax.set_title('방문 목적별 입국자 비율')
    img_path = 'images/plot7_purpose_pie.png'
    plt.savefig(os.path.join(BASE_DIR, img_path), bbox_inches='tight')
    plt.close()
    plots.append({"id": 7, "path": img_path, "type": "파이 차트", "title": "방문 목적별 입국자 비율"})

    # 8. 목적별 입국자 수 가로 막대 차트 (목적별)
    fig, ax = plt.subplots(figsize=(10, 6))
    df_purp_bar = df_purp.sort_values('방문자 수(명)', ascending=True)
    ax.barh(df_purp_bar['목적 유형'], df_purp_bar['방문자 수(명)'], color='seagreen')
    ax.set_title('방문 목적별 입국자 수 (명)')
    ax.set_xlabel('방문자 수(명)')
    ax.ticklabel_format(style='plain', axis='x')
    img_path = 'images/plot8_purpose_barh.png'
    plt.savefig(os.path.join(BASE_DIR, img_path), bbox_inches='tight')
    plt.close()
    plots.append({"id": 8, "path": img_path, "type": "가로 막대 그래프", "title": "방문 목적별 입국자 수(명)"})

    # 9. 연령대별 성비(남/여) 라인 차트
    fig, ax = plt.subplots(figsize=(10, 6))
    df_age['성비'] = df_age['남성 승객 수(명)'] / df_age['여성 승객 수(명)'] * 100
    ax.plot(df_age['연령 구분'], df_age['성비'], marker='^', color='darkorange')
    ax.set_title('연령대별 성비 (여성 100명 당 남성 수)')
    ax.set_ylabel('성비')
    ax.axhline(y=100, color='r', linestyle='--', alpha=0.5)
    plt.xticks(rotation=45)
    img_path = 'images/plot9_age_sex_ratio.png'
    plt.savefig(os.path.join(BASE_DIR, img_path), bbox_inches='tight')
    plt.close()
    plots.append({"id": 9, "path": img_path, "type": "선 그래프", "title": "연령대별 성비 추이"})

    # 10. 방문자수 대비 전년대비 증감 산점도
    fig, ax = plt.subplots(figsize=(8, 6))
    ax.scatter(df_month['조회기간 방문자 수'], df_month['전년대비 증감 비율'], color='crimson', s=100, alpha=0.6)
    for i, txt in enumerate(df_month['기준년월']):
        ax.annotate(txt, (df_month['조회기간 방문자 수'].iloc[i], df_month['전년대비 증감 비율'].iloc[i]))
    ax.set_title('월별 방문자 수와 증감률 간의 산점도')
    ax.set_xlabel('방문자 수(명)')
    ax.set_ylabel('전년대비 증감 비율(%)')
    ax.ticklabel_format(style='plain', axis='x')
    img_path = 'images/plot10_scatter_growth.png'
    plt.savefig(os.path.join(BASE_DIR, img_path), bbox_inches='tight')
    plt.close()
    plots.append({"id": 10, "path": img_path, "type": "산점도", "title": "월별 방문자 수 vs 증감 비율 산점도"})

    return plots

def main():
    data = load_data()
    results = process_eda(data)
    plots = generate_visualizations(data)
    
    output = {
        "dataset_stats": results,
        "plots": plots
    }
    
    with open(os.path.join(BASE_DIR, "report_data.json"), "w", encoding="utf-8") as f:
        json.dump(output, f, ensure_ascii=False, indent=2)

if __name__ == "__main__":
    main()
