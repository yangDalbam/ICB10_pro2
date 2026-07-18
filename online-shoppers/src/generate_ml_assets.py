"""
이 스크립트는 Online Shoppers Intention 데이터를 로드하여 EDA 시각화 및 머신러닝 분석을 수행하고,
생성된 플롯 이미지와 주요 평가 지표를 로컬 디스크에 저장하는 기능을 수행합니다.
주요 기능:
- VisitorType 등 주요 변수에 따른 결제 전환 여부 시각화
- 데이터 전처리 및 3종의 앙상블 트리 모델 학습
- 모델 성능 평가 및 피처 중요도 결과물(JSON, PNG) 저장
"""

import os
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
import koreanize_matplotlib
from sklearn.model_selection import train_test_split
from sklearn.preprocessing import LabelEncoder
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from xgboost import XGBClassifier
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, log_loss
import json

def main():
    # 경로 설정
    base_dir = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
    data_path = os.path.join(base_dir, 'online-shoppers', 'data', 'online_shoppers_intention.csv')
    reports_img_dir = os.path.join(base_dir, 'online-shoppers', 'images')
    os.makedirs(reports_img_dir, exist_ok=True)
    
    # 데이터 로드
    df = pd.read_csv(data_path)
    
    # ------------------
    # 1. EDA 파트
    # ------------------
    
    # (1) VisitorType에 따른 Revenue 교차표
    crosstab_visitor = pd.crosstab(df['VisitorType'], df['Revenue'])
    crosstab_visitor_pct = crosstab_visitor.div(crosstab_visitor.sum(1), axis=0) * 100
    
    # 교차표 딕셔너리화 (보고서용)
    eda_tables = {
        "VisitorType_Revenue": crosstab_visitor.to_dict(),
        "VisitorType_Revenue_Pct": crosstab_visitor_pct.round(2).to_dict()
    }
    
    # (2) EDA 시각화 (방문자 유형별 전환 수)
    plt.figure(figsize=(8, 6))
    sns.countplot(data=df, x='VisitorType', hue='Revenue')
    plt.title('방문자 유형별 구매 여부 (Revenue)')
    plt.xlabel('방문자 유형')
    plt.ylabel('세션 수')
    plt.tight_layout()
    eda_plot_path = os.path.join(reports_img_dir, 'visitor_revenue_countplot.png')
    plt.savefig(eda_plot_path)
    plt.close()
    
    # ------------------
    # 2. 데이터 전처리
    # ------------------
    ml_df = df.dropna().copy()
    
    le = LabelEncoder()
    cat_columns = ml_df.select_dtypes(include=['object', 'bool']).columns.tolist()
    if 'Revenue' in cat_columns:
        cat_columns.remove('Revenue')
        
    for col in cat_columns:
        ml_df[col] = le.fit_transform(ml_df[col].astype(str))
        
    X = ml_df.drop('Revenue', axis=1)
    y = ml_df['Revenue'].astype(int)
    
    X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)
    
    # ------------------
    # 3. 모델링 및 평가
    # ------------------
    models = {
        'Random Forest': RandomForestClassifier(n_estimators=100, random_state=42),
        'Gradient Boosting': GradientBoostingClassifier(n_estimators=100, random_state=42),
        'XGBoost': XGBClassifier(use_label_encoder=False, eval_metric='logloss', random_state=42)
    }
    
    results = {}
    
    for name, model in models.items():
        model.fit(X_train, y_train)
        y_pred = model.predict(X_test)
        y_proba = model.predict_proba(X_test)[:, 1]
        
        acc = accuracy_score(y_test, y_pred)
        prec = precision_score(y_test, y_pred)
        rec = recall_score(y_test, y_pred)
        f1 = f1_score(y_test, y_pred)
        roc = roc_auc_score(y_test, y_proba)
        loss = log_loss(y_test, y_proba)
        
        results[name] = {
            'Accuracy': round(acc, 4),
            'Precision': round(prec, 4),
            'Recall': round(rec, 4),
            'F1-Score': round(f1, 4),
            'ROC-AUC': round(roc, 4),
            'Log-Loss': round(loss, 4)
        }
        
    # (3) 결과 비교 시각화 (ROC-AUC 기준 바 차트)
    model_names = list(results.keys())
    roc_scores = [results[m]['ROC-AUC'] for m in model_names]
    
    plt.figure(figsize=(8, 6))
    sns.barplot(x=model_names, y=roc_scores, palette='viridis')
    plt.title('모델별 ROC-AUC 스코어 비교')
    plt.ylim(0.8, 1.0)
    for i, v in enumerate(roc_scores):
        plt.text(i, v + 0.005, str(v), ha='center')
    plt.tight_layout()
    ml_plot_path = os.path.join(reports_img_dir, 'model_comparison_roc.png')
    plt.savefig(ml_plot_path)
    plt.close()

    # (4) 피처 중요도 (XGBoost 기준)
    xgb_model = models['XGBoost']
    feature_importances = pd.Series(xgb_model.feature_importances_, index=X.columns).sort_values(ascending=False).head(10)
    
    plt.figure(figsize=(10, 6))
    sns.barplot(x=feature_importances.values, y=feature_importances.index, palette='mako')
    plt.title('XGBoost 상위 10개 피처 중요도')
    plt.tight_layout()
    fi_plot_path = os.path.join(reports_img_dir, 'xgboost_feature_importance.png')
    plt.savefig(fi_plot_path)
    plt.close()
    
    # Feature Importance 딕셔너리화 (보고서 표 생성용)
    fi_dict = feature_importances.round(4).to_dict()
    
    # ------------------
    # 4. 종합 결과 저장
    # ------------------
    summary_data = {
        'eda_tables': eda_tables,
        'model_results': results,
        'feature_importance': fi_dict,
        'image_paths': {
            'eda_plot': 'online-shoppers/images/visitor_revenue_countplot.png',
            'ml_comp_plot': 'online-shoppers/images/model_comparison_roc.png',
            'fi_plot': 'online-shoppers/images/xgboost_feature_importance.png'
        }
    }
    
    summary_path = os.path.join(base_dir, 'online-shoppers', 'report', 'ml_summary.json')
    with open(summary_path, 'w', encoding='utf-8') as f:
        json.dump(summary_data, f, ensure_ascii=False, indent=4)
        
    print(f"분석 자산 생성이 완료되었습니다. 요약 결과는 {summary_path}에 저장되었습니다.")

if __name__ == "__main__":
    main()
