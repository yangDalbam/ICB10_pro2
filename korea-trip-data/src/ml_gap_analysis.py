"""
이 모듈은 한국 로컬 도시(서울, 부산, 제주 제외)의 관광 데이터를 바탕으로, 
외국인들의 '관광 관심도'와 '실제 방문수'의 불일치(Gap) 요인을 머신러닝 및 SHAP으로 분석합니다.
주요 기능:
- 데이터 전처리 및 파생변수(Gap_Index) 생성
- RandomForest/XGBoost Regressor 모델 학습 및 평가
- SHAP (Shapley Additive exPlanations) 기반 특성 중요도 해석 및 시각화
"""

import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib  # 한글 폰트 깨짐 방지용
import shap

from sklearn.model_selection import train_test_split
from sklearn.preprocessing import MinMaxScaler
from sklearn.ensemble import RandomForestRegressor
from sklearn.metrics import mean_squared_error, r2_score
import xgboost as xgb

def prepare_data(df: pd.DataFrame) -> pd.DataFrame:
    """
    데이터 전처리 및 Gap_Index 파생변수 생성 함수.
    
    Args:
        df (pd.DataFrame): 원본 데이터프레임
            - 필수 컬럼: '시군구명', 'SNS_검색건수', '네비게이션_검색건수', 
                        '외국인_방문객수', '외국인_관광지출액', 'OTA_등록상품수', 
                        'OTA_만족도', '추천_여행지수', '지역별_축제수', '문화시설수'
    
    Returns:
        pd.DataFrame: 스케일링 및 Gap_Index가 추가된 데이터프레임
    """
    # 원본 데이터 보호를 위해 복사본 사용
    data = df.copy()
    
    # 서울, 부산, 제주 제외 로직 (만약 아직 제외되지 않은 경우를 대비)
    # 실제 적용 시에는 시군구명이나 시도명 컬럼을 기준으로 필터링을 수행할 수 있습니다.
    # ex) data = data[~data['시도명'].isin(['서울', '부산', '제주'])]
    
    # 1. MinMax 스케일링 수행
    # 'SNS_검색건수'(관심도)와 '외국인_방문객수'(실제 방문)를 0~1 사이로 스케일링
    scaler = MinMaxScaler()
    data[['Scaled_SNS', 'Scaled_Visit']] = scaler.fit_transform(
        data[['SNS_검색건수', '외국인_방문객수']]
    )
    
    # 2. 관광 전환 실패 지수 (Gap_Index) 생성
    # 공식: 표준화된_SNS_검색건수 - 표준화된_외국인_방문객수
    # Gap_Index가 양수로 클수록: 관심(SNS)은 높으나 실제 방문은 적은 "전환 실패" 지역
    data['Gap_Index'] = data['Scaled_SNS'] - data['Scaled_Visit']
    
    return data


def train_and_evaluate_model(df: pd.DataFrame, target_col='Gap_Index'):
    """
    RandomForest/XGBoost를 활용하여 모델을 학습하고 평가하는 함수.
    
    Args:
        df (pd.DataFrame): 전처리가 완료된 데이터프레임
        target_col (str): 예측할 타겟 변수명 (기본값: 'Gap_Index')
        
    Returns:
        model: 학습된 머신러닝 모델
        X_train, X_test: 학습 및 테스트 독립변수
        y_train, y_test: 학습 및 테스트 종속변수
    """
    # 1. 독립변수(X)와 종속변수(y) 정의
    feature_cols = [
        'OTA_등록상품수', 'OTA_만족도', '추천_여행지수', 
        '지역별_축제수', '문화시설수'
    ]
    
    # 결측치 처리 (간단히 0으로 대체, 필요시 평균/중앙값 대치 가능)
    X = df[feature_cols].fillna(0)
    y = df[target_col]
    
    # 2. Train / Test 데이터 분리 (8:2 비율)
    X_train, X_test, y_train, y_test = train_test_split(
        X, y, test_size=0.2, random_state=42
    )
    
    # 3. 모델 정의 및 학습 (XGBoost Regressor 활용)
    # Random Forest를 원할 경우: model = RandomForestRegressor(random_state=42)
    model = xgb.XGBRegressor(
        n_estimators=100, 
        learning_rate=0.1, 
        max_depth=5, 
        random_state=42
    )
    model.fit(X_train, y_train)
    
    # 4. 모델 예측 및 평가
    y_pred = model.predict(X_test)
    
    rmse = np.sqrt(mean_squared_error(y_test, y_pred))
    r2 = r2_score(y_test, y_pred)
    
    print("=== 머신러닝 모델 평가 결과 ===")
    print(f"RMSE (Root Mean Squared Error): {rmse:.4f}")
    print(f"R2 Score (결정계수): {r2:.4f}")
    
    return model, X_train, X_test, y_train, y_test


