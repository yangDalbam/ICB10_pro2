"""
이 모듈은 네이버 API 대시보드의 메인 진입점(Entry Point)입니다.
주요 기능:
- API Key 설정 상태 확인 및 사이드바 설정 제공
- 설정 완료 시, 단일 키워드에 대한 종합 분석 대시보드(Overview) 활성화
- 데이터랩 트렌드, 쇼핑, 뉴스, 블로그 API를 통합 호출하여 3단 메트릭 카드 및 탭 형식 분석 화면 제공
- Plotly 시각화와 인터랙티브 데이터 테이블 및 단어 빈도 요약 제공
"""

import os
import sys
import re
from collections import Counter
import streamlit as st
import pandas as pd
import plotly.graph_objects as go
import plotly.express as px
from datetime import datetime, timedelta
from dotenv import load_dotenv

# API 모듈 검색 경로 추가
current_dir = os.path.dirname(os.path.abspath(__file__))
if current_dir not in sys.path:
    sys.path.append(current_dir)

from api.naver_client import inject_custom_css
from api.datalab_api import get_search_trend
from api.search_api import search_shopping, search_news, search_blog

# 1) 환경 변수 로드
load_dotenv()
parent_dir = os.path.dirname(current_dir)
load_dotenv(os.path.join(parent_dir, ".env"))

# 2) 세션 상태 초기화 (API Key)
if "client_id" not in st.session_state:
    val = os.getenv("NAVER_CLIENT_ID", "")
    try:
        if "NAVER_CLIENT_ID" in st.secrets:
            val = st.secrets["NAVER_CLIENT_ID"]
    except Exception:
        pass
    st.session_state["client_id"] = val.strip() if val else ""

if "client_secret" not in st.session_state:
    val = os.getenv("NAVER_CLIENT_SECRET", "")
    try:
        if "NAVER_CLIENT_SECRET" in st.secrets:
            val = st.secrets["NAVER_CLIENT_SECRET"]
    except Exception:
        pass
    st.session_state["client_secret"] = val.strip() if val else ""

# 프리미엄 CSS 테마 적용
inject_custom_css()

st.set_page_config(
    page_title="Naver API Dashboard",
    page_icon="📊",
    layout="wide"
)

# 사이드바 API Key 설정 영역
with st.sidebar:
    st.header("🔑 API 설정")
    client_id = st.text_input("Client ID", value=st.session_state["client_id"], type="password")
    client_secret = st.text_input("Client Secret", value=st.session_state["client_secret"], type="password")
    save_to_file = st.checkbox("입력한 키를 .env 파일에 저장하여 자동 로드", value=True)
    
    if st.button("설정 저장"):
        if client_id and client_secret:
            st.session_state["client_id"] = client_id.strip()
            st.session_state["client_secret"] = client_secret.strip()
            
            save_success = True
            if save_to_file:
                env_file_path = os.path.join(parent_dir, ".env")
                try:
                    with open(env_file_path, "w", encoding="utf-8") as f:
                        f.write(f"NAVER_CLIENT_ID={client_id.strip()}\n")
                        f.write(f"NAVER_CLIENT_SECRET={client_secret.strip()}\n")
                except Exception as e:
                    st.error(f".env 파일 저장 실패: {e}")
                    save_success = False
            
            if save_success:
                st.success("API 설정이 저장되었습니다! (세션 적용 완료)")
                st.rerun()
        else:
            st.error("Client ID와 Client Secret을 모두 입력해주세요.")
            
    st.markdown("---")
    if st.session_state["client_id"] and st.session_state["client_secret"]:
        st.success("✅ API 설정 완료")
    else:
        st.warning("⚠️ API 설정 필요")

# 메인 콘텐츠 영역 분기
c_id = st.session_state["client_id"]
c_secret = st.session_state["client_secret"]

# 텍스트 내에서 명사/단어 요약을 위한 유틸리티 함수
def extract_top_keywords(items, text_key="title", top_n=10):
    stop_words = set([
        "네이버", "블로그", "뉴스", "및", "이", "그", "저", "은", "는", "이", "가", "을", "를", "에", "의", "와", "과", 
        "으로", "로", "에서", "합니다", "하는", "있다", "없다", "대한", "관한", "등", "일", "월", "년", "최근", 
        "출시", "공개", "진행", "통해", "위해", "때문", "관련", "이유", "우려", "기대", "전망", "분석"
    ])
    words = []
    for item in items:
        # HTML 태그 제거
        text = re.sub(r'<[^>]*>', '', item.get(text_key, ''))
        # 한글/영문 단어 추출
        text_words = re.findall(r'[a-zA-Z가-힣0-9]+', text)
        for w in text_words:
            if len(w) > 1 and w.lower() not in stop_words:
                words.append(w)
    counter = Counter(words)
    return counter.most_common(top_n)

