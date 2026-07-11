import pandas as pd
df = pd.read_csv('korea-trip-data/data/문화체육관광부_추천여행지(20260602).csv', encoding='utf-8')
print("Top 5 Rows:")
print(df.head().to_markdown())
print("\nTidy Data Transform:")

# Create tidy data
# Example: If SPATIALCOVERAGE contains comma-separated values, we split and explode
df_tidy = df[['TITLE', 'SPATIALCOVERAGE']].copy()
# Drop NaNs just in case
df_tidy = df_tidy.dropna(subset=['SPATIALCOVERAGE'])
# Split by comma
df_tidy['SPATIALCOVERAGE'] = df_tidy['SPATIALCOVERAGE'].str.split(',')
# Explode
df_tidy = df_tidy.explode('SPATIALCOVERAGE')
df_tidy['SPATIALCOVERAGE'] = df_tidy['SPATIALCOVERAGE'].str.strip()

with open('temp_head.md', 'w', encoding='utf-8') as f:
    f.write("# Top 5 Rows of Original DataFrame\n")
    f.write(df.head().to_markdown())
    f.write("\n\n# Top 5 Rows of Tidy TITLE & SPATIALCOVERAGE\n")
    f.write(df_tidy.head().to_markdown())
