"""
이 모듈은 Online Shoppers 데이터를 분석하여 Revenue 여부에 따른 고객 특성을 시각화하는 Streamlit 대시보드 애플리케이션입니다.
주요 기능:
- 데이터 로드 및 전처리
- Revenue 기준 수치형 변수의 분포 비교 시각화 (Boxplot) 및 기술 통계 요약
- Revenue 기준 범주형 변수의 비율 비교 시각화 (누적 막대 그래프) 및 교차표 제공
- 고객 구매 여정 퍼널(Funnel) 분석
- 머신러닝을 이용한 구매 여부 예측 모델(Random Forest, Gradient Boosting) 학습 및 평가
- Mermaid 시각화를 활용한 데이터 흐름 및 고객 여정 시퀀스 다이어그램 제공
"""

import streamlit as st
import streamlit.components.v1 as components
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from plotly.subplots import make_subplots
import os
from sklearn.model_selection import train_test_split
from sklearn.ensemble import RandomForestClassifier, GradientBoostingClassifier
from sklearn.metrics import accuracy_score, classification_report, confusion_matrix
from sklearn.preprocessing import LabelEncoder

st.set_page_config(page_title="Online Shoppers Dashboard", layout="wide")

st.title("🛒 Online Shoppers Purchasing Intention 대시보드")
st.markdown("Revenue(수익 발생) 여부에 따른 고객 행동 및 특성 비교 분석")

# 데이터 로드
@st.cache_data
def load_data():
    # 데이터 파일 경로 설정 (워크스페이스 구조에 맞게)
    file_path = os.path.join(os.path.dirname(__file__), "..", "data", "online_shoppers_intention.csv")
    
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        return df
    else:
        return None

df = load_data()

if df is None:
    st.error("⚠️ 데이터를 찾을 수 없습니다. `online-shoppers/data/` 폴더에 `online_shoppers_intention.csv` 파일을 추가한 후 다시 실행해주세요.")
    st.stop()

def render_mermaid(code: str, height: int = 500):
    components.html(
        f"""
        <div class="mermaid" style="display: flex; justify-content: center; background-color: white; padding: 20px; border-radius: 10px;">
            {code}
        </div>
        <script type="module">
            import mermaid from 'https://cdn.jsdelivr.net/npm/mermaid@10/dist/mermaid.esm.min.mjs';
            mermaid.initialize({{ startOnLoad: true, theme: 'default' }});
        </script>
        """,
        height=height,
        scrolling=True
    )

# 변수 분류
# (Online Shoppers Purchasing Intention 데이터셋 기준)
numeric_cols = ['Administrative', 'Administrative_Duration', 'Informational', 'Informational_Duration', 
                'ProductRelated', 'ProductRelated_Duration', 'BounceRates', 'ExitRates', 'PageValues', 'SpecialDay']
categorical_cols = ['Month', 'OperatingSystems', 'Browser', 'Region', 'TrafficType', 'VisitorType', 'Weekend']
target_col = 'Revenue'

# 탭 생성
tab1, tab2, tab3, tab4 = st.tabs(["📊 기본 EDA", "🎯 퍼널 분석", "🤖 머신러닝 예측 모델", "🗺️ 아키텍처 & 고객 여정"])

