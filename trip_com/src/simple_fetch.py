import httpx
import json
import re

url = 'https://kr.trip.com/hotels/detail/?hotelId=58635410'
r = httpx.get(url, headers={'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'})

m = re.search(r'<script id="__NEXT_DATA__" type="application/json"[^>]*>(.*?)</script>', r.text, re.DOTALL)
if m:
    data = json.loads(m.group(1))
    with open('trip_com/data/simple_next_data.json', 'w', encoding='utf-8') as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print(f"Data saved. Length: {len(m.group(1))}")
    
    # Check if login required
    title = data.get('props', {}).get('initialState', {}).get('title', '')
    print(f"Page title in state: {title}")
else:
    print("No NEXT_DATA found.")
