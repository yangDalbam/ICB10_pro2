"""
이 모듈은 리뷰 텍스트 데이터의 TF-IDF 전체 단어 사전 크기를 산출하고,
상위 30개 단어에 대한 데이터 5개 행의 TF-IDF 가중치 행렬을 추출하여 리포트에 추가합니다.
주요 기능:
- max_features 제한 없는 전체 단어 사전 크기 추출
- 상위 30개 키워드에 대한 상위 5행 데이터프레임 생성 및 마크다운 추가
"""
import pandas as pd
import re
from sklearn.feature_extraction.text import TfidfVectorizer

DATA_PATH = '../data/shop-review.csv'
REPORT_PATH = '../report/eda_report.md'

try:
    df = pd.read_csv(DATA_PATH, encoding='utf-8', on_bad_lines='skip')
except:
    df = pd.read_csv(DATA_PATH, encoding='cp949', on_bad_lines='skip')

df['title'] = df['title'].fillna('')
df['content'] = df['content'].fillna('')
df['full_text'] = df['title'] + ' ' + df['content']

stop_words = ['너무', '정말', '진짜', '아주', '많이', '조금', '매우', '그리고', '근데', '하지만', '좋습니다', '좋아요', '같아요', '입니다', '있습니다', '하는', '것', '수', '이', '그', '저', '있는', '없는', '대한', '대해', '위해']

def clean_text(text):
    text = re.sub(r'<[^>]+>', ' ', text)
    text = re.sub(r'[^가-힣a-zA-Z0-9\s]', ' ', text)
    words = text.split()
    words = [w for w in words if w not in stop_words and len(w) > 1]
    return ' '.join(words)

df['cleaned_text'] = df['full_text'].apply(clean_text)

# 1. 전체 단어 사전 크기 확인
vectorizer_full = TfidfVectorizer()
vectorizer_full.fit(df['cleaned_text'])
total_vocab_size = len(vectorizer_full.get_feature_names_out())

# 2. 상위 30개 단어만 추출하여 TF-IDF 매트릭스 생성
vectorizer_top30 = TfidfVectorizer(max_features=30)
tfidf_top30 = vectorizer_top30.fit_transform(df['cleaned_text'])
feature_names_30 = vectorizer_top30.get_feature_names_out()

# 상위 5개 행을 추출
tfidf_df = pd.DataFrame(tfidf_top30[:5].toarray(), columns=feature_names_30)

def write_md(text):
    with open(REPORT_PATH, 'a', encoding='utf-8') as f:
        f.write(text + '\n')

write_md('\n## 7. TF-IDF 전체 단어 사전 및 행렬 (샘플)\n')
write_md('### 전체 단어 사전 크기')
write_md(f'- **정제 후 고유 단어(Vocabulary) 총합**: `{total_vocab_size:,}`개')
write_md('  - HTML 태그, 특수문자, 커스텀 불용어(너무, 정말 등) 및 1글자 단어를 제외한 후 공백을 기준으로 추출한 고유 단어의 개수입니다.\n')

write_md('### 상위 30개 단어의 TF-IDF 가중치 (데이터 상위 5개 행)')
write_md('전체 말뭉치에서 가장 빈도와 중요도가 높은 30개 키워드에 대해, 데이터의 첫 5개 리뷰(행)가 가지고 있는 TF-IDF 가중치를 나타냅니다. 값이 0이면 해당 단어가 해당 리뷰에 등장하지 않았음을 의미합니다.\n')
write_md(tfidf_df.round(4).to_markdown())
write_md('\n')

print("TF-IDF 단어사전 및 행렬 추출 완료")
