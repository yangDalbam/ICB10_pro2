"""
이 모듈은 정제된 리뷰 데이터(제목, 내용, 제품명 결합)를 바탕으로 6개 주제의 NMF 토픽 모델링을 수행합니다.
주요 기능:
- 6개의 토픽 추출 및 시각화
- 토픽별 상위 30개 키워드 및 TF-IDF 가중치 표 생성
- 데이터 상위/하위 5개 행에 대한 토픽 가중치 표(색상 포함) 생성
"""
import pandas as pd
import numpy as np
import matplotlib.pyplot as plt
import seaborn as sns
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.decomposition import NMF
import os
import re
import importlib

# 설정
sns.reset_orig()
import koreanize_matplotlib
importlib.reload(koreanize_matplotlib)
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
df['product'] = df['product'].fillna('')

# 1. 제목, 내용, 제품을 공백 기준으로 결합
df['full_text'] = df['title'] + ' ' + df['content'] + ' ' + df['product']

stop_words = ['너무', '정말', '진짜', '아주', '많이', '조금', '매우', '그리고', '근데', '하지만', '좋습니다', '좋아요', '같아요', '입니다', '있습니다', '하는', '것', '수', '이', '그', '저', '있는', '없는', '대한', '대해', '위해']

def clean_text(text):
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', text)
    words = text.split()
    words = [w for w in words if w not in stop_words and len(w) > 1]
    return ' '.join(words)

df['cleaned_text'] = df['full_text'].apply(clean_text)

# 토픽 모델링 (NMF, 6 topics)
n_topics = 6
vectorizer = TfidfVectorizer(max_features=1000)
tfidf_matrix = vectorizer.fit_transform(df['cleaned_text'])
feature_names = vectorizer.get_feature_names_out()

nmf = NMF(n_components=n_topics, random_state=42)
W = nmf.fit_transform(tfidf_matrix)
H = nmf.components_

for i in range(n_topics):
    df[f'Topic_{i+1}_Weight'] = W[:, i]

write_md('\n## 8. 리뷰 텍스트 심층 토픽 모델링 (6개 주제)\n')

# 시각화 (3행 2열)
fig, axes = plt.subplots(3, 2, figsize=(16, 18))
axes = axes.flatten()

topic_keywords = []

for topic_idx, topic in enumerate(H):
    top_indices = topic.argsort()[:-31:-1]
    top_keywords = [(feature_names[i], topic[i]) for i in top_indices]
    topic_keywords.append(top_keywords)
    
    ax = axes[topic_idx]
    words, weights = zip(*top_keywords[:15]) # 차트에는 상위 15개만 표시
    ax.barh(words[::-1], weights[::-1], color='mediumpurple')
    ax.set_title(f'Topic {topic_idx + 1}')
    ax.set_xlabel('TF-IDF Weight')

plt.tight_layout()
topic_img = 'plot_topic_modeling_6.png'
plt.savefig(os.path.join(IMG_DIR, topic_img), bbox_inches='tight')
plt.close()

write_md(f'![토픽 모델링(6개)](../images/{topic_img})\n')

# 토픽별 상위 30개 키워드 표 생성
write_md('### 토픽별 상위 30개 키워드 및 가중치 (6개 주제)\n')
header = "| 순위 | " + " | ".join([f"Topic {i+1} 키워드 | Topic {i+1} 가중치" for i in range(n_topics)]) + " |"
separator = "|" + "---|"* (1 + 2*n_topics)
write_md(header)
write_md(separator)

for rank in range(30):
    row = f"| {rank + 1} | "
    for i in range(n_topics):
        word, weight = topic_keywords[i][rank]
        row += f"{word} | {weight:.4f} | "
    write_md(row)

write_md('\n### 6개 토픽별 인사이트 및 주제 정리\n')
write_md('<!-- INSIGHT_PLACEHOLDER_6 -->\n')

# 데이터 상하위 5개 행 가중치 표 생성
write_md('### 데이터 상/하위 5개 행의 토픽 가중치 (6개 주제)\n')

def get_color(val):
    if val >= 0.1: return f'<span style="color:red; font-weight:bold">{val:.4f}</span>'
    elif val >= 0.05: return f'<span style="color:blue">{val:.4f}</span>'
    elif val > 0.01: return f'<span style="color:green">{val:.4f}</span>'
    else: return f'<span style="color:gray">{val:.4f}</span>'

write_md("| 데이터 | 제목 | Topic 1 | Topic 2 | Topic 3 | Topic 4 | Topic 5 | Topic 6 |")
write_md("|---|---|---|---|---|---|---|---|")

for idx, row in df.head(5).iterrows():
    title = str(row['title']).replace('|', '&#124;')
    title = (title[:30] + '...') if len(title) > 30 else title
    weights_str = " | ".join([get_color(row[f'Topic_{i}_Weight']) for i in range(1, 7)])
    write_md(f"| 상위 {idx+1} | {title} | {weights_str} |")

for i, (idx, row) in enumerate(df.tail(5).iterrows()):
    title = str(row['title']).replace('|', '&#124;')
    title = (title[:30] + '...') if len(title) > 30 else title
    weights_str = " | ".join([get_color(row[f'Topic_{i}_Weight']) for i in range(1, 7)])
    write_md(f"| 하위 {5-i} | {title} | {weights_str} |")

write_md('\n')
print("6개 주제 토픽 모델링 처리 완료.")
