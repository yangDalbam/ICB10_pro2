import pandas as pd
df = pd.read_csv(r'c:\Users\user1\Downloads\ICB10_proj2\burger_index\data\burger.csv')
subset = df[df['상권업종대분류명'].isin(['과학·기술', '교육'])][['상호명', '상권업종대분류명', '상권업종중분류명', '도로명주소']]
output_path = r'c:\Users\user1\Downloads\ICB10_proj2\burger_index\report\special_categories.md'
with open(output_path, 'w', encoding='utf-8') as f:
    f.write(subset.to_markdown(index=False))
