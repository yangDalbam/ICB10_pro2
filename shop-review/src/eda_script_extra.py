"""
이 모듈은 쇼핑 리뷰 데이터를 불러와 추가적인 EDA(텍스트 전처리, 제품별 TF-IDF 분석 및 워드클라우드)를 수행하는 스크립트입니다.
주요 기능:
- title과 content 컬럼 결합 및 HTML 태그/불용어 제거
- 제품(product)별 TF-IDF 상위 30개 키워드 서브플롯 시각화
- 제품(product)별 워드클라우드 서브플롯 시각화
- 기존 eda_report.md에 분석 결과 추가
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from wordcloud import WordCloud
import os
import re
# 설정
sns.reset_orig()
import koreanize_matplotlib
plt.rcParams['axes.unicode_minus'] = False

DATA_PATH = '../data/shop-review.csv'
REPORT_PATH = '../report/eda_report.md'
IMG_DIR = '../images'

def write_md(text):
    with open(REPORT_PATH, 'a', encoding='utf-8') as f:
        f.write(text + '\n')

try:
    df = pd.read_csv(DATA_PATH, encoding='utf-8', on_bad_lines='skip')
except:
    df = pd.read_csv(DATA_PATH, encoding='cp949', on_bad_lines='skip')

df['title'] = df['title'].fillna('')
df['content'] = df['content'].fillna('')
df['product'] = df['product'].fillna('알수없음')

# 1. 제목과 내용을 공백을 기준으로 합치기
df['full_text'] = df['title'] + ' ' + df['content']

# 2. HTML 태그 및 불용어 제거 (정규표현식 사용, 형태소 분석 X)
stop_words = ['너무', '정말', '진짜', '아주', '많이', '조금', '매우', '그리고', '근데', '하지만', '좋습니다', '좋아요', '같아요', '입니다', '있습니다', '하는', '것', '수', '이', '그', '저']
def clean_text(text):
    # HTML 태그 제거
    text = re.sub(r'<[^>]+>', ' ', text)
    # 특수문자 제거 (한글, 영문, 숫자, 공백 남김)
    text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', text)
    
    # 형태소 분석 없이 단순 공백 기준으로 단어 분리 후 불용어 제거
    words = text.split()
    words = [w for w in words if w not in stop_words and len(w) > 1] # 1글자 단어도 제외
    return ' '.join(words)

df['cleaned_text'] = df['full_text'].apply(clean_text)

# 고유 제품 추출
products = df['product'].unique()
n_products = len(products)
cols = 2
rows = (n_products + 1) // cols

write_md('\n## 5. 제품별 텍스트 및 키워드 심층 분석\n')

# 3. 제품별 TF-IDF 상위 30개 막대그래프 서브플롯
fig, axes = plt.subplots(rows, cols, figsize=(15, rows * 6))
axes = axes.flatten()

for i, prod in enumerate(products):
    subset = df[df['product'] == prod]['cleaned_text']
    if len(subset) == 0:
        continue
    
    vectorizer = TfidfVectorizer(max_features=500)
    try:
        tfidf_matrix = vectorizer.fit_transform(subset)
        feature_names = vectorizer.get_feature_names_out()
        sums = tfidf_matrix.sum(axis=0)
        
        data = [(term, sums[0, col]) for col, term in enumerate(feature_names)]
        ranking = pd.DataFrame(data, columns=['term', 'tfidf']).sort_values('tfidf', ascending=False).head(30)
        
        ax = axes[i]
        ax.barh(ranking['term'][::-1], ranking['tfidf'][::-1], color='skyblue')
        ax.set_title(f'제품: {prod}')
        ax.set_xlabel('TF-IDF Score')
    except Exception as e:
        axes[i].set_title(f'제품: {prod} (데이터 부족)')

# 남는 서브플롯 숨기기
for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
tfidf_img = 'plot_product_tfidf.png'
plt.savefig(os.path.join(IMG_DIR, tfidf_img), bbox_inches='tight')
plt.close()

write_md('### 제품별 TF-IDF 상위 30개 키워드 분석\n')
write_md(f'![제품별 TF-IDF](../images/{tfidf_img})\n')
write_md('**[해석]** HTML 태그와 불용어를 1차적으로 정제한 리뷰 데이터를 바탕으로, 각 제품별 특징을 가장 잘 나타내는 상위 30개의 TF-IDF 키워드를 서브플롯으로 구성했습니다. 각 제품의 강점이나 소비자가 주목하는 요소(배터리, 노이즈 캔슬링 등)가 제품마다 어떻게 다르게 나타나는지 한눈에 파악할 수 있습니다.\n')

# 4. 제품별 워드클라우드 서브플롯
# 윈도우 환경 폰트 설정
font_path = 'C:/Windows/Fonts/malgun.ttf'
if not os.path.exists(font_path):
    font_path = None # 기본 폰트 사용 시 깨질 수 있으나 안전을 위해

fig, axes = plt.subplots(rows, cols, figsize=(15, rows * 6))
axes = axes.flatten()

for i, prod in enumerate(products):
    subset = df[df['product'] == prod]['cleaned_text']
    text_data = ' '.join(subset)
    
    if len(text_data.strip()) == 0:
        continue
        
    try:
        wc = WordCloud(font_path=font_path, width=400, height=300, background_color='white', max_words=100).generate(text_data)
        ax = axes[i]
        ax.imshow(wc, interpolation='bilinear')
        ax.axis('off')
        ax.set_title(f'제품: {prod}')
    except Exception as e:
        axes[i].set_title(f'제품: {prod} (오류)')
        axes[i].axis('off')

# 남는 서브플롯 숨기기
for j in range(i + 1, len(axes)):
    fig.delaxes(axes[j])

plt.tight_layout()
wc_img = 'plot_product_wordcloud.png'
plt.savefig(os.path.join(IMG_DIR, wc_img), bbox_inches='tight')
plt.close()

write_md('\n### 제품별 워드클라우드\n')
write_md(f'![제품별 워드클라우드](../images/{wc_img})\n')
write_md('**[해석]** 각 제품 리뷰에서 자주 언급되는 단어들의 빈도를 기반으로 워드클라우드를 생성했습니다. 글자의 크기가 클수록 많이 언급된 핵심 단어이며, 직관적으로 해당 제품과 관련된 주요 피드백 키워드를 파악하는 데 효과적입니다.\n')

print("텍스트 처리 및 제품별 시각화가 완료되었습니다.")