if not c_id or not c_secret:
    st.markdown('<h1 class="gradient-text">네이버 API 분석 대시보드 📊</h1>', unsafe_allow_html=True)
    st.markdown("""
    이 대시보드는 네이버 검색 및 데이터랩 API를 활용하여 트렌드, 쇼핑, 뉴스, 블로그 등 다각도의 채널 데이터를 실시간 수집하고 시각화 분석을 수행합니다.  
    
    ### 👈 시작하기 위해 API Key를 먼저 입력해주세요!
    왼쪽 사이드바에서 **Naver OpenAPI Client ID**와 **Client Secret**을 설정해 주시면 종합 대시보드 화면이 활성화됩니다.
    
    - [네이버 개발자 센터](https://developers.naver.com/)에서 애플리케이션을 등록하여 무료로 API Key를 발급받으실 수 있습니다.
    - 사용 권한 추가 필요: **데이터랩(검색어트렌드/쇼핑인사이트)**, **검색(뉴스/블로그/쇼핑)**
    """)
    
    # 기본 안내 카드 노출
    st.subheader("🛠️ 분석 서비스 제공 목록")
    col1, col2 = st.columns(2)
    with col1:
        st.markdown("""
        <div class="metric-card">
            <h3>📈 종합 분석 홈화면 (Overview)</h3>
            <p style="color:#666;font-size:14px;">검색어 한 개에 대해 검색 트렌드, 쇼핑 가격 정보, 최근 뉴스 및 블로그 콘텐츠 동향을 요약하여 한 눈에 보여줍니다.</p>
        </div>
        """, unsafe_allow_html=True)
    with col2:
        st.markdown("""
        <div class="metric-card">
            <h3>📂 상세 분석 페이지 (사이드바 메뉴)</h3>
            <p style="color:#666;font-size:14px;">검색어 트렌드 다중 비교, 쇼핑 최저가 정밀 시각화, 블로그/뉴스/카페 개별 채널의 대량 데이터 수집 기능을 각각 수행할 수 있습니다.</p>
        </div>
        """, unsafe_allow_html=True)
