"""
방한 외래객 추이 분석 모듈입니다.
주요 기능:
- 성별/연령대별 교차 분포, 국적 점유율
- 방문자/입국자 국적 집중화 현상 분석
"""
import os
import sys
import streamlit as st
import pandas as pd
import plotly.express as px

sys.path.append(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

def render_foreigner_trend():
    st.title("📈 방한 외래관광객 트렌드 분석")
    st.markdown("글로벌 외래 관광객의 입국 트렌드와 인구통계학적 세그먼트 분석을 제공합니다.")
    st.caption("🔹 **자료 출처:** 한국관광공사(한국관광 데이터랩), 공공데이터포털(ODCloud)")
    st.markdown("---")

    data_dir = os.path.join(os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__)))), 'data')
    
    @st.cache_data
    def load_real_data():
        try:
            df_monthly = pd.read_csv(os.path.join(data_dir, '20260702201956_전체 외국인 방문자수 및 증감률 CSV 다운로드.csv'), encoding='utf-8')
        except:
            df_monthly = pd.read_csv(os.path.join(data_dir, '20260702201956_전체 외국인 방문자수 및 증감률 CSV 다운로드.csv'), encoding='cp949')
            
        try:
            df_gender_age = pd.read_csv(os.path.join(data_dir, '20260702211925_성_연령별 입국현황.csv'), encoding='utf-8')
        except:
            df_gender_age = pd.read_csv(os.path.join(data_dir, '20260702211925_성_연령별 입국현황.csv'), encoding='cp949')
            
        try:
            df_purpose = pd.read_csv(os.path.join(data_dir, '20260702211937_목적별 입국현황.csv'), encoding='utf-8')
        except:
            df_purpose = pd.read_csv(os.path.join(data_dir, '20260702211937_목적별 입국현황.csv'), encoding='cp949')
            
        try:
            df_entry = pd.read_csv(os.path.join(data_dir, '20260620155533_입국자 국적별 입국현황.csv'), encoding='utf-8')
        except:
            df_entry = pd.read_csv(os.path.join(data_dir, '20260620155533_입국자 국적별 입국현황.csv'), encoding='cp949')
            
        return df_monthly, df_gender_age, df_purpose, df_entry

    try:
        df_monthly, df_gender_age, df_purpose, df_entry = load_real_data()
    except Exception as e:
        st.warning(f"로컬 입국자 데이터를 불러올 수 없습니다: {e}")
        return

    # 데이터 타입 캐스팅 및 파생 변수 처리
    df_monthly['기준년월'] = df_monthly['기준년월'].astype(str)
    
    # 2026년 총 방문자 수 계산
    df_2026 = df_monthly[df_monthly['기준년월'].str.startswith('2026')]
    total_foreigner_2026 = df_2026['조회기간 방문자 수'].sum()
    
    # 대표 목적 및 연령 산출
    top_purpose = df_purpose.loc[df_purpose['방문자 수(명)'].idxmax(), '목적 유형']
    
    df_gender_age['총 승객 수'] = df_gender_age['남성 승객 수(명)'] + df_gender_age['여성 승객 수(명)']
    top_age = df_gender_age.loc[df_gender_age['총 승객 수'].idxmax(), '연령 구분']

    # 메인 요약 KPI
    st.markdown("### 📊 방한 외래객 유입 현황 요약")
    
    kpi_col1, kpi_col2, kpi_col3 = st.columns(3)
    with kpi_col1:
        st.metric(
            label="방한 외래객 총수(2026년 기준 누적)", 
            value=f"{total_foreigner_2026:,.0f} 명"
        )
    with kpi_col2:
        st.metric(label="핵심 입국 목적", value=top_purpose)
    with kpi_col3:
        st.metric(label="주요 방문 연령층", value=top_age)

    # 월별 추이 라인 차트
    with st.container():
        st.markdown("#### 월별 외래 관광객 유입 추이")
        df_monthly_sorted = df_monthly.sort_values('기준년월')
        fig = px.line(
            df_monthly_sorted, x="기준년월", y="조회기간 방문자 수", 
            labels={"조회기간 방문자 수": "관광객 수(명)", "기준년월": "연월"},
            markers=True,
            color_discrete_sequence=["#00F0FF"] # Neon Cyan
        )
        fig.update_traces(
            line=dict(width=3),
            marker=dict(size=8, symbol="circle", line=dict(width=2, color="white")),
            hovertemplate="<b>기준연월</b>: %{x}<br><b>관광객 수</b>: %{y:,.0f}명<extra></extra>"
        )
        fig.update_layout(
            hovermode="x unified",
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Pretendard, sans-serif", size=14, color="#E2E8F0"),
            hoverlabel=dict(bgcolor="#1E293B", font_size=13, font_family="Pretendard", font=dict(color="#F8FAFC")),
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis=dict(showgrid=False, zeroline=False, linecolor="#334155"),
            yaxis=dict(showgrid=True, gridcolor="#1E293B", zeroline=False, linecolor="#334155")
        )
        st.plotly_chart(fig, use_container_width=True)
        
    st.markdown("---")

    col1, col2 = st.columns(2)
    with col1:
        st.markdown("#### 1. 성별/연령대별 교차 분포")
        # 데이터를 롱폼으로 변환
        df_long = pd.melt(df_gender_age, id_vars=['연령 구분'], value_vars=['남성 승객 수(명)', '여성 승객 수(명)'], 
                          var_name='성별', value_name='인원수')
        df_long['성별'] = df_long['성별'].replace({'남성 승객 수(명)': '남성', '여성 승객 수(명)': '여성'})
        
        fig_gender_age = px.bar(
            df_long, x="연령 구분", y="인원수", color="성별",
            labels={"인원수": "관광객 수(명)", "연령 구분": "연령대"},
            barmode="group",
            color_discrete_map={"여성": "#38BDF8", "남성": "#2563EB"}
        )
        fig_gender_age.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Pretendard, sans-serif", size=14, color="#E2E8F0"),
            hoverlabel=dict(bgcolor="#1E293B", font_size=13, font_family="Pretendard", font=dict(color="#F8FAFC")),
            margin=dict(l=20, r=20, t=30, b=20),
            xaxis=dict(showgrid=False, zeroline=False, linecolor="#334155"),
            yaxis=dict(showgrid=True, gridcolor="#1E293B", zeroline=False, linecolor="#334155")
        )
        st.plotly_chart(fig_gender_age, use_container_width=True)

    with col2:
        st.markdown("#### 2. 방한 외래객 목적별 점유율")
        
        df_share = df_purpose.nlargest(7, "방문자 수(명)")
        fig_share = px.pie(
            df_share, names="목적 유형", values="방문자 수(명)", hole=0.4,
            color_discrete_sequence=["#00F0FF", "#38BDF8", "#2563EB", "#1E3A8A", "#64748B", "#94A3B8", "#080D1A"]
        )
        fig_share.update_layout(
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Pretendard, sans-serif", size=14, color="#E2E8F0"),
            hoverlabel=dict(bgcolor="#1E293B", font_size=13, font_family="Pretendard", font=dict(color="#F8FAFC")),
            margin=dict(l=20, r=20, t=20, b=20)
        )
        st.plotly_chart(fig_share, use_container_width=True)
        
    st.markdown("---")
    
    st.header("🗺️ 국적 집중화 현상")
    st.markdown("특정 국가에 편중된 의존도를 분석합니다.")
    
    if df_entry is not None and not df_entry.empty:
        st.subheader("방한 주요 국적별 입국자 총량")
        
        iso_mapping = {
            '중국': 'CHN', '일본': 'JPN', '대만': 'TWN', '미국': 'USA',
            '홍콩': 'HKG', '베트남': 'VNM', '싱가포르': 'SGP', '필리핀': 'PHL',
            '태국': 'THA', '말레이시아': 'MYS', '인도네시아': 'IDN', '러시아': 'RUS',
            '영국': 'GBR', '캐나다': 'CAN', '프랑스': 'FRA', '독일': 'DEU', '호주': 'AUS'
        }
        df_entry['ISO_CODE'] = df_entry['입국자 국적'].map(iso_mapping)
        
        fig4 = px.choropleth(
            df_entry, 
            locations="ISO_CODE", 
            color="입국자 수(명)", 
            hover_name="입국자 국적",
            title="국적별 입국자 수 카토그램 (중국 및 동아시아 강세)",
            color_continuous_scale="Blues",
            projection="equirectangular"
        )
        
        fig4.update_traces(marker_line_color="white", marker_line_width=1)
        fig4.update_layout(
            geo=dict(
                showframe=False,
                showcoastlines=True,
                coastlinecolor="white",
                showcountries=True,
                countrycolor="white",
                bgcolor="rgba(0,0,0,0)"
            ),
            plot_bgcolor="rgba(0,0,0,0)",
            paper_bgcolor="rgba(0,0,0,0)",
            font=dict(family="Pretendard, sans-serif", size=14, color="#E2E8F0"),
            hoverlabel=dict(bgcolor="#1E293B", font_size=13, font_family="Pretendard", font=dict(color="#F8FAFC")),
            margin=dict(l=0, r=0, t=40, b=0)
        )
        st.plotly_chart(fig4, use_container_width=True)
    else:
        st.warning("입국자 국적 데이터를 확인할 수 없습니다.")
