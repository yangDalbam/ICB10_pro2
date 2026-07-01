"""
이 스크립트는 burger.csv 파일에서 '상호명'과 '도로명주소' 기준으로 중복된 데이터를 하나만 남기고 제거한 후,
상권업종대분류명과 브랜드명 간의 교차표를 생성하여 리포트로 저장합니다.
주요 기능:
- 중복 데이터(상호명 + 도로명주소) 제거
- 정제된 데이터를 바탕으로 브랜드명 파생변수 다시 확인
- 교차표 생성 후 markdown 파일로 저장
"""
import pandas as pd

def main():
    file_path = r"c:\Users\user1\Downloads\ICB10_proj2\burger_index\data\burger.csv"
    report_path = r"c:\Users\user1\Downloads\ICB10_proj2\burger_index\report\crosstab.md"
    
    # 1. 데이터 로드
    df = pd.read_csv(file_path)
    original_count = len(df)
    
    # 2. 중복 제거 (상호명 + 도로명주소 기준, 첫 번째 값만 유지)
    df_dedup = df.drop_duplicates(subset=['상호명', '도로명주소'], keep='first')
    dedup_count = len(df_dedup)
    
    # 3. 데이터 덮어쓰기 (정제본 유지)
    df_dedup.to_csv(file_path, index=False, encoding='utf-8-sig')
    
    # 4. 교차표 작성
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
            
    df_dedup = df_dedup.copy()
    df_dedup['브랜드명'] = df_dedup['상호명'].apply(get_brand)
    
    # 상권업종대분류명별 빈도수 교차표
    ct_category = pd.crosstab(df_dedup['상권업종대분류명'], df_dedup['브랜드명'], margins=True, margins_name='총계')
    
    # 지역별(시도명) 교차표
    ct_region = pd.crosstab(df_dedup['시도명'], df_dedup['브랜드명'], margins=True, margins_name='총계')
    
    with open(report_path, "w", encoding="utf-8") as f:
        f.write(f"### 🏢 상권업종대분류명별 브랜드 교차표 (중복 제거 완료: {dedup_count}건)\n\n")
        f.write(ct_category.to_markdown())
        f.write(f"\n\n### 📍 지역별(시도명) 브랜드 교차표\n\n")
        f.write(ct_region.to_markdown())
        
    print(f"중복 제거: {original_count}행 -> {dedup_count}행 (제거됨: {original_count - dedup_count}행)")
    print(f"리포트 업데이트 완료: {report_path}")

if __name__ == "__main__":
    main()
