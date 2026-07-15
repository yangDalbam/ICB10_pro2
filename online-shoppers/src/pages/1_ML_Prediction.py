"""
이 모듈은 의사결정나무(Decision Tree)를 사용하여 고객의 구매(Revenue) 여부를 예측하고 분석하는 Streamlit 페이지입니다.
주요 기능:
- 데이터 전처리 (범주형 변수 인코딩)
- 의사결정나무 모델 학습 (하이퍼파라미터 max_depth 조절)
- 모델 분석 시각화 (Mermaid 플로우, 트리 구조 시각화, 피처 중요도)
- 모델 평가 (정확도, 정밀도, 재현율, F1, ROC-AUC 및 혼동행렬, ROC 곡선)
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import numpy as np
import os
import matplotlib.pyplot as plt
import seaborn as sns
import plotly.express as px
import plotly.graph_objects as go
from sklearn.model_selection import train_test_split
from sklearn.tree import DecisionTreeClassifier, plot_tree
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, roc_auc_score, confusion_matrix, roc_curve
from sklearn.preprocessing import LabelEncoder
from imblearn.over_sampling import SMOTE
try:
    import koreanize_matplotlib
except ImportError:
    pass

st.set_page_config(page_title="ML Revenue Prediction", layout="wide")

st.title("🤖 의사결정나무 기반 구매(Revenue) 예측 모델")
st.markdown("온라인 쇼핑몰 방문객의 데이터를 기반으로 최종 구매 여부(Revenue)를 예측합니다.")

# 1. 모델링 프로세스 시각화 (Mermaid)
st.subheader("📌 머신러닝 모델링 프로세스")
mermaid_code = """
graph LR
    A[데이터 로드] --> B[데이터 전처리<br/>범주형 인코딩]
    B --> C[데이터 분할<br/>Train/Test]
    C --> S[데이터 증강<br/>SMOTE 오버샘플링]
    S --> D[모델 학습<br/>Decision Tree]
    D --> E[모델 평가<br/>Train vs Test 및 5가지 지표]
    D --> F[모델 시각화<br/>의사결정나무 & 피처 중요도]
