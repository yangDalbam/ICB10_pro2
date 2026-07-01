"""
이 스크립트는 burger.csv 파일에서 '교육' 및 '과학·기술' 업종으로 잘못 분류된 
아웃라이어(예: 축구클럽, 경영 컨설팅 회사 등) 데이터를 제거하고 파일을 덮어쓰는 기능을 수행합니다.
주요 기능:
- burger.csv 데이터 로드
- 상권업종대분류명 기준 불필요 업종 제외
- 정제된 데이터를 다시 burger.csv로 저장
"""
import pandas as pd

def main():
    file_path = r"c:\Users\user1\Downloads\ICB10_proj2\burger_index\data\burger.csv"
    
    # 데이터 로드
    df = pd.read_csv(file_path)
    original_count = len(df)
    
    # '교육', '과학·기술' 업종 제외
    df_cleaned = df[~df['상권업종대분류명'].isin(['교육', '과학·기술'])]
    cleaned_count = len(df_cleaned)
    
    # 파일 덮어쓰기
    df_cleaned.to_csv(file_path, index=False, encoding='utf-8-sig')
    
    print(f"데이터 정제 완료: {original_count}행 -> {cleaned_count}행 (제외: {original_count - cleaned_count}행)")

if __name__ == "__main__":
    main()
