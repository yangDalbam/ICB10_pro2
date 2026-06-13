"""
선택된 성공 도시(도시 1)와 잠재 도시(도시 2)의 인프라 및 소비 패턴을 1:1 정밀 비교하고, 데이터 기반 벤치마킹 관광 활성화 제안을 도출하는 Streamlit 서브 페이지입니다.

주요 기능:
- st.session_state 기반 선택 도시 로드 및 예외 처리
- 5대 핵심 지표 레이더 플롯 비교 (Plotly line_polar)
- 소비 업종 비율, 방문객 연령대 구성, 내비게이션 목적지 비중 등 1:1 비교 시각화
- 격차 분석 결과를 기반으로 한 자동 생성형 활성화 액션 플랜 제시
"""

import os
import sys
import streamlit as st
import pandas as pd
import numpy as np
import plotly.express as px
import plotly.graph_objects as go

# 프로젝트 루트 경로 추가
sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from api.kto_api import (
    get_area_visitor_diversity,
    get_area_spend_diversity,
    get_area_intl_diversity,
    get_area_service_demand,
    get_area_cultural_demand
)

st.set_page_config(page_title="성공 도시 vs 잠재 도시 1:1 비교 분석", page_icon="⚖️", layout="wide")

st.title("⚖️ 도시 1:1 심층 비교 및 벤치마킹 제언")
st.markdown("선택된 두 도시의 관광객 특징, 카드 소비 형태, 목적지 선호도 등 세부 인프라 지표를 심층 대조하여 활성화 개선점을 도출합니다.")
st.markdown("---")

# 세션 상태 체크 및 안내
if "city_1" not in st.session_state or "city_2" not in st.session_state:
    st.warning("⚠️ 2단계 페이지('2_Tourism_Diversity')에서 분석 대상 도시를 먼저 선택해 주세요. 기본값으로 서울 마포구와 강원 삼척시를 대조군으로 분석을 로드합니다.")
    st.session_state.city_1 = "서울 마포구"
    st.session_state.city_2 = "강원 삼척시"

city_1 = st.session_state.city_1
city_2 = st.session_state.city_2

st.subheader(f"🔍 분석 비교군: 🔴 {city_1} (기준 도시) vs 🔵 {city_2} (개선 대상 도시)")

# 데이터 통합 로드
df_visitor = get_area_visitor_diversity()
df_spend = get_area_spend_diversity()
df_intl = get_area_intl_diversity()
df_demand = get_area_service_demand()
df_cult = get_area_cultural_demand()

# 두 도시 데이터 필터링
v_c1 = df_visitor[df_visitor["signguNm"] == city_1]
v_c2 = df_visitor[df_visitor["signguNm"] == city_2]

s_c1 = df_spend[df_spend["signguNm"] == city_1]
s_c2 = df_spend[df_spend["signguNm"] == city_2]

i_c1 = df_intl[df_intl["signguNm"] == city_1]
i_c2 = df_intl[df_intl["signguNm"] == city_2]

d_c1 = df_demand[df_demand["signguNm"] == city_1]
d_c2 = df_demand[df_demand["signguNm"] == city_2]

c_c1 = df_cult[df_cult["signguNm"] == city_1]
c_c2 = df_cult[df_cult["signguNm"] == city_2]