"""

components.html(
    f"""
    <div class="mermaid">
        {mermaid_code}
    </div>
    <script type="module">
        import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
        mermaid.initialize({{ startOnLoad: true }});
    </script>
    """,
    height=250
)
st.divider()

# 데이터 로드
@st.cache_data
def load_data():
    file_path = os.path.join(os.path.dirname(__file__), "..", "..", "data", "online_shoppers_intention.csv")
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return None

df = load_data()

if df is None:
    st.error("⚠️ 데이터를 찾을 수 없습니다. `online-shoppers/data/` 폴더에 데이터가 있는지 확인해주세요.")
    st.stop()

# 2. 데이터 전처리
@st.cache_data
def preprocess_data(data):
    df_processed = data.copy()
    
    # 범주형 컬럼 인코딩
    categorical_cols = ['Month', 'VisitorType', 'Weekend', 'Revenue']
    le_dict = {}
    
    for col in categorical_cols:
        le = LabelEncoder()
        df_processed[col] = le.fit_transform(df_processed[col].astype(str))
        le_dict[col] = le
        
    return df_processed, le_dict

df_processed, le_dict = preprocess_data(df)

# X, y 분리
X = df_processed.drop('Revenue', axis=1)
y = df_processed['Revenue']

# Train/Test Split
X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=0.2, random_state=42, stratify=y)

# 3. 사이드바 설정 (하이퍼파라미터 튜닝)
st.sidebar.header("⚙️ 하이퍼파라미터 설정")
use_smote = st.sidebar.checkbox("불균형 데이터 오버샘플링 (SMOTE)", value=True, help="SMOTE 기법을 사용하여 클래스 불균형 문제를 해결하고 구매(Revenue) 분류의 재현율(Recall)을 높입니다.")
use_class_weight = st.sidebar.checkbox("클래스 가중치 균형 조정 (Class Weight)", value=True, help="Decision Tree의 class_weight='balanced' 옵션을 사용하여 소수 클래스의 예측력을 강화합니다.")

max_depth = st.sidebar.slider(
    "의사결정나무 최대 깊이 (max_depth)", 
    min_value=1, max_value=20, value=5, step=1,
    help="트리의 최대 깊이를 설정합니다. 너무 깊으면 과적합(Overfitting)이 발생할 수 있습니다."
)

min_samples_split = st.sidebar.slider(
    "노드 분할 최소 샘플 수 (min_samples_split)",
    min_value=2, max_value=20, value=2, step=1
)

# SMOTE 적용
if use_smote:
    smote = SMOTE(random_state=42)
    X_train_resampled, y_train_resampled = smote.fit_resample(X_train, y_train)
else:
    X_train_resampled, y_train_resampled = X_train, y_train

# 4. 모델 학습
model = DecisionTreeClassifier(
    max_depth=max_depth, 
    min_samples_split=min_samples_split,
    class_weight='balanced' if use_class_weight else None,
    random_state=42
)
model.fit(X_train_resampled, y_train_resampled)

# 예측 (Test)
y_pred = model.predict(X_test)
y_proba = model.predict_proba(X_test)[:, 1]

# 예측 (Train - Overfitting 체크용)
y_train_pred = model.predict(X_train_resampled)

# 5. 모델 시각화 탭 (트리 및 피처 중요도)
tab1, tab2 = st.tabs(["🌳 의사결정나무 시각화", "📊 피처 중요도 (Feature Importance)"])

with tab1:
    st.subheader("의사결정나무 (Decision Tree) 구조")
    st.markdown("학습된 의사결정나무가 어떻게 구매 여부를 분류하는지 보여줍니다.")
    
    fig_tree, ax_tree = plt.subplots(figsize=(20, 10))
    # 트리가 너무 깊을 경우 상위 3단까지만 표시하여 가독성 확보
    plot_tree(
        model, 
        feature_names=X.columns.tolist(), 
        class_names=['No Revenue', 'Revenue'],
        filled=True, 
        rounded=True, 
        fontsize=10,
        ax=ax_tree,
        max_depth=3 if max_depth > 3 else max_depth
    )
    st.pyplot(fig_tree)
    if max_depth > 3:
        st.info("💡 트리가 너무 깊어 화면에 모두 표시하기 어렵기 때문에 상위 3개 깊이(Depth)까지만 시각화했습니다.")

with tab2:
    st.subheader("피처 중요도 (Feature Importance)")
    st.markdown("모델이 예측을 수행할 때 어떤 변수(특성)가 가장 중요한 역할을 했는지 나타냅니다.")
    
    # Feature Importance 추출
    importances = model.feature_importances_
    feat_imp_df = pd.DataFrame({
        'Feature': X.columns,
        'Importance': importances
    }).sort_values(by='Importance', ascending=True) # Plotly Bar(가로)를 위해 오름차순 정렬
    
    fig_imp = px.bar(
        feat_imp_df, 
        x='Importance', 
        y='Feature', 
        orientation='h',
        title="의사결정나무 피처 중요도",
        color='Importance',
        color_continuous_scale='Blues'
    )
    st.plotly_chart(fig_imp, use_container_width=True)

st.divider()

# 6. 모델 평가 및 시각화
st.header("📈 모델 평가 (Evaluation)")

# 평가 지표 계산 (Test)
acc_test = accuracy_score(y_test, y_pred)
prec_test = precision_score(y_test, y_pred)
rec_test = recall_score(y_test, y_pred)
f1_test = f1_score(y_test, y_pred)
roc_auc_test = roc_auc_score(y_test, y_proba)

# 평가 지표 계산 (Train)
acc_train = accuracy_score(y_train_resampled, y_train_pred)

# Train vs Test (Overfitting Check)
st.subheader("1) 과적합/과소적합 점검 (Train vs Test)")
st.markdown("훈련(Train) 데이터와 테스트(Test) 데이터의 정확도(Accuracy)를 비교하여 모델의 일반화 성능을 확인합니다.")
col_tr, col_te, col_res = st.columns([1, 1, 2])
col_tr.metric("Train Accuracy", f"{acc_train:.4f}")
col_te.metric("Test Accuracy", f"{acc_test:.4f}", delta=f"{acc_test - acc_train:.4f} (Diff)", delta_color="inverse")

# 해석 로직
diff = acc_train - acc_test
if diff > 0.1:
    fit_status = "⚠️ **과적합(Overfitting) 의심**: 훈련 데이터에 비해 테스트 데이터의 정확도가 크게 떨어집니다. `max_depth`를 줄이거나 데이터를 더 확보해야 합니다."
elif diff < -0.05:
    fit_status = "⚠️ **과소적합(Underfitting) 의심**: 모델이 데이터의 패턴을 충분히 학습하지 못했습니다. `max_depth`를 늘리거나 피처를 추가해 보세요."
else:
    fit_status = "✅ **적절한 적합(Good Fit)**: 훈련 성능과 테스트 성능의 차이가 크지 않아 일반화가 잘 된 모델입니다."

col_res.info(fit_status)

# 지표 대시보드 표시
st.subheader("2) 주요 평가 지표 (5가지, Test Data 기준)")
col1, col2, col3, col4, col5 = st.columns(5)
col1.metric("Accuracy (정확도)", f"{acc_test:.4f}")
col2.metric("Precision (정밀도)", f"{prec_test:.4f}")
col3.metric("Recall (재현율)", f"{rec_test:.4f}")
col4.metric("F1-Score", f"{f1_test:.4f}")
col5.metric("ROC-AUC", f"{roc_auc_test:.4f}")

st.markdown("""
* **Accuracy(정확도)**: 전체 예측 중 정답을 맞춘 비율
* **Precision(정밀도)**: 모델이 구매(True)라고 예측한 것 중 실제 구매한 비율
* **Recall(재현율)**: 실제 구매(True)한 사람 중 모델이 구매라고 맞춘 비율
* **F1-Score**: 정밀도와 재현율의 조화평균
* **ROC-AUC**: 분류 모델의 임계값에 따른 전반적인 성능 지표 (1에 가까울수록 우수)
""")

# 혼동 행렬 및 ROC Curve
st.subheader("3) 혼동 행렬 & ROC Curve")
col_cm, col_roc = st.columns(2)

with col_cm:
    st.markdown("**혼동 행렬 (Confusion Matrix)**")
    cm = confusion_matrix(y_test, y_pred)
    
    fig_cm, ax_cm = plt.subplots(figsize=(6, 5))
    sns.heatmap(cm, annot=True, fmt='d', cmap='Blues', 
                xticklabels=['No Revenue', 'Revenue'], 
                yticklabels=['No Revenue', 'Revenue'], ax=ax_cm)
    ax_cm.set_xlabel('Predicted')
    ax_cm.set_ylabel('Actual')
    st.pyplot(fig_cm)

with col_roc:
    st.markdown("**ROC Curve**")
    fpr, tpr, thresholds = roc_curve(y_test, y_proba)
    
    fig_roc = go.Figure()
    fig_roc.add_trace(go.Scatter(x=fpr, y=tpr, name=f"ROC Curve (AUC = {roc_auc_test:.4f})",
                                 mode='lines', line=dict(color='darkorange', width=2)))
    fig_roc.add_trace(go.Scatter(x=[0, 1], y=[0, 1], name="Random Model",
                                 mode='lines', line=dict(color='navy', width=2, dash='dash')))
    fig_roc.update_layout(
        xaxis_title='False Positive Rate',
        yaxis_title='True Positive Rate',
        showlegend=True,
        margin=dict(l=20, r=20, t=20, b=20)
    )
    st.plotly_chart(fig_roc, use_container_width=True)

st.divider()

st.header("💡 비즈니스 인사이트 및 액션 플랜 (Action Plan)")
st.markdown("""
위의 **피처 중요도(Feature Importance)** 및 **의사결정나무(Decision Tree) 분기 결과**를 종합해보면, 방문자의 최종 구매(Revenue) 여부를 결정짓는 가장 핵심적인 요소들을 파악할 수 있습니다. 이를 바탕으로 다음과 같은 비즈니스 수익화(Monetization) 극대화 액션 플랜을 제안합니다.