def plot_shap_summary(model, X_train):
    """
    SHAP (Shapley Additive exPlanations) 값을 계산하고 Summary Plot을 시각화하는 함수.
    
    Args:
        model: 학습된 머신러닝 모델 (XGBoost, RandomForest 등)
        X_train: SHAP value를 계산할 기준 데이터 (훈련 데이터 셋)
    """
    # SHAP Explainer 객체 생성 (Tree-based 모델 전용)
    explainer = shap.TreeExplainer(model)
    shap_values = explainer.shap_values(X_train)
    
    # SHAP Summary Plot 시각화
    plt.figure(figsize=(10, 6))
    
    # Streamlit 등에서 출력 시 폰트 깨짐을 방지하기 위한 설정
    # (koreanize_matplotlib 임포트 시 자동 적용되지만, 안정성을 위해 명시적 폰트 지정)
    plt.rcParams['font.family'] = 'Malgun Gothic' # 윈도우 맑은고딕 (리눅스는 'NanumGothic')
    plt.rcParams['axes.unicode_minus'] = False
    
    plt.title("관광 전환 실패(Gap Index) 유발 핵심 요인 SHAP Summary Plot", fontsize=15, pad=15)
    
    # show=False 설정 후 matplotlib fig 객체로 컨트롤 가능 (Streamlit 이식 시 st.pyplot(fig) 활용)
    shap.summary_plot(shap_values, X_train, show=False)
    
    plt.tight_layout()
    plt.show()


# ==========================================
# 실행 예시 (Streamlit이나 메인 함수에서 활용)
# ==========================================
if __name__ == "__main__":
    # 예시용 더미 데이터 생성 (실제 환경에서는 DB나 CSV에서 불러오면 됩니다)
    dummy_data = pd.DataFrame({
        '시군구명': ['경기 가평군', '강원 강릉시', '충남 천안시', '전북 전주시', '경북 경주시'],
        'SNS_검색건수': [50000, 80000, 20000, 60000, 75000],
        '네비게이션_검색건수': [30000, 50000, 15000, 40000, 45000],
        '외국인_방문객수': [1000, 5000, 500, 8000, 6000],
        '외국인_관광지출액': [100, 500, 50, 800, 600],
        'OTA_등록상품수': [10, 25, 5, 30, 20],
        'OTA_만족도': [4.2, 4.5, 3.8, 4.8, 4.6],
        '추천_여행지수': [15, 30, 10, 25, 35],
        '지역별_축제수': [2, 5, 1, 4, 3],
        '문화시설수': [3, 8, 2, 10, 7]
    })
    
    print("1. 데이터 전처리 및 Gap_Index 생성 중...")
    df_prepared = prepare_data(dummy_data)
    
    print("2. 머신러닝 모델 학습 중...")
    model, X_train, X_test, y_train, y_test = train_test_split_and_evaluate = train_and_evaluate_model(df_prepared)
    
    print("3. SHAP 시각화 생성 중...")
    plot_shap_summary(model, X_train)