with tab1:
    # --- 1. 전체 데이터 개요 ---
    st.header("1. 전체 데이터 개요")
    col1, col2, col3 = st.columns(3)
    total_sessions = len(df)
    revenue_counts = df[target_col].value_counts()
    rev_true = revenue_counts.get(True, 0)
    
    col1.metric("총 세션 수", f"{total_sessions:,}")
    col2.metric("구매 전환 세션 (Revenue=True)", f"{rev_true:,}")
    col3.metric("구매 전환율", f"{(rev_true / total_sessions) * 100:.2f}%")
    
    st.divider()
    
    # --- 2. 수치형 변수 분석 ---
    st.header("2. 수치형 변수 탐색 (Revenue 비교)")
    st.markdown("수치형 변수들이 수익(Revenue) 발생 여부에 따라 어떤 분포 차이를 보이는지 확인합니다.")
    
    # Streamlit의 columns를 활용하여 2열 그리드로 개별 Plotly 차트 배치 (히스토그램 상단에 박스플롯 추가)
    for i in range(0, len(numeric_cols), 2):
        cols = st.columns(2)
        for j in range(2):
            if i + j < len(numeric_cols):
                col_name = numeric_cols[i + j]
                with cols[j]:
                    fig = px.histogram(
                        df, 
                        x=col_name, 
                        color=target_col, 
                        marginal="box", # 히스토그램 위에 박스플롯 배치
                        barmode="overlay",
                        color_discrete_map={True: '#1f77b4', False: '#ff7f0e'},
                        opacity=0.7,
                        title=f"{col_name} 분포"
                    )
                    fig.update_layout(height=400, showlegend=True, legend_title_text='Revenue')
                    st.plotly_chart(fig, use_container_width=True)
    
    # 기술통계표 요약
    st.subheader("📋 수치형 변수 기술 통계 요약")
    st.markdown("각 수치형 변수의 평균, 표준편차, 사분위수 등을 Revenue 여부에 따라 비교합니다.")
    
    # 변수 선택해서 볼 수 있도록 Selectbox 제공 (화면 공간 절약)
    selected_num_col = st.selectbox("상세 통계를 확인할 수치형 변수를 선택하세요:", numeric_cols)
    stats_df = df.groupby(target_col)[selected_num_col].describe()
    st.dataframe(stats_df, use_container_width=True)
    
    st.divider()
    
    # --- 3. 범주형 변수 분석 ---
    st.header("3. 범주형 변수 탐색 (Revenue 비교)")
    st.markdown("각 범주형 변수의 항목별 구매 전환율(Revenue=True의 비율)을 확인합니다.")
    
    # 서브플롯 생성 (2열 배열)
    rows_cat = (len(categorical_cols) + 1) // 2
    fig_cat = make_subplots(rows=rows_cat, cols=2, subplot_titles=categorical_cols)
    
    # 레전드 중복 방지를 위한 플래그
    show_legend_true = True
    show_legend_false = True
    
    for i, col in enumerate(categorical_cols):
        row = (i // 2) + 1
        c = (i % 2) + 1
        
        # 비율 계산을 위한 교차표 (index 단위로 normalize)
        cross_tab = pd.crosstab(df[col], df[target_col], normalize='index') * 100
        
        # 누적 막대 그래프용 데이터 추가
        for rev_val in [False, True]:
            if rev_val == True:
                show_leg = show_legend_true
                show_legend_true = False
            else:
                show_leg = show_legend_false
                show_legend_false = False
                
            if rev_val in cross_tab.columns:
                fig_cat.add_trace(
                    go.Bar(x=cross_tab.index.astype(str), y=cross_tab[rev_val], 
                           name=f'Revenue={rev_val}', showlegend=show_leg,
                           marker_color='#1f77b4' if rev_val else '#ff7f0e'),
                    row=row, col=c
                )
    
    fig_cat.update_layout(barmode='stack', height=400 * rows_cat, title_text="범주형 변수의 항목별 Revenue 비율 (100% 누적 막대)")
    st.plotly_chart(fig_cat, use_container_width=True)
    
    # 빈도 및 비율 표
    st.subheader("📋 범주형 변수 빈도 및 비율 요약")
    st.markdown("각 범주형 변수의 실제 데이터 수(Count)와 구매 전환 비율(%)을 확인합니다.")
    
    selected_cat_col = st.selectbox("상세 통계를 확인할 범주형 변수를 선택하세요:", categorical_cols)
    
    col_t1, col_t2 = st.columns(2)
    with col_t1:
        st.markdown("**빈도수 (Count)**")
        crosstab_count = pd.crosstab(df[selected_cat_col], df[target_col], margins=True, margins_name="Total")
        st.dataframe(crosstab_count, use_container_width=True)
    
    with col_t2:
        st.markdown("**비율 (%)**")
        crosstab_ratio = pd.crosstab(df[selected_cat_col], df[target_col], normalize='index') * 100
        # 스타일 적용하여 소수점 2자리와 % 기호 추가
        st.dataframe(crosstab_ratio.style.format("{:.2f}%"), use_container_width=True)

with tab2:
    st.header("🎯 고객 구매 여정 퍼널 (Funnel) 분석")
    st.markdown("고객이 웹사이트에 접속한 후 최종 구매에 이르기까지의 주요 전환 단계를 시각화합니다.")
    
    # 퍼널 단계 정의 로직
    step1_count = len(df)
    step2_count = len(df[df['ProductRelated'] > 0])
    step3_count = len(df[(df['ProductRelated'] > 0) & (df['PageValues'] > 0)])
    step4_count = len(df[df['Revenue'] == True])
    
    funnel_data = dict(
        number=[step1_count, step2_count, step3_count, step4_count],
        stage=["1. 전체 접속 (Total Sessions)", 
               "2. 상품 탐색 (Product Viewed)", 
               "3. 장바구니/결제 시도 (High Engagement)", 
               "4. 구매 완료 (Purchase)"]
    )
    
    fig_funnel = px.funnel(funnel_data, x='number', y='stage', title="이커머스 구매 전환 퍼널", opacity=0.9)
    st.plotly_chart(fig_funnel, use_container_width=True)
    
    # 퍼널 단계 설명 추가
    st.subheader("💡 퍼널 단계별 설명")
    st.info('''
    * **1단계: 전체 접속 (Total Sessions)**
        * 웹사이트에 방문한 모든 사용자 세션(총 데이터 수)을 나타냅니다.
    * **2단계: 상품 탐색 (Product Viewed)**
        * 사이트 내에서 상품 관련 페이지(`ProductRelated`)를 1번 이상 조회한 세션입니다. 상품에 관심이 있는 잠재 고객 구간입니다.
    * **3단계: 장바구니/결제 시도 (High Engagement)**
        * 단순 상품 조회를 넘어, 구매와 직결되는 가치 있는 페이지(`PageValues` > 0)에 도달한 세션입니다. (예: 장바구니 담기, 결제 프로세스 진입 등)
    * **4단계: 구매 완료 (Purchase)**
        * 최종적으로 수익(`Revenue=True`)이 발생하여 실제 구매가 완료된 최종 전환 세션입니다.
    ''')

    st.markdown("---")
    st.markdown("**📌 분석 인사이트 활용:** 각 단계별로 사용자 수가 얼마나 감소하는지 파악하여, **이탈률이 가장 높은 구간**의 UI/UX를 개선하거나 리타겟팅 마케팅 전략을 수립하는 데 활용할 수 있습니다.")

with tab3:
    st.header("🤖 머신러닝 예측 모델 (Random Forest & Boosting)")
    st.markdown("Random Forest와 Gradient Boosting 알고리즘을 사용하여 구매 여부(Revenue)를 예측하는 모델을 학습하고 성능을 평가합니다.")
    
    # 데이터 전처리
    st.subheader("1. 데이터 전처리")
    
    # 복사본 사용
    ml_df = df.copy()
    
    # 결측치 처리 (간단히 제거)
    ml_df = ml_df.dropna()
    
    # 범주형 데이터 인코딩
    le = LabelEncoder()
    cat_columns = ml_df.select_dtypes(include=['object', 'bool']).columns.tolist()
    if 'Revenue' in cat_columns:
        cat_columns.remove('Revenue')
        
    for col in cat_columns:
        ml_df[col] = le.fit_transform(ml_df[col].astype(str))
        
    # 특성과 타겟 분리
    X = ml_df.drop('Revenue', axis=1)
    y = ml_df['Revenue'].astype(int)
    
    st.write(f"전처리 완료: 특성 {X.shape[1]}개, 샘플 {X.shape[0]}개")
    
    # 하이퍼파라미터 설정 및 모델 훈련
    st.subheader("2. 모델 학습 및 평가")
    
    col1, col2 = st.columns(2)
    
    with col1:
        model_type = st.selectbox("알고리즘 선택", ["Random Forest", "Gradient Boosting"])
        test_size = st.slider("테스트 데이터 비율", 0.1, 0.5, 0.2, 0.05)
        
    with col2:
        n_estimators = st.slider("트리 개수 (n_estimators)", 10, 200, 100, 10)
        max_depth = st.slider("최대 깊이 (max_depth)", 3, 20, 5, 1)
        
    if st.button("모델 학습 시작"):
        with st.spinner('모델을 학습하고 있습니다...'):
            # 데이터 분할
            X_train, X_test, y_train, y_test = train_test_split(X, y, test_size=test_size, random_state=42, stratify=y)
            
            # 모델 선택
            if model_type == "Random Forest":
                model = RandomForestClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
            else:
                model = GradientBoostingClassifier(n_estimators=n_estimators, max_depth=max_depth, random_state=42)
                
            # 모델 훈련
            model.fit(X_train, y_train)
            
            # 예측
            y_pred = model.predict(X_test)
            
            # 평가
            acc = accuracy_score(y_test, y_pred)
            
            st.success("학습 완료!")
            
            st.markdown(f"### 모델 정확도(Accuracy): {acc:.4f}")
            
            eval_col1, eval_col2 = st.columns(2)
            
            with eval_col1:
                st.markdown("**분류 리포트 (Classification Report)**")
                report = classification_report(y_test, y_pred, output_dict=True)
                report_df = pd.DataFrame(report).transpose()
                st.dataframe(report_df.style.format("{:.4f}"))
                
            with eval_col2:
                st.markdown("**혼동 행렬 (Confusion Matrix)**")
                cm = confusion_matrix(y_test, y_pred)
                
                # Plotly로 혼동 행렬 그리기
                fig_cm = px.imshow(cm, text_auto=True, color_continuous_scale='Blues',
                                   labels=dict(x="예측값", y="실제값"),
                                   x=['False', 'True'], y=['False', 'True'])
                fig_cm.update_layout(title="Confusion Matrix")
                st.plotly_chart(fig_cm, use_container_width=True)
                
            # 피처 중요도 (Feature Importance)
            st.markdown("**특성 중요도 (Feature Importance)**")
            feature_importance = pd.DataFrame({
                'Feature': X.columns,
                'Importance': model.feature_importances_
            }).sort_values(by='Importance', ascending=False)
            
            fig_fi = px.bar(feature_importance.head(10), x='Importance', y='Feature', orientation='h',
                            title=f"Top 10 Feature Importances ({model_type})")
            fig_fi.update_layout(yaxis={'categoryorder':'total ascending'})
            st.plotly_chart(fig_fi, use_container_width=True)

with tab4:
    st.header("🗺️ 시스템 아키텍처 및 고객 여정 (Mermaid)")
    st.markdown("전체적인 데이터 흐름과 고객의 구매 여정을 다이어그램으로 시각화하여 제공합니다.")
    
    st.subheader("1. 👤 고객 구매 여정 시퀀스 다이어그램")
    st.markdown("고객이 처음 웹사이트에 방문해서부터 구매를 완료하고 데이터베이스에 기록되기까지의 과정을 보여줍니다.")
    
    sequence_code = '''
sequenceDiagram
    actor 고객
    participant 웹사이트
    participant 데이터베이스
    
    고객->>웹사이트: 1. 웹사이트 접속 (방문)
    웹사이트-->>고객: 메인 페이지 표시
    고객->>웹사이트: 2. 상품 탐색 (ProductRelated 페이지 조회)
    웹사이트->>데이터베이스: 세션 데이터 기록 (Duration 등)
    고객->>웹사이트: 3. 관심 상품 장바구니 담기 / 결제 시도 (PageValues 증가)
    웹사이트-->>고객: 결제 페이지 (Checkout)
    고객->>웹사이트: 4. 결제 완료 (Revenue=True)
    웹사이트->>데이터베이스: 최종 구매 여부 저장
    웹사이트-->>고객: 구매 완료 안내
    '''
    render_mermaid(sequence_code, height=750)
    
    st.divider()
    
    st.subheader("2. ⚙️ 데이터 분석 및 ML 파이프라인 흐름도")
    st.markdown("본 대시보드에서 사용하는 원본 데이터부터 전처리, 모델 학습 및 평가까지의 전체 파이프라인입니다.")
    
    flowchart_code = '''
graph TD
    A["Raw Data: online_shoppers_intention.csv"] --> B("데이터 전처리")
    B --> C{"결측치 제거"}
    C --> D["Label Encoding: 범주형 변수 변환"]
    D --> E["Feature X / Target y 분리"]
    E --> F["Train/Test Split"]
    F --> G["머신러닝 모델 학습"]
    G --> H["Random Forest"]
    G --> I["Gradient Boosting"]
    H --> J["모델 평가"]
    I --> J
    J --> K["Accuracy, Confusion Matrix, Classification Report"]
    K --> L(("최종 인사이트 도출"))
    
    style A fill:#f9f,stroke:#333,stroke-width:2px
    style L fill:#bbf,stroke:#f66,stroke-width:2px,color:#fff,stroke-dasharray: 5 5
    '''
    render_mermaid(flowchart_code, height=950)