### 1. 페이지 가치(PageValues) 극대화 및 장바구니 최적화
머신러닝 분석 결과, **`PageValues` (방문자가 구매 전에 머문 페이지의 평균 가치)** 가 구매 예측에 가장 압도적인 기여도를 가진 최중요 특성(Feature)으로 나타났습니다. 의사결정나무의 최상단 루트 노드 역시 해당 변수를 기준으로 고객을 1차 분류합니다.
- **액션 플랜**: 높은 가치를 지닌 페이지(장바구니, 결제 프로세스, 베스트셀러 상품 상세 페이지 등)로 유도하는 깔때기(Funnel)를 최적화해야 합니다. 특히 결제 단계에서의 마찰(Friction)을 줄이기 위해 간편 결제 시스템을 강화하고, 장바구니에 도달한 유저들에게는 타임 세일 팝업이나 무료 배송 쿠폰을 넛지(Nudge) 형태로 제공하여 이탈 없이 구매를 확정 짓도록 유도해야 합니다.

### 2. 이탈률(ExitRates) 분석 및 첫 페이지 체류(Retention) 방어 전략
트리 하위 분기에서 `ExitRates`(종료율)와 `BounceRates`(반송률)가 높은 고객 그룹은 수익 전환율이 급격히 저하되는 경향을 보입니다.
- **액션 플랜**: 유입 직후 이탈이 많이 발생하는 '문제 랜딩 페이지'를 추적하여 직관적인 UI/UX로 전면 개편해야 합니다. 페이지 로딩 속도를 1초 단위로 단축하고, 화면 상단(Above the Fold)에 고객의 시선을 끄는 매력적인 프로모션 배너와 CTA(Call to Action) 버튼을 배치하여 다음 페이지로의 이동을 적극 유도해야 합니다.

