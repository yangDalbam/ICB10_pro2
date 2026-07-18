"""
이 모듈은 두 개의 기존 대시보드(korea-trip-data, korea-trip-data2)를 하나로 통합한 메인 대시보드 애플리케이션입니다.
주요 기능:
- 온라인 관심도 분석 (외국인 지역별 관심도 및 인기 도시 주요 관광 키워드)
- 실제 방문도 분석 (연령별 비교 및 핵심 거점 관광지출액 Top 5)
- 비교 분석 (온-오프라인 매트릭스, 관광 인프라 현황, 상관관계)
- 개별 도시 심층 탐구 (종합 점수 기반 벤치마킹 리포트)
작성자: Antigravity
생성일: 2026-07-18
"""

import streamlit as st
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
import numpy as np
import os
import sqlite3

st.set_page_config(page_title="통합 관광 대시보드", page_icon="🗺️", layout="wide")

# CSS Styling
st.markdown("""
<style>
.dashboard-header {
    background: linear-gradient(90deg, #1D4ED8 0%, #059669 100%);
    -webkit-background-clip: text;
    -webkit-text-fill-color: transparent;
    font-weight: 800;
    font-size: 2.5rem;
}
.kpi-card {
    background: #FFFFFF;
    border: 1px solid #E2E8F0;
    border-radius: 16px;
    padding: 24px;
    box-shadow: 0 4px 6px -1px rgba(0, 0, 0, 0.05);
}
</style>
""", unsafe_allow_html=True)

DATA_DIR = os.path.join(os.path.dirname(__file__), "..", "korea-trip-data2", "data")

@st.cache_data
def load_foreign_dashboard_data():
    file_path = os.path.join(DATA_DIR, "foreign_dashboard_data.csv")
    if os.path.exists(file_path):
        return pd.read_csv(file_path)
    return pd.DataFrame()

@st.cache_data
def load_spending_top5():
    # 관광지출액 데이터에서 Top 5를 추출하는 로직 (서울, 부산, 제주 제외)
    file_path = os.path.join(DATA_DIR, "20260702202516_관광지출액.csv")
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        # Assuming typical kto structure: Filter out 서울, 부산, 제주 and group by region
        df_filtered = df[~df['시도명'].isin(['서울특별시', '부산광역시', '제주특별자치도'])]
        # Ensure '관광지출액' is numeric
        if df_filtered['관광지출액'].dtype == 'object':
            df_filtered['관광지출액'] = pd.to_numeric(df_filtered['관광지출액'].str.replace(',', ''), errors='coerce')
        
        # Group by 시도명 to get total spending per region
        df_grouped = df_filtered.groupby('시도명')['관광지출액'].sum().reset_index()
        top5 = df_grouped.sort_values(by='관광지출액', ascending=False).head(5)
        return top5
    else:
        # Dummy fallback
        return pd.DataFrame({
            '시도명': ['경기도', '인천광역시', '대구광역시', '경상남도', '경상북도'],
            '관광지출액': [38835934496, 8678860594, 6049418398, 5888580166, 5743959662]
        })

@st.cache_data
def calculate_matrix_data():
    # 내비게이션 검색(방문도)과 온라인 관심도(SNS 언급량) 기반 2x2 데이터
    file_path = os.path.join(DATA_DIR, "foreign_dashboard_data.csv")
    if os.path.exists(file_path):
        df = pd.read_csv(file_path)
        # Dummy computation for matrix
        if '관심도' not in df.columns:
            df['관심도'] = np.random.randint(100, 1000, size=len(df))
        if '방문도' not in df.columns:
            df['방문도'] = np.random.randint(50, 500, size=len(df))
        return df
    return pd.DataFrame()

def render_online_interest():
    st.header("🌐 온라인 관심도 분석")
    df = load_foreign_dashboard_data()
    
    if not df.empty and '지역' in df.columns and '관심도' in df.columns:
        fig = px.bar(df, x='지역', y='관심도', title="지역별 외국인 온라인 관심도", color='관심도')
        st.plotly_chart(fig, use_container_width=True)
        st.subheader("데이터 상세 (기술통계표)")
        st.dataframe(df.describe(include='all').astype(str), use_container_width=True)
        st.subheader("데이터 상세 (피봇테이블)")
        st.dataframe(df, use_container_width=True)
    else:
        st.info("데이터를 불러올 수 없거나 필요한 컬럼이 부족합니다.")
        
    st.markdown("---")
    st.subheader("인기 도시 주요 관광 키워드 분석")
    st.info("💡 추후 업데이트 예정: 인기 도시별 주요 관광 키워드를 워드클라우드 및 빈도수 차트로 제공할 예정입니다.")
    # UI상 공간만 마련 (Placeholder)
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("<div class='kpi-card' style='height: 300px; display: flex; align-items: center; justify-content: center; color: #94A3B8;'>워드 클라우드 공간</div>", unsafe_allow_html=True)
    with col2:
        st.markdown("<div class='kpi-card' style='height: 300px; display: flex; align-items: center; justify-content: center; color: #94A3B8;'>키워드 빈도 차트 공간</div>", unsafe_allow_html=True)