else:
    # API 설정이 된 경우: 종합 분석 대시보드 활성화
    st.markdown('<h1 class="gradient-text">종합 분석 대시보드 (Overview) 📊</h1>', unsafe_allow_html=True)
    st.markdown("특정 검색어를 하나 입력하면 검색 트렌드 변화, 쇼핑 최저가, 뉴스/블로그 동향까지 네이버 API가 제공하는 다채로운 데이터를 한눈에 분석합니다.")
    
    # 1) 입력 폼 영역
    with st.form("overview_form"):
        col_in1, col_in2 = st.columns([7, 3])
        with col_in1:
            keyword_input = st.text_input("분석할 단일 검색어를 입력하세요", value="인공지능", placeholder="예: 아이폰, 챗GPT, 전기차 등")
        with col_in2:
            period_opt = st.selectbox(
                "조회 기간",
                options=["최근 1개월", "최근 3개월", "최근 6개월", "최근 1년"],
                index=1
            )
        submit_btn = st.form_submit_button("종합 분석 시작 🚀")
        
    # 기간 옵션에 따른 날짜 계산
    today = datetime.today()
    if period_opt == "최근 1개월":
        start_date = today - timedelta(days=30)
    elif period_opt == "최근 3개월":
        start_date = today - timedelta(days=90)
    elif period_opt == "최근 6개월":
        start_date = today - timedelta(days=180)
    else:
        start_date = today - timedelta(days=365)
        
    # 분석 실행 처리
    if submit_btn or "overview_keyword" not in st.session_state:
        # 최초 로드 시 기본 키워드로 자동 분석 실행을 위해 세션에 저장
        st.session_state["overview_keyword"] = keyword_input.strip()
        st.session_state["overview_start_date"] = start_date
        st.session_state["overview_end_date"] = today
        
    # 세션 기반으로 항상 데이터 렌더링 유지
    search_keyword = st.session_state.get("overview_keyword", "인공지능")
    s_date = st.session_state.get("overview_start_date", today - timedelta(days=90))
    e_date = st.session_state.get("overview_end_date", today)
    
    st.markdown(f"### 🔍 **'{search_keyword}'** 에 대한 종합 분석 결과 (기간: {s_date.strftime('%Y-%m-%d')} ~ {e_date.strftime('%Y-%m-%d')})")
    
    # API 동시 호출 및 로딩 스피너
    with st.spinner("네이버 API에서 실시간 통합 데이터를 불러오고 있습니다..."):
        # 1) 데이터랩 트렌드 데이터
        keyword_groups = [{"groupName": search_keyword, "keywords": [search_keyword]}]
        trend_data = get_search_trend(
            s_date.strftime("%Y-%m-%d"),
            e_date.strftime("%Y-%m-%d"),
            "date",
            keyword_groups,
            c_id,
            c_secret
        )
        
        # 2) 쇼핑 검색 데이터
        shop_data = search_shopping(search_keyword, c_id, c_secret, display=100)
        
        # 3) 뉴스 검색 데이터
        news_data = search_news(search_keyword, c_id, c_secret, display=100)
        
        # 4) 블로그 검색 데이터
        blog_data = search_blog(search_keyword, c_id, c_secret, display=100)
        
    # 데이터 가공 및 예외 처리
    # 1. 트렌드 가공
    df_trend = pd.DataFrame()
    if trend_data and "results" in trend_data and trend_data["results"]:
        records = []
        for result in trend_data["results"]:
            title = result["title"]
            for d in result["data"]:
                records.append({
                    "날짜": d["period"],
                    "검색량": d["ratio"],
                    "검색어": title
                })
        if records:
            df_trend = pd.DataFrame(records)
            
    # 2. 쇼핑 가공
    df_shop = pd.DataFrame()
    if shop_data and "items" in shop_data:
        shop_items = []
        for item in shop_data["items"]:
            # 가격 정보 정제
            try:
                lprice = int(item.get("lprice", 0))
            except ValueError:
                lprice = 0
            shop_items.append({
                "상품명": re.sub(r'<[^>]*>', '', item.get("title", "")),
                "최저가": lprice,
                "몰이름": item.get("mallName", "네이버"),
                "링크": item.get("link", "")
            })
        df_shop = pd.DataFrame(shop_items)
        # 0원 혹은 비정상 데이터 제외
        df_shop = df_shop[df_shop["최저가"] > 0]
        
    # 3. 뉴스 및 블로그 가공
    news_list = news_data.get("items", []) if news_data else []
    blog_list = blog_data.get("items", []) if blog_data else []
    
    # ------------------ 메트릭 계산 ------------------
    # 1) 트렌드 메트릭
    if not df_trend.empty:
        avg_trend = df_trend["검색량"].mean()
        max_row = df_trend.loc[df_trend["검색량"].idxmax()]
        max_trend = max_row["검색량"]
        max_trend_date = max_row["날짜"]
        trend_metric_html = f"""
        <p style="margin:5px 0 0 0;font-size:14px;color:#555;">평균 관심도: <b>{avg_trend:.2f}%</b></p>
        <p style="margin:5px 0 0 0;font-size:14px;color:#555;">최대 관심도: <b>{max_trend:.1f}%</b></p>
        <span style="font-size:11px;color:#888;">(최고치 기록일: {max_trend_date})</span>
        """
    else:
        trend_metric_html = "<p style='color:#999;font-size:14px;'>데이터랩 트렌드 정보 없음</p>"
        
    # 2) 쇼핑 메트릭
    if not df_shop.empty:
        avg_price = df_shop["최저가"].mean()
        min_price = df_shop["최저가"].min()
        max_price = df_shop["최저가"].max()
        shop_metric_html = f"""
        <p style="margin:5px 0 0 0;font-size:14px;color:#555;">평균가: <b>{avg_price:,.0f}원</b></p>
        <p style="margin:5px 0 0 0;font-size:14px;color:#555;">최저가: <b style="color:#e03e2d;">{min_price:,.0f}원</b></p>
        <p style="margin:2px 0 0 0;font-size:14px;color:#555;">최고가: <b>{max_price:,.0f}원</b></p>
        """
    else:
        shop_metric_html = "<p style='color:#999;font-size:14px;'>쇼핑 상품 정보 없음</p>"
        
    # 3) 콘텐츠 메트릭
    news_cnt = len(news_list)
    blog_cnt = len(blog_list)
    content_metric_html = f"""
    <p style="margin:5px 0 0 0;font-size:14px;color:#555;">최신 뉴스 수집: <b>{news_cnt}건</b></p>
    <p style="margin:5px 0 0 0;font-size:14px;color:#555;">최신 블로그 수집: <b>{blog_cnt}건</b></p>
    <span style="font-size:11px;color:#888;">(최대 각 100건 기준 분석 진행)</span>
    """
    
    # 3단 메트릭 가로 배치 렌더링
    st.subheader("📊 핵심 요약 통계 (Key Metrics)")
    col_m1, col_m2, col_m3 = st.columns(3)
    
    with col_m1:
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="margin:0;color:#00c73c;font-size:18px;">📈 검색량 관심도 트렌드</h4>
            {trend_metric_html}
        </div>
        """, unsafe_allow_html=True)
        
    with col_m2:
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="margin:0;color:#00c73c;font-size:18px;">🛒 쇼핑 상품 가격 동향</h4>
            {shop_metric_html}
        </div>
        """, unsafe_allow_html=True)
        
    with col_m3:
        st.markdown(f"""
        <div class="metric-card">
            <h4 style="margin:0;color:#00c73c;font-size:18px;">📰 최신 콘텐츠 현황</h4>
            {content_metric_html}
        </div>
        """, unsafe_allow_html=True)
        
    # ------------------ 하단 탭 영역 ------------------
    st.markdown("---")
    st.subheader("🔍 채널별 상세 분석 정보")
    
    tab1, tab2, tab3 = st.tabs(["📈 검색어 트렌드 상세", "🛒 쇼핑 최저가 상세", "📰 뉴스 및 블로그 콘텐츠 상세"])
    
    # Tab 1: 검색어 트렌드 상세
    with tab1:
        if not df_trend.empty:
            fig_trend = go.Figure()
            fig_trend.add_trace(go.Scatter(
                x=df_trend["날짜"],
                y=df_trend["검색량"],
                mode="lines",
                name=search_keyword,
                line=dict(width=3, color="#00c73c"),
                hovertemplate=f"<b>{search_keyword}</b><br>날짜: %{{x}}<br>상대검색량: %{{y:.2f}}%<extra></extra>"
            ))
            fig_trend.update_layout(
                title=f"'{search_keyword}' 검색 관심도 추이",
                hovermode="x unified",
                plot_bgcolor="rgba(0,0,0,0)",
                paper_bgcolor="rgba(0,0,0,0)",
                xaxis=dict(gridcolor="#f0f2f6", showline=True, linecolor="#dcdcdc"),
                yaxis=dict(gridcolor="#f0f2f6", showline=True, linecolor="#dcdcdc"),
                margin=dict(l=40, r=40, t=50, b=40)
            )
            st.plotly_chart(fig_trend, use_container_width=True)
            
            # 상세 데이터 테이블 제공
            with st.expander("📝 상세 검색 트렌드 데이터 리스트"):
                st.dataframe(df_trend, use_container_width=True)
        else:
            st.info("트렌드 데이터를 가져오지 못했습니다. 키워드 및 날짜 설정을 다시 확인해 주세요.")
            
    # Tab 2: 쇼핑 최저가 상세
    with tab2:
        if not df_shop.empty:
            col_s_ch1, col_s_ch2 = st.columns([6, 4])
            
            with col_s_ch1:
                # 가격 분포 박스 플롯 시각화
                fig_box = px.box(
                    df_shop, 
                    y="최저가", 
                    points="all", 
                    title=f"'{search_keyword}' 관련 상품 가격 분포도",
                    color_discrete_sequence=["#00c73c"]
                )
                fig_box.update_layout(
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(showline=True, linecolor="#dcdcdc"),
                    yaxis=dict(gridcolor="#f0f2f6", showline=True, linecolor="#dcdcdc")
                )
                st.plotly_chart(fig_box, use_container_width=True)
                
            with col_s_ch2:
                # 판매점별 상품 등록 분포
                mall_counts = df_shop["몰이름"].value_counts().reset_index()
                mall_counts.columns = ["몰이름", "등록수"]
                fig_pie = px.pie(
                    mall_counts.head(8), 
                    values="등록수", 
                    names="몰이름", 
                    title="주요 판매 쇼핑몰 비중",
                    color_discrete_sequence=px.colors.qualitative.Pastel
                )
                st.plotly_chart(fig_pie, use_container_width=True)
                
            # 최저가 순 상위 상품 목록 출력
            st.markdown("#### 🏆 최저가 상품 목록 Top 15")
            df_shop_sorted = df_shop.sort_values(by="최저가").reset_index(drop=True)
            
            # 링크 컬럼을 클릭 가능하게 렌더링하기 위해 데이터 가공
            df_display = df_shop_sorted.head(15).copy()
            st.dataframe(
                df_display, 
                column_config={
                    "링크": st.column_config.LinkColumn("상품 링크")
                },
                use_container_width=True
            )
        else:
            st.info("쇼핑 상품 데이터를 찾지 못했습니다.")
            
    # Tab 3: 뉴스 및 블로그 콘텐츠 상세
    with tab3:
        # 1) 단어 빈도 시각화
        combined_items = news_list + blog_list
        if combined_items:
            st.markdown("#### 🔑 수집 데이터 핵심 단어 요약")
            top_words = extract_top_keywords(combined_items, "title", 10)
            
            if top_words:
                df_words = pd.DataFrame(top_words, columns=["단어", "빈도"])
                fig_bar = px.bar(
                    df_words, 
                    x="빈도", 
                    y="단어", 
                    orientation="h",
                    title="뉴스 및 블로그 제목에서 가장 많이 언급된 단어 Top 10",
                    color="빈도",
                    color_continuous_scale=["#a3eab3", "#00c73c"]
                )
                fig_bar.update_layout(
                    yaxis={'categoryorder':'total ascending'},
                    plot_bgcolor="rgba(0,0,0,0)",
                    paper_bgcolor="rgba(0,0,0,0)",
                    xaxis=dict(gridcolor="#f0f2f6", showline=True, linecolor="#dcdcdc"),
                )
                st.plotly_chart(fig_bar, use_container_width=True)
                
        # 2) 뉴스 및 블로그 리스트
        col_c1, col_c2 = st.columns(2)
        
        with col_c1:
            st.markdown("#### 📰 최신 뉴스 목록")
            if news_list:
                for idx, news in enumerate(news_list[:8]):
                    clean_title = re.sub(r'<[^>]*>', '', news.get("title", ""))
                    clean_desc = re.sub(r'<[^>]*>', '', news.get("description", ""))
                    link = news.get("link", news.get("originallink", "#"))
                    pub_date = news.get("pubDate", "")
                    # 날짜 간략화
                    if pub_date:
                        try:
                            parsed_dt = datetime.strptime(pub_date, "%a, %d %b %Y %H:%M:%S +0900")
                            pub_date_str = parsed_dt.strftime("%Y-%m-%d %H:%M")
                        except Exception:
                            pub_date_str = pub_date[:20]
                    else:
                        pub_date_str = ""
                        
                    st.markdown(f"""
                    <div style="padding: 10px; border-bottom: 1px solid #f0f2f6;">
                        <a href="{link}" target="_blank" style="font-weight: 600; color: #1e1e1e; text-decoration: none;">{clean_title}</a>
                        <p style="font-size: 13px; color: #666; margin: 5px 0;">{clean_desc[:120]}...</p>
                        <span style="font-size: 11px; color: #999;">보도일: {pub_date_str}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("조회된 뉴스가 없습니다.")
                
        with col_c2:
            st.markdown("#### 📝 최신 블로그 목록")
            if blog_list:
                for idx, blog in enumerate(blog_list[:8]):
                    clean_title = re.sub(r'<[^>]*>', '', blog.get("title", ""))
                    clean_desc = re.sub(r'<[^>]*>', '', blog.get("description", ""))
                    link = blog.get("link", "#")
                    postdate = blog.get("postdate", "")
                    
                    if postdate:
                        try:
                            parsed_dt = datetime.strptime(postdate, "%Y%m%d")
                            postdate_str = parsed_dt.strftime("%Y-%m-%d")
                        except Exception:
                            postdate_str = postdate
                    else:
                        postdate_str = ""
                        
                    st.markdown(f"""
                    <div style="padding: 10px; border-bottom: 1px solid #f0f2f6;">
                        <a href="{link}" target="_blank" style="font-weight: 600; color: #00c73c; text-decoration: none;">{clean_title}</a>
                        <p style="font-size: 13px; color: #666; margin: 5px 0;">{clean_desc[:120]}...</p>
                        <span style="font-size: 11px; color: #999;">발행일: {postdate_str} | 작성자: {blog.get("bloggername", "")}</span>
                    </div>
                    """, unsafe_allow_html=True)
            else:
                st.info("조회된 블로그 포스트가 없습니다.")
