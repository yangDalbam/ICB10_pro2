import re

with open('seoul-pops/src/app.py', 'r', encoding='utf-8') as f:
    content = f.read()

# 1. Remove save_plot from tab2
content = re.sub(r'(\s+)utils\.save_plot\((fig\d+), "(.*?)"\)', r'\1# utils.save_plot(\2, "\3")', content)

# 2. Add 'fig' to charts_info
for i in range(1, 16):
    content = re.sub(rf"(charts_info\.append\(\{{)'title': (.*?)chart{i}_(.*?)\.png", rf"\g<1>'fig': fig{i}, 'title': \g<2>chart{i}_\g<3>.png", content)

# 3. Update tab3 logic
old_tab3 = '''        with st.spinner("리포트를 생성 중입니다..."):
            report_path = utils.generate_report_markdown(charts_info)'''
new_tab3 = '''        with st.spinner("리포트에 포함할 시각화 차트 이미지를 추출하고 리포트를 생성 중입니다. (약 5~10초 소요)..."):
            for info in charts_info:
                if 'fig' in info and info['fig'] is not None:
                    utils.save_plot(info['fig'], info['filename'])
            report_path = utils.generate_report_markdown(charts_info)'''
content = content.replace(old_tab3, new_tab3)

with open('seoul-pops/src/app.py', 'w', encoding='utf-8') as f:
    f.write(content)
print("app.py patched!")
