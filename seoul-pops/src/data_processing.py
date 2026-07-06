"""
이 모듈은 서울 생활인구 데이터(LOCAL_PEOPLE_DONG_202606.zip)를 읽어와 Tidy Data 형태로 변환하고, 
데이터 타입을 최적화(downcast)한 후 Parquet 포맷으로 저장하는 기능을 수행합니다.
주요 기능:
- ZIP 파일 읽기 및 원본 데이터 정보 확인
- 성별, 연령대 컬럼 추출 및 Tidy Data(Melt) 변환
- 데이터 다운캐스트(Downcast)를 통한 메모리 최적화
- 데이터 Parquet 저장 및 info() 비교 리포트 작성
"""
import pandas as pd
import io

def memory_usage(df):
    return df.memory_usage(deep=True).sum() / 1024**2

def get_info(df):
    buf = io.StringIO()
    df.info(buf=buf)
    return buf.getvalue()

def process_data():
    print("Reading original ZIP file...")
    # 1. Read original zip file
    df_orig = pd.read_csv('seoul-pops/data/LOCAL_PEOPLE_DONG_202606.zip', index_col=False)
    
    # Capture original info
    orig_info = get_info(df_orig)
    
    # Output top 5 rows of original
    print("=== Original DataFrame Top 5 Rows ===")
    print(df_orig.head())
    print("\n")
    
    # 2. Tidy data transformation (melt)
    id_vars = ['기준일ID', '시간대구분', '행정동코드', '총생활인구수']
    value_vars = [col for col in df_orig.columns if col not in id_vars]
    
    print("Melting data...")
    df_melt = pd.melt(df_orig, id_vars=id_vars, value_vars=value_vars, var_name='성별_연령대', value_name='생활인구수')
    
    # 3. Extract 성별 and 연령대
    print("Extracting gender and age...")
    df_melt['성별'] = df_melt['성별_연령대'].str[:2]
    df_melt['연령대'] = df_melt['성별_연령대'].str[2:].str.replace('생활인구수', '')
    
    # Drop the original combined column
    df_melt = df_melt.drop('성별_연령대', axis=1)
    
    # 4. Downcast data types to reduce size
    print("Downcasting data types...")
    # Numeric columns
    df_melt['기준일ID'] = pd.to_numeric(df_melt['기준일ID'], downcast='unsigned')
    df_melt['시간대구분'] = pd.to_numeric(df_melt['시간대구분'], downcast='unsigned')
    df_melt['행정동코드'] = pd.to_numeric(df_melt['행정동코드'], downcast='unsigned')
    df_melt['총생활인구수'] = pd.to_numeric(df_melt['총생활인구수'], downcast='float')
    df_melt['생활인구수'] = pd.to_numeric(df_melt['생활인구수'], downcast='float')
    
    # Categorical columns
    df_melt['성별'] = df_melt['성별'].astype('category')
    df_melt['연령대'] = df_melt['연령대'].astype('category')
    
    # Output top 5 rows of processed
    print("=== Processed DataFrame Top 5 Rows ===")
    print(df_melt.head())
    print("\n")
    
    # 5. Save to parquet
    print("Saving to parquet...")
    parquet_path = 'seoul-pops/data/LOCAL_PEOPLE_DONG_202606.parquet'
    df_melt.to_parquet(parquet_path, engine='pyarrow', compression='snappy')
    
    # 6. Read parquet back and capture info
    print("Reading back parquet...")
    df_parquet = pd.read_parquet(parquet_path)
    parquet_info = get_info(df_parquet)
    
    # 7. Write report
    report_content = f"""# 데이터 처리 리포트 (LOCAL_PEOPLE_DONG_202606)

## 1. 전처리 내용
- 원본 `.zip` 파일을 읽어들인 후 판다스의 `melt` 함수를 이용해 Tidy Data 형태로 변환했습니다.
- 컬럼 이름에 포함되어 있던 `성별`과 `연령대`를 추출하여 별도의 카테고리형 컬럼으로 분리했습니다.
- 메모리 사용량을 줄이기 위해 숫자형 데이터는 `downcast` 옵션(`unsigned`, `float` 등)을 적용하고, 문자열 데이터는 `category` 형으로 변환했습니다.
- 처리된 데이터는 파케이(`.parquet`) 포맷으로 저장했습니다.

## 2. DataFrame 정보 비교

### 원본 DataFrame (`.zip` 로드 직후)
```text
{orig_info}
```

### 변환 후 DataFrame (`.parquet` 로드 시)
```text
{parquet_info}
```
"""
    
    with open('seoul-pops/report/data_processing_report.md', 'w', encoding='utf-8') as f:
        f.write(report_content)
        
    print("Process complete. Report saved.")

if __name__ == '__main__':
    process_data()