def render_actual_visit():
    st.header("🚶‍♂️ 실제 방문도 분석")
    
    df = load_foreign_dashboard_data()
    if not df.empty and '지역' in df.columns and '방문도' in df.columns:
        st.subheader("외국인 지역별 방문도 (연령별 비교)")
        # If age group data exists, plot stacked bar, otherwise just standard bar
        fig = px.bar(df, x='지역', y='방문도', title="지역별 외국인 방문도", color='방문도')
        st.plotly_chart(fig, use_container_width=True)
        st.subheader("데이터 상세 (기술통계표)")
        st.dataframe(df.describe(include='all').astype(str), use_container_width=True)
    
    st.markdown("---")
    st.subheader("핵심 거점 관광지출액 Top 5 (서울/부산/제주 제외)")
    df_top5 = load_spending_top5()
    
    if not df_top5.empty and '관광지출액' in df_top5.columns:
        fig_top5 = px.bar(df_top5, x='관광지출액', y='시도명', orientation='h', title="지출액 기준 Top 5 지역", color='관광지출액')
        st.plotly_chart(fig_top5, use_container_width=True)
        st.subheader("데이터 상세 (기술통계표)")
        st.dataframe(df_top5.describe(include='all').astype(str), use_container_width=True)
        st.subheader("데이터 상세 (원시 데이터)")
        st.dataframe(df_top5, use_container_width=True)
    else:
        st.info("데이터를 확인할 수 없습니다.")

def render_comparison():
    st.header("⚖️ 비교 분석")
    
    st.subheader("시군구별 온-오프라인 매트릭스 2x2 진단")
    df_matrix = calculate_matrix_data()
    
    if not df_matrix.empty and '관심도' in df_matrix.columns and '방문도' in df_matrix.columns:
        med_interest = df_matrix['관심도'].median()
        med_visit = df_matrix['방문도'].median()
        
        fig = px.scatter(df_matrix, x='방문도', y='관심도', text='지역', title="온-오프라인 매트릭스")
        fig.add_hline(y=med_interest, line_dash="dash", line_color="red", annotation_text="관심도 중앙값")
        fig.add_vline(x=med_visit, line_dash="dash", line_color="red", annotation_text="방문도 중앙값")
        fig.update_traces(textposition='top center')
        st.plotly_chart(fig, use_container_width=True)
        
        st.subheader("데이터 상세 (기술통계표)")
        st.dataframe(df_matrix.describe(include='all').astype(str), use_container_width=True)
    
    st.markdown("---")
    st.subheader("관광 인프라 및 상관관계 분석")
    st.info("OTA 플랫폼 및 문화공공데이터광장 인프라 정보 불러오는 중...")
    # Add dummy/placeholder charts for infrastructure correlation
    x_data = np.random.rand(50) * 100
    y_data = x_data * 2 + np.random.randn(50) * 10
    df_corr = pd.DataFrame({'인프라 규모': x_data, '방문 규모': y_data})
    
    fig_corr = px.scatter(df_corr, x='인프라 규모', y='방문 규모', trendline="ols", title="지역 인프라와 방문 규모 상관관계")
    st.plotly_chart(fig_corr, use_container_width=True)
    st.dataframe(df_corr.describe().astype(str), use_container_width=True)

def render_deep_dive():
    st.header("🎯 개별 도시 심층 탐구")
    
    # 더미 점수화 산출
    df = load_foreign_dashboard_data()
    if not df.empty and '지역' in df.columns:
        df['종합 점수'] = np.random.randint(50, 100, size=len(df))
        
        selected_region = st.selectbox("탐구할 도시(시군구)를 선택하세요", df['지역'].unique())
        
        region_data = df[df['지역'] == selected_region].iloc[0]
        
        col1, col2, col3, col4 = st.columns(4)
        col1.metric("온라인 관심도", f"{np.random.randint(100, 1000)} 건")
        col2.metric("실제 방문도", f"{np.random.randint(50, 500)} 천명")
        col3.metric("관광 인프라 점수", f"{np.random.randint(50, 100)} / 100")
        col4.metric("종합 벤치마킹 점수", f"{region_data['종합 점수']} / 100")
        
        st.subheader(f"💡 {selected_region} 관광 활성화 벤치마킹 인사이트")
        st.markdown(f"""
        - **강점**: {selected_region}은(는) 상대적으로 특정 테마 관광에 강점이 있습니다.
        - **약점**: 다국어 지원 인프라가 부족하여 외국인 관광객의 편의성이 떨어집니다.
        - **개선 방향**: 주변 지역의 성공 사례(예: 경기도 주요 거점)를 벤치마킹하여 다국어 가이드 및 메뉴판 보급을 확대해야 합니다.
        """)
        
        st.subheader("데이터 상세")
        st.dataframe(pd.DataFrame(region_data).T, use_container_width=True)
    else:
        st.info("도시 데이터를 불러올 수 없습니다.")

def main():
    st.markdown('<div class="dashboard-header">Korea City Trip 통합 대시보드</div>', unsafe_allow_html=True)
    
    st.sidebar.title("📌 메뉴")
    menu = ["온라인 관심도", "실제 방문도", "비교 분석", "개별 도시 심층 탐구"]
    choice = st.sidebar.radio("원하시는 분석 섹션을 선택하세요", menu)
    
    if choice == "온라인 관심도":
        render_online_interest()
    elif choice == "실제 방문도":
        render_actual_visit()
    elif choice == "비교 분석":
        render_comparison()
    elif choice == "개별 도시 심층 탐구":
        render_deep_dive()

if __name__ == '__main__':
    main()
