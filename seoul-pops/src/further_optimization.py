"""
이 모듈은 이전에 Parquet으로 저장된 데이터를 추가로 최적화합니다.
주요 기능:
- 기준일ID, 행정동코드를 Category 타입으로 변환
- 수치형, 범주형 데이터의 기술 통계량 산출
- 수치형 데이터를 float32/float16 수준으로 추가 다운캐스팅
- 최종 최적화된 DataFrame의 info() 출력
"""
import pandas as pd
import io

def further_optimize():
    parquet_path = 'seoul-pops/data/LOCAL_PEOPLE_DONG_202606.parquet'
    print("Reading parquet file...")
    df = pd.read_parquet(parquet_path)
    
    # 1. 기준일ID, 행정동코드를 카테고리로 변경
    print("Converting 기준일ID and 행정동코드 to category...")
    df['기준일ID'] = df['기준일ID'].astype('category')
    df['행정동코드'] = df['행정동코드'].astype('category')
    
    # 2. 기술 통계 확인 (수치형, 범주형 모두)
    print("\n=== 기술 통계 (Descriptive Statistics) ===")
    desc = df.describe(include='all')
    print(desc)
    
    # 3. 추가 다운캐스트 (총생활인구수, 생활인구수 float64 -> float32)
    # Pyarrow parquet reading can default floats back to float64, let's force downcast
    print("\nFurther downcasting numeric columns...")
    df['총생활인구수'] = pd.to_numeric(df['총생활인구수'], downcast='float')
    df['생활인구수'] = pd.to_numeric(df['생활인구수'], downcast='float')
    
    # Check max values to see if float16 is possible (max float16 is ~65500, max pop might be larger)
    max_total = df['총생활인구수'].max()
    max_pop = df['생활인구수'].max()
    print(f"Max 총생활인구수: {max_total}, Max 생활인구수: {max_pop}")
    
    # If they are within float32 limits, they are float32. 
    # Can we do float32 explicitly just to be sure?
    df['총생활인구수'] = df['총생활인구수'].astype('float32')
    df['생활인구수'] = df['생활인구수'].astype('float32')
    
    # Drop '총생활인구수' as requested
    print("\nDropping '총생활인구수' column...")
    df = df.drop('총생활인구수', axis=1)
    
    # 4. info() 출력
    print("\n=== 최종 최적화(컬럼 제거) 후 DataFrame Info ===")
    buf = io.StringIO()
    df.info(buf=buf)
    print(buf.getvalue())
    
    # Write the info to a text file for easy extraction to update the report
    with open('seoul-pops/report/final_info.txt', 'w', encoding='utf-8') as f:
        f.write(buf.getvalue())
        
    # Optional: Save back to parquet (overwrite or new file)
    optimized_path = 'seoul-pops/data/LOCAL_PEOPLE_DONG_202606_optimized_final.parquet'
    df.to_parquet(optimized_path, engine='pyarrow', compression='snappy')
    print(f"Saved optimized data to {optimized_path}")

if __name__ == '__main__':
    further_optimize()
