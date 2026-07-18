$filepath = 'c:\Users\user1\Downloads\ICB10_proj2\korea-trip-data\src\views\demand_analysis.py'
$content = [System.IO.File]::ReadAllText($filepath, [System.Text.Encoding]::UTF8)

$marker1 = '        st.subheader("📍 지역별 축제·체험·문화 인프라 분석")'
$marker2 = '        import sqlite3' + [Environment]::NewLine + '        db_path = os.path.join(data_dir, ''tourist_spots.db'')'
$marker3 = '        st.markdown(''---'')' + [Environment]::NewLine + '        st.markdown("### 4. 🔍 지역 인프라와 방문 규모 상관관계 분석")'

$parts1 = $content -split [Regex]::Escape($marker1), 2
$part_before_A = $parts1[0]
$rest1 = $parts1[1]

$parts2 = $rest1 -split [Regex]::Escape($marker2), 2
$block_A_content = $parts2[0]
$rest2 = $parts2[1]

$parts3 = $rest2 -split [Regex]::Escape($marker3), 2
$block_B_content = $parts3[0]
$part_after_B = $parts3[1]

$block_A = $marker1 + $block_A_content
$block_B = $marker2 + $block_B_content

$new_content = $part_before_A + $block_B + [Environment]::NewLine + '        st.markdown(''---'')' + [Environment]::NewLine + [Environment]::NewLine + $block_A + $marker3 + $part_after_B

[System.IO.File]::WriteAllText($filepath, $new_content, [System.Text.Encoding]::UTF8)
