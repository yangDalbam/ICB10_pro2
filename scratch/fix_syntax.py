import os

file_path = 'korea-trip-data/src/views/demand_analysis.py'
with open(file_path, 'r', encoding='utf-8') as f:
    content = f.read()

# Fix the literal \\n strings that were written
content = content.replace('\\\\n        st.markdown(\\'---\\')\\\\n', '\\n        st.markdown("---")\\n')

with open(file_path, 'w', encoding='utf-8') as f:
    f.write(content)
