"""
이 스크립트는 burger.csv 파일 내의 중복 데이터를 확인하고,
중복된 항목들이 어떻게 겹치는지 분석하여 마크다운 리포트로 출력합니다.
주요 기능:
- 상가업소번호 기준 중복 데이터 검사
- 상호명 및 도로명주소 기준 중복 데이터 검사
- 중복 내역을 burger_index/report/duplicates.md 로 저장
"""
import pandas as pd
import os

def main():
    file_path = r"c:\Users\user1\Downloads\ICB10_proj2\burger_index\data\burger.csv"
    report_path = r"c:\Users\user1\Downloads\ICB10_proj2\burger_index\report\duplicates.md"
    
    df = pd.read_csv(file_path)
    
    # 1. 상가업소번호(고유 식별자) 기준 중복
    dup_id = df[df.duplicated(subset=['상가업소번호'], keep=False)].sort_values(by='상가업소번호')
    
    # 2. 상호명 + 도로명주소 기준 중복 (ID가 달라도 같은 가게로 추정되는 경우)
    dup_address = df[df.duplicated(subset=['상호명', '도로명주소'], keep=False)].sort_values(by=['도로명주소', '상호명'])
    
    with open(report_path, 'w', encoding='utf-8') as f:
        f.write("# 🍔 햄버거 매장 데이터 중복 검사 결과\n\n")
        
        f.write("## 1. 상가업소번호 기준 중복 데이터\n")
        if dup_id.empty:
            f.write("상가업소번호 기준으로 완전히 중복된 데이터는 **없습니다**.\n\n")
        else:
            f.write(f"상가업소번호 기준 총 **{len(dup_id)}건**의 중복(원본 포함)이 발견되었습니다.\n\n")
            f.write(dup_id[['상가업소번호', '상호명', '시도명', '시군구명', '도로명주소']].to_markdown(index=False) + "\n\n")
            
        f.write("## 2. 상호명 + 도로명주소 기준 중복 데이터\n")
        f.write("> 상가업소번호(ID)는 다르지만, **이름과 주소가 완전히 동일한** 매장입니다. (폐업 후 재등록 등으로 인한 중복일 가능성이 있습니다.)\n\n")
        
        if dup_address.empty:
            f.write("이름과 주소가 겹치는 매장은 **없습니다**.\n\n")
        else:
            f.write(f"상호명과 도로명주소 기준 총 **{len(dup_address)}건**의 중복 데이터(원본 포함)가 발견되었습니다.\n\n")
            f.write(dup_address[['상가업소번호', '상호명', '시도명', '시군구명', '도로명주소']].to_markdown(index=False) + "\n\n")

    print(f"중복 분석 완료. 레포트가 {report_path}에 저장되었습니다.")

if __name__ == "__main__":
    main()
