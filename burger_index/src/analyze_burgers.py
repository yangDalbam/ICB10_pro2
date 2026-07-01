"""
이 스크립트는 추출된 burger.csv 데이터를 기반으로 브랜드명 파생변수를 생성하고,
브랜드별 지역(시도명) 및 상권업종대분류명 교차표를 작성하는 기능을 수행합니다.
"""
import pandas as pd

def main():
    file_path = r"c:\Users\user1\Downloads\ICB10_proj2\burger_index\data\burger.csv"
    
    # 데이터 불러오기
    df = pd.read_csv(file_path)
    
    # 브랜드명 파생변수 생성 함수
    def get_brand(name):
        name = str(name).lower()
        if '버거킹' in name or 'burger king' in name or 'burgerking' in name:
            return '버거킹'
        elif '맥도날드' in name or 'mcdonald' in name:
            return '맥도날드'
        elif 'kfc' in name or '케이에프씨' in name:
            return 'KFC'
        elif '롯데리아' in name or 'lotteria' in name:
            return '롯데리아'
        else:
            return '기타'
            
    df['브랜드명'] = df['상호명'].apply(get_brand)
    
    # '기타'로 분류된 데이터는 제외 (정확히 4개 브랜드만 보고 싶을 경우)
    df = df[df['브랜드명'] != '기타']
    
    # 지역별(시도명) 빈도수 교차표
    ct_region = pd.crosstab(df['시도명'], df['브랜드명'], margins=True, margins_name='총계')
    
    # 상권업종대분류명별 빈도수 교차표
    ct_category = pd.crosstab(df['상권업종대분류명'], df['브랜드명'], margins=True, margins_name='총계')
    
    report_path = r"c:\Users\user1\Downloads\ICB10_proj2\burger_index\report\crosstab.md"
    with open(report_path, "w", encoding="utf-8") as f:
        f.write("### 지역별(시도명) 브랜드 교차표\n\n")
        f.write(ct_region.to_markdown())
        f.write("\n\n### 상권업종대분류명별 브랜드 교차표\n\n")
        f.write(ct_category.to_markdown())
    
    print(f"Report saved to {report_path}")

if __name__ == "__main__":
    main()
