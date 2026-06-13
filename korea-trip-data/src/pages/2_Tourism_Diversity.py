"""
전국 시군구 대상 온-오프라인 관광 데이터를 융합해 도시 유형을 매트릭스로 매핑하고, 비교 분석 대상 도시들을 선정하는 Streamlit 서브 페이지입니다.

주요 기능:
- 2x2 관심도(SNS 언급량) vs 실제 방문도(내비게이션 검색량) 사분면 산점도 시각화 (Plotly)
- 사분면 경계선 가이드 제시 및 도시 분포 확인
- 사용자의 동적 비교 대상 도시 1(성공군) 및 도시 2(잠재 개선군) 선정 기능 (st.session_state를 이용해 다른 페이지와 연동)
"""

import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.kto_api import get_area_service_demand
try:
    from src.styles import apply_custom_style
except ModuleNotFoundError:
    from styles import apply_custom_style

st.set_page_config(page_title="관광지 관심도 vs 실제 방문 매트릭스", page_icon="🧩", layout="wide")

# 커스텀 CSS 스타일 적용
apply_custom_style()

st.title("🧩 관심도 vs 실제 방문 매트릭스 및 도시 분류")
st.markdown("온라인 관심도(SNS 언급량)와 물리적 실제 방문량(내비게이션 검색량) 데이터를 기준으로 시군구별 위치를 확인하고 비교 분석할 도시를 선정합니다.")
st.markdown("---")

# 세션 상태 초기화 (기본 비교 대상 도시 세팅)
if "city_1" not in st.session_state:
    st.session_state.city_1 = "서울 마포구"
if "city_2" not in st.session_state:
    st.session_state.city_2 = "강원 삼척시"

# 데이터 로드
df_demand = get_area_service_demand("202401")

if not df_demand.empty:
    st.markdown("### 1. 시군구별 온-오프라인 매트릭스 2x2 분포")
    
    # 사분면 지표 계산 (중앙값 기준)
    median_sns = df_demand["snsMentionCo"].median()
    median_navi = df_demand["naviSearchCo"].median()
    
    # 산점도 생성
    fig = px.scatter(
        df_demand, x="snsMentionCo", y="naviSearchCo",
        color="cityType",
        hover_name="signguNm",
        text="signguNm",
        title="관광 관심도(SNS) vs 실제 방문도(내비게이션 검색)",
        labels={
            "snsMentionCo": "SNS 언급량 (온라인 관심도)", 
            "naviSearchCo": "내비게이션 검색수 (실제 방문도)",
            "cityType": "도시 유형"
        },
        color_discrete_map={"도시1": "#EF4444", "도시2": "#3B82F6", "일반": "#94A3B8"}
    )
    
    # 텍스트 라벨 가독성 조정
    fig.update_traces(
        textposition='top center', 
        marker=dict(size=14, opacity=0.85, line=dict(width=1.5, color='white'))
    )
    
    # 사분면 가이드 라인 추가 (단정한 슬레이트 색상으로 변경)
    fig.add_vline(x=median_sns, line_width=1.5, line_dash="dash", line_color="#94A3B8")
    fig.add_hline(y=median_navi, line_width=1.5, line_dash="dash", line_color="#94A3B8")
    
    fig.update_layout(
        plot_bgcolor="rgba(0,0,0,0)",
        paper_bgcolor="rgba(0,0,0,0)",
        font=dict(family="Pretendard, sans-serif", size=12),
        margin=dict(l=40, r=40, t=60, b=40),
        xaxis=dict(showgrid=True, gridcolor="#F1F5F9"),
        yaxis=dict(showgrid=True, gridcolor="#F1F5F9")
    )
    
    st.plotly_chart(fig, use_container_width=True)
    
    # 사분면 설명 UI 구성
    col_explain1, col_explain2 = st.columns(2)
    with col_explain1:
        st.markdown(f"""
        * **🟢 수직 기준선 (SNS 중앙값)**: `{median_sns:,.0f}`
        * **🟢 수평 기준선 (내비 중앙값)**: `{median_navi:,.0f}`
        """)
    with col_explain2:
        st.markdown("""
        * **🔴 도시 1 영역 (우상분면)**: 관심도와 방문도 모두 높은 성공적인 관광 거점 도시
        * **🔵 도시 2 영역 (우하분면)**: 온라인 관심은 뜨거우나 실제 방문 전환율이 저조한 잠재적 개선 도시
        """)
        
    st.markdown("---")
    
    # 비교 도시 선정 섹션
    st.markdown("### 🎯 2. 인프라 심층 비교 및 벤치마킹을 위한 도시 선정")
    st.markdown("아래 드롭다운에서 비교 분석을 수행할 대상을 선택해 주세요. 선택한 정보는 다음 페이지의 1:1 정밀 비교 화면에 반영됩니다.")
    
    # 도시 리스트 추출
    city_list = sorted(df_demand["signguNm"].unique().tolist())
    
    # selectbox로 세션 상태 갱신
    col_select1, col_select2 = st.columns(2)
    
    with col_select1:
        # 도시 1 (기본값 설정 유도)
        default_idx1 = city_list.index(st.session_state.city_1) if st.session_state.city_1 in city_list else 0
        selected_city1 = st.selectbox("📍 비교 기준 성공 도시 (도시 1 - 우상분면 권장)", city_list, index=default_idx1)
        st.session_state.city_1 = selected_city1
        
        # 선택한 도시의 간단 요약 카드
        df_c1 = df_demand[df_demand["signguNm"] == selected_city1].iloc[0]
        st.success(f"**{selected_city1}** ({df_c1['cityType']})\n\n* SNS 언급량: {df_c1['snsMentionCo']:,.0f}건\n* 내비 검색량: {df_c1['naviSearchCo']:,.0f}건")
        
    with col_select2:
        # 도시 2
        default_idx2 = city_list.index(st.session_state.city_2) if st.session_state.city_2 in city_list else 0
        selected_city2 = st.selectbox("📍 분석 및 개선 잠재 도시 (도시 2 - 우하분면 권장)", city_list, index=default_idx2)
        st.session_state.city_2 = selected_city2
        
        # 선택한 도시의 간단 요약 카드
        df_c2 = df_demand[df_demand["signguNm"] == selected_city2].iloc[0]
        st.info(f"**{selected_city2}** ({df_c2['cityType']})\n\n* SNS 언급량: {df_c2['snsMentionCo']:,.0f}건\n* 내비 검색량: {df_c2['naviSearchCo']:,.0f}건")

    st.markdown("---")
    st.info("💡 도시 선정을 마쳤다면, 왼쪽 사이드바에서 **'3_Demand_Analysis'** 페이지로 이동하여 두 도시의 1:1 비교 보고서를 확인해 보세요!")
else:
    st.error("데이터 로드 실패로 분석을 진행할 수 없습니다.")