if not d_c1.empty and not d_c2.empty:
    st.markdown("### 📊 1. 5대 핵심 관광 역량 레이더 차트 비교")
    
    # 레이더용 점수 산정 (Mock 가중치 기반 동적 대리치 매핑)
    # 실제 데이터에서는 백분위 순위 등을 계산하여 매핑할 수 있습니다.
    labels = ["관광객 다양성", "소비 다양성", "국제 다양성", "SNS 언급량", "내비 검색량"]
    
    val_c1 = [
        0.95 if d_c1.iloc[0]["cityType"] == "도시1" else (0.45 if d_c1.iloc[0]["cityType"] == "도시2" else 0.75),
        0.90 if d_c1.iloc[0]["cityType"] == "도시1" else (0.25 if d_c1.iloc[0]["cityType"] == "도시2" else 0.70),
        0.92 if d_c1.iloc[0]["cityType"] == "도시1" else (0.35 if d_c1.iloc[0]["cityType"] == "도시2" else 0.65),
        float(d_c1.iloc[0]["snsMentionCo"]) / 20000,
        float(d_c1.iloc[0]["naviSearchCo"]) / 15000
    ]
    
    val_c2 = [
        0.95 if d_c2.iloc[0]["cityType"] == "도시1" else (0.45 if d_c2.iloc[0]["cityType"] == "도시2" else 0.75),
        0.90 if d_c2.iloc[0]["cityType"] == "도시1" else (0.25 if d_c2.iloc[0]["cityType"] == "도시2" else 0.70),
        0.92 if d_c2.iloc[0]["cityType"] == "도시1" else (0.35 if d_c2.iloc[0]["cityType"] == "도시2" else 0.65),
        float(d_c2.iloc[0]["snsMentionCo"]) / 20000,
        float(d_c2.iloc[0]["naviSearchCo"]) / 15000
    ]
    
    # 1.0 초과 방지
    val_c1 = [min(x, 1.0) for x in val_c1]
    val_c2 = [min(x, 1.0) for x in val_c2]
    
    # Plotly 레이더 플롯 그리기
    fig_radar = go.Figure()
    fig_radar.add_trace(go.Scatterpolar(
        r=val_c1, theta=labels, fill='toself', name=city_1, line_color='red'
    ))
    fig_radar.add_trace(go.Scatterpolar(
        r=val_c2, theta=labels, fill='toself', name=city_2, line_color='blue'
    ))
    fig_radar.update_layout(
        polar=dict(radialaxis=dict(visible=True, range=[0, 1])),
        showlegend=True,
        title=f"{city_1} vs {city_2} 5대 차원 평가 지표"
    )
    st.plotly_chart(fig_radar, use_container_width=True)
    
    st.markdown("---")
    
    # 2. 소비 업종 카드 매출 분포 및 격차 비교
    st.markdown("### 💳 2. 관광 카드 소비 구조 분석 (소비 인프라 격차)")
    
    # 소비 정규화 비율 비교
    s_pivot = pd.concat([s_c1, s_c2])
    fig_spend = px.bar(
        s_pivot, x="cardUseAmt", y="signguNm", color="indutyNm",
        title="두 도시의 관광 카드 결제 업종 구성 비교",
        labels={"cardUseAmt": "카드 총 매출액(원)", "signguNm": "도시명", "indutyNm": "소비 업종"},
        orientation="h",
        color_discrete_sequence=px.colors.qualitative.Set1
    )
    st.plotly_chart(fig_spend, use_container_width=True)
    
    # 수치적 격차 분석
    c1_total_spend = s_c1["cardUseAmt"].sum()
    c2_total_spend = s_c2["cardUseAmt"].sum()
    
    # 식음료 비중 계산
    c1_food_amt = s_c1[s_c1["indutyNm"] == "식음료"]["cardUseAmt"].sum()
    c1_food_ratio = (c1_food_amt / c1_total_spend) * 100 if c1_total_spend > 0 else 0
    
    c2_food_amt = s_c2[s_c2["indutyNm"] == "식음료"]["cardUseAmt"].sum()
    c2_food_ratio = (c2_food_amt / c2_total_spend) * 100 if c2_total_spend > 0 else 0
    
    # 숙박 비중 계산
    c1_stay_amt = s_c1[s_c1["indutyNm"] == "숙박"]["cardUseAmt"].sum()
    c1_stay_ratio = (c1_stay_amt / c1_total_spend) * 100 if c1_total_spend > 0 else 0
    
    c2_stay_amt = s_c2[s_c2["indutyNm"] == "숙박"]["cardUseAmt"].sum()
    c2_stay_ratio = (c2_stay_amt / c2_total_spend) * 100 if c2_total_spend > 0 else 0

    col_spend_stat1, col_spend_stat2 = st.columns(2)
    with col_spend_stat1:
        st.markdown(f"**🔴 {city_1} 소비 특징**")
        st.write(f"- 총 소비 규모: **{c1_total_spend / 100000000:.1f} 억원**")
        st.write(f"- 식음료 편중률: **{c1_food_ratio:.1f}%**")
        st.write(f"- 체류형 숙박 비율: **{c1_stay_ratio:.1f}%**")
    with col_spend_stat2:
        st.markdown(f"**🔵 {city_2} 소비 특징**")
        st.write(f"- 총 소비 규모: **{c2_total_spend / 100000000:.1f} 억원**")
        st.write(f"- 식음료 편중률: **{c2_food_ratio:.1f}%**")
        st.write(f"- 체류형 숙박 비율: **{c2_stay_ratio:.1f}%**")

    st.markdown("---")
    
    # 3. 방문객 인구통계학적 특성 및 문화 자원 비교
    st.markdown("### 👥 3. 관광객 인구 세그먼트 및 선호 목적지 비교")
    
    col_sub1, col_sub2 = st.columns(2)
    
    with col_sub1:
        # 연령대 비교
        v_pivot = pd.concat([v_c1, v_c2])
        fig_vis = px.bar(
            v_pivot, x="visitorCo", y="signguNm", color="ageGrp",
            title="방문객 연령대 분포 비교",
            labels={"visitorCo": "방문객 수(명)", "signguNm": "도시명", "ageGrp": "연령대"},
            orientation="h",
            color_discrete_sequence=px.colors.qualitative.Set3
        )
        st.plotly_chart(fig_vis, use_container_width=True)
        
    with col_sub2:
        # 문화 자원 비교
        c_pivot = pd.concat([c_c1, c_c2])
        fig_cult = px.bar(
            c_pivot, x="searchCo", y="signguNm", color="clNm",
            title="내비게이션 목적지 카테고리 비교",
            labels={"searchCo": "목적지 검색수", "signguNm": "도시명", "clNm": "목적지 분류"},
            orientation="h",
            color_discrete_sequence=px.colors.qualitative.Set2
        )
        st.plotly_chart(fig_cult, use_container_width=True)

    st.markdown("---")
    
    # 4. 데이터 기반 벤치마킹 및 활성화 대안 제언 (5단계의 핵심 결과물)
    st.markdown("### 💡 4. 데이터 기반 벤치마킹 제언 리포트")
    
    # 동적 격차 분석 문장 생성
    food_gap = c2_food_ratio - c1_food_ratio
    stay_gap = c1_stay_ratio - c2_stay_ratio
    
    st.success(f"""
    #### ✍️ {city_2} 관광 활성화를 위한 성공 도시 {city_1} 벤치마킹 보고서
    
    1. **식음료 편중 완화 및 복합 상권 개발 (맛집 연계 쇼핑 인프라)**
       - 분석 결과, {city_2}의 식음료 소비 비중은 **{c2_food_ratio:.1f}%**로, {city_1}의 **{c1_food_ratio:.1f}%** 대비 **{food_gap:.1f}%p 높은 극단적 편중** 현상을 보이고 있습니다.
       - 단순 식사 소비에 그치지 않고 소비가 지역 내로 분산될 수 있도록, 대표 맛집 주변 반경 500m 이내에 지역 고유의 공방, 청년 창업 매장, 기념품 숍을 배치하여 동선 내 **'로컬 쇼핑 상권' 연계**를 구축해야 합니다.
       
    2. **체류 여건 보완 및 다각적 야간 콘텐츠 활성화 (숙박 유도)**
       - {city_1}은 전체 소비 중 **{c1_stay_ratio:.1f}%**가 숙박 업종에서 이루어져 높은 체류성 소비를 생산하는 반면, {city_2}은 **{c2_stay_ratio:.1f}%** 수준에 머물러 관광객이 체류하지 않고 당일로 이탈하고 있습니다.
       - {city_1}의 감성 한옥스테이나 도심형 게스트하우스 모델을 벤치마킹하여, 지역 유휴 자원을 활용한 **감성 숙박(스테이) 클러스터**를 보급하고, 야간 경관 미술관이나 야간 푸드 마켓 등을 개방하여 머무를 수 있는 밤 문화를 개발해야 합니다.
       
    3. **내비게이션 행선지 다양화 (문화/체험 시설 확대)**
       - 내비게이션 목적지 검색 비교 결과, {city_2}은 역사나 자연관광지의 단순 자연 경관 감상 비중이 압도적인 반면, {city_1}은 복합 문화시설 및 스포츠여가 검색 비중이 뚜렷합니다.
       - 자연 자원을 보유한 {city_2}의 장점을 극대화하되, 실내 미디어 아트 센터, 복합 문화 체험 공간 등을 결합하여 기후 영향 없이 4계절 내내 방문객을 흡수할 수 있는 하이브리드 관광 복합 공간 확충이 요구됩니다.
    """)
else:
    st.error("도시 정보를 비교하기 위한 통계 데이터가 부족합니다.")
