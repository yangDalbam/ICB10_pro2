"""
이 스크립트는 전국 상가 정보 CSV 파일들을 읽어 상호명에 특정 버거 브랜드(버거킹, 맥도날드, KFC, 롯데리아 등)가 포함된 데이터를 추출하고,
이를 하나의 `burger.csv` 파일로 통합 저장하는 기능을 수행합니다.
주요 기능:
- 여러 CSV 파일 순회 및 데이터 읽기
- 상호명 컬럼 기준 키워드 필터링
- 결과 데이터를 단일 CSV로 저장
"""
import os
import csv
import glob

data_dir = r"c:\Users\user1\Downloads\ICB10_proj2\burger_index\data"
output_file = os.path.join(data_dir, "burger.csv")

keywords = [
    "버거킹", "burger king", "burgerking", 
    "맥도날드", "mcdonald", 
    "kfc", "케이에프씨", 
    "롯데리아", "lotteria"
]

csv_files = glob.glob(os.path.join(data_dir, "*.csv"))
if output_file in csv_files:
    csv_files.remove(output_file)

header_written = False

with open(output_file, 'w', encoding='utf-8-sig', newline='') as f_out:
    writer = csv.writer(f_out)
    
    for file in csv_files:
        print(f"Processing {os.path.basename(file)}...")
        try:
            with open(file, 'r', encoding='utf-8') as f_in:
                reader = csv.reader(f_in)
                try:
                    header = next(reader)
                    if not header_written:
                        writer.writerow(header)
                        header_written = True
                        
                    name_idx = header.index("상호명")
                    
                    for row in reader:
                        if len(row) > name_idx:
                            store_name = row[name_idx].lower()
                            if any(k in store_name for k in keywords):
                                writer.writerow(row)
                except StopIteration:
                    pass
        except UnicodeDecodeError:
            with open(file, 'r', encoding='cp949') as f_in:
                reader = csv.reader(f_in)
                try:
                    header = next(reader)
                    if not header_written:
                        writer.writerow(header)
                        header_written = True
                        
                    name_idx = header.index("상호명")
                    
                    for row in reader:
                        if len(row) > name_idx:
                            store_name = row[name_idx].lower()
                            if any(k in store_name for k in keywords):
                                writer.writerow(row)
                except StopIteration:
                    pass
        except Exception as e:
            print(f"Error reading {file}: {e}")

print("Extraction completed. Output saved to:", output_file)