### 3. 상품 집중 탐색(ProductRelated_Duration) 기반의 리타겟팅(Retargeting)
단순 정보성 페이지보다 상품 탐색 페이지 방문 횟수(`ProductRelated`)와 체류 시간(`ProductRelated_Duration`)이 길수록 실제 전환으로 이어질 확률이 높습니다.
- **액션 플랜**: 특정 상품 상세 페이지에 오래 머물렀으나 결제하지 않고 이탈한 고객은 매우 훌륭한 **'고관여 잠재 고객'** 입니다. 이 유저 풀(Pool)을 세그먼트화하여 맞춤형 리마인드 이메일, 앱 푸시 알림, 구글/메타 스폰서드 광고 등을 집행하는 타겟팅 캠페인이 필요합니다. 사용자가 유심히 살펴본 상품의 연관 상품(Cross-Selling)을 지속적으로 추천하는 시스템 고도화도 필수적입니다.

### 4. 방문 시기(Month, SpecialDay)를 고려한 시즌 맞춤 프로모션 집중
특정 월(예: 11월 블랙프라이데이 등)이나 특별한 날(`SpecialDay`)과의 근접성은 고객의 심리적 구매 장벽을 낮추는 요인이 됩니다.
- **액션 플랜**: 머신러닝 모델의 트렌드 예측을 바탕으로 특정 시즌 및 공휴일 직전에 집중적인 마케팅 예산(Budget Allocation)을 편성하는 것이 투자 대비 효율(ROI)이 높습니다. 특별한 날에 근접하여 유입되는 유저들에게 'D-Day 한정 특가', '오늘 자정 마감' 등의 FOMO(소외 불안) 마케팅 소스를 적재적소에 노출시켜 충동구매를 유도하는 팝업 전략을 수립해야 합니다.
""")
