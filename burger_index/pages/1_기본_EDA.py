"""
이 모듈은 버거지수 데이터의 기본적인 통계 및 탐색적 데이터 분석(EDA) 결과를 제공하는 Streamlit 페이지입니다.
"""

import streamlit as st
import pandas as pd
import numpy as np

st.set_page_config(page_title="기본 EDA", page_icon="📊", layout="wide")
st.title("📊 기본 EDA (탐색적 데이터 분석)")

# 데이터 로드
@st.cache_data
def load_data():
    df = pd.read_csv('burger_index/report/sigungu_crosstab.csv')
    return df

df = load_data()

st.header("1. 데이터 미리보기")
col1, col2 = st.columns(2)
with col1:
    st.subheader("상위 5개 행")
    st.dataframe(df.head())
with col2:
    st.subheader("하위 5개 행")
    st.dataframe(df.tail())

st.header("2. 데이터 기본 정보 및 통계")
col3, col4 = st.columns(2)
with col3:
    st.subheader("데이터 크기(Shape)")
    st.write(f"- 행(Rows): {df.shape[0]} 개")
    st.write(f"- 열(Columns): {df.shape[1]} 개")
    
    st.subheader("결측치 확인")
    st.dataframe(df.isnull().sum().to_frame("결측치 수"))

with col4:
    st.subheader("수치형 변수 기술통계량")
    st.dataframe(df.describe())

st.header("3. 버거지수 상/하위 분포")

col5, col6 = st.columns(2)

# 무한대나 결측치가 있는 경우 제외하고 정렬
df_clean = df.replace([np.inf, -np.inf], np.nan).dropna(subset=['버거지수'])

with col5:
    st.subheader("버거지수 Top 10 지역")
    top10 = df_clean.sort_values(by='버거지수', ascending=False).head(10)
    st.bar_chart(data=top10, x='시도시군구명', y='버거지수', color="#ff4b4b")

with col6:
    st.subheader("버거지수 Bottom 10 지역")
    bottom10 = df_clean.sort_values(by='버거지수', ascending=True).head(10)
    st.bar_chart(data=bottom10, x='시도시군구명', y='버거지수', color="#4b4bff")
