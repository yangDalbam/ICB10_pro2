# 데이터 처리 리포트 (LOCAL_PEOPLE_DONG_202606)

## 1. 전처리 내용
- 원본 `.zip` 파일을 읽어들인 후 판다스의 `melt` 함수를 이용해 Tidy Data 형태로 변환했습니다.
- 컬럼 이름에 포함되어 있던 `성별`과 `연령대`를 추출하여 별도의 카테고리형 컬럼으로 분리했습니다.
- 메모리 사용량을 줄이기 위해 숫자형 데이터는 `downcast` 옵션(`unsigned`, `float` 등)을 적용하고, 문자열 데이터는 `category` 형으로 변환했습니다.
- 처리된 데이터는 파케이(`.parquet`) 포맷으로 저장했습니다.

## 2. DataFrame 정보 비교

### 원본 DataFrame (`.zip` 로드 직후)
```text
<class 'pandas.DataFrame'>
RangeIndex: 305280 entries, 0 to 305279
Data columns (total 32 columns):
 #   Column           Non-Null Count   Dtype  
---  ------           --------------   -----  
 0   기준일ID            305280 non-null  int64  
 1   시간대구분            305280 non-null  int64  
 2   행정동코드            305280 non-null  int64  
 3   총생활인구수           305280 non-null  float64
 4   남자0세부터9세생활인구수    305280 non-null  float64
 5   남자10세부터14세생활인구수  305280 non-null  float64
 6   남자15세부터19세생활인구수  305280 non-null  float64
 7   남자20세부터24세생활인구수  305280 non-null  float64
 8   남자25세부터29세생활인구수  305280 non-null  float64
 9   남자30세부터34세생활인구수  305280 non-null  float64
 10  남자35세부터39세생활인구수  305280 non-null  float64
 11  남자40세부터44세생활인구수  305280 non-null  float64
 12  남자45세부터49세생활인구수  305280 non-null  float64
 13  남자50세부터54세생활인구수  305280 non-null  float64
 14  남자55세부터59세생활인구수  305280 non-null  float64
 15  남자60세부터64세생활인구수  305280 non-null  float64
 16  남자65세부터69세생활인구수  305280 non-null  float64
 17  남자70세이상생활인구수     305280 non-null  float64
 18  여자0세부터9세생활인구수    305280 non-null  float64
 19  여자10세부터14세생활인구수  305280 non-null  float64
 20  여자15세부터19세생활인구수  305280 non-null  float64
 21  여자20세부터24세생활인구수  305280 non-null  float64
 22  여자25세부터29세생활인구수  305280 non-null  float64
 23  여자30세부터34세생활인구수  305280 non-null  float64
 24  여자35세부터39세생활인구수  305280 non-null  float64
 25  여자40세부터44세생활인구수  305280 non-null  float64
 26  여자45세부터49세생활인구수  305280 non-null  float64
 27  여자50세부터54세생활인구수  305280 non-null  float64
 28  여자55세부터59세생활인구수  305280 non-null  float64
 29  여자60세부터64세생활인구수  305280 non-null  float64
 30  여자65세부터69세생활인구수  305280 non-null  float64
 31  여자70세이상생활인구수     305280 non-null  float64
dtypes: float64(29), int64(3)
memory usage: 74.5 MB

```

### 변환 후 DataFrame (`.parquet` 로드 시)
```text
<class 'pandas.DataFrame'>
RangeIndex: 8547840 entries, 0 to 8547839
Data columns (total 7 columns):
 #   Column  Dtype   
---  ------  -----   
 0   기준일ID   uint32  
 1   시간대구분   uint8   
 2   행정동코드   uint32  
 3   총생활인구수  float64 
 4   생활인구수   float64 
 5   성별      category
 6   연령대     category
dtypes: category(2), float64(2), uint32(2), uint8(1)
memory usage: 220.1 MB

```

### 최종 최적화 DataFrame (`총생활인구수` 제거 및 타입 다운캐스팅 완료 시)
```text
<class 'pandas.DataFrame'>
RangeIndex: 8547840 entries, 0 to 8547839
Data columns (total 6 columns):
 #   Column  Dtype   
---  ------  -----   
 0   기준일ID   category
 1   시간대구분   uint8   
 2   행정동코드   category
 3   생활인구수   float32 
 4   성별      category
 5   연령대     category
dtypes: category(4), float32(1), uint8(1)
memory usage: 81.5 MB

```

## 3. Parquet 파일 메타데이터 정보

### 메타데이터 출력 결과
```text
<pyarrow._parquet.FileMetaData object>
  created_by: parquet-cpp-arrow version 24.0.0
  num_columns: 6
  num_rows: 8547840
  num_row_groups: 9
  format_version: 2.6
  serialized_size: 10149

=== Schema ===
<pyarrow._parquet.ParquetSchema object>
required group field_id=-1 schema {
  optional int32 field_id=-1 기준일ID (Int(bitWidth=32, isSigned=false));
  optional int32 field_id=-1 시간대구분 (Int(bitWidth=8, isSigned=false));
  optional int32 field_id=-1 행정동코드 (Int(bitWidth=32, isSigned=false));
  optional float field_id=-1 생활인구수;
  optional binary field_id=-1 성별 (String);
  optional binary field_id=-1 연령대 (String);
}
```

### 메타데이터 항목 설명
- **`created_by`**: 이 파일을 생성할 때 사용된 내부 엔진과 버전입니다. (`pyarrow`가 의존하는 C++ 라이브러리인 `parquet-cpp-arrow 24.0.0` 사용)
- **`num_columns` / `num_rows`**: 파일에 저장된 열(6개)과 행(약 854만 줄)의 총 개수입니다.
- **`num_row_groups` (로우 그룹 수 = 9개)**: 파케이(Parquet) 파일의 가장 큰 특징이자 검색 속도 최적화의 핵심입니다. 약 850만 개의 데이터를 통째로 저장하지 않고 9개의 그룹으로 잘라서(Partition) 저장했습니다. 이를 통해 특정 행정동이나 특정 시간대만 검색할 때, 해당 데이터가 없는 로우 그룹은 아예 읽지 않고 건너뛰는(Skip) 고속 처리가 가능합니다.
- **`Schema` (스키마)**: 각 컬럼이 디스크 상에 어떤 물리적 자료형으로 저장되었는지 보여줍니다.
  - `Int(bitWidth=32/8, isSigned=false)`: Pandas에서 최적화한 부호 없는 정수(`uint32`, `uint8`)가 그대로 32비트/8비트 정수로 저장되었습니다.
  - `float`: `float32` 타입이 단정밀도 실수로 매핑되었습니다.
  - `String`: Pandas의 `category` 타입 문자열이 Parquet 내부의 딕셔너리 인코딩(Dictionary Encoding) 방식으로 압축 저장(binary/String) 되었습니다.
