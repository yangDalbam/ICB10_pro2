import json
from scrapling import Fetcher
from bs4 import BeautifulSoup

url = "https://www.klook.com/ko/activity/252-everland-seoul/"
fetcher = Fetcher()
response = fetcher.get(url)

if response.status == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    scripts = soup.find_all('script', type='application/ld+json')
    ld_json_data = []
    for s in scripts:
        try:
            ld_json_data.append(json.loads(s.text))
        except:
            pass
    
    # Try finding Next.js data or Apollo state
    next_data = soup.find('script', id='__NEXT_DATA__')
    if next_data:
        try:
            print("Found Next.js data")
        except:
            pass
            
    print(json.dumps(ld_json_data, indent=2, ensure_ascii=False)[:1000])
else:
    print("Failed", response.status)
