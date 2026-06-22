import json
import re

def parse():
    with open('trip_com/data/non_headless_page.html', encoding='utf-8') as f:
        html = f.read()
    
    print("Length of html:", len(html))
    print("INITIAL_STATE in html:", 'INITIAL_STATE' in html)
    print("NEXT_DATA in html:", '__NEXT_DATA__' in html)
    
    m = re.search(r'<script id="__NEXT_DATA__" type="application/json">(.*?)</script>', html, re.DOTALL)
    if m:
        try:
            data = json.loads(m.group(1))
            with open('trip_com/data/next_data.json', 'w', encoding='utf-8') as out:
                json.dump(data, out, ensure_ascii=False, indent=2)
            print("next_data.json written. length:", len(m.group(1)))
        except Exception as e:
            print("Error parsing JSON:", e)
    else:
        print("NEXT_DATA not found.")
        
if __name__ == '__main__':
    parse()
