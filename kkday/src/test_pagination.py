import requests
import json

url = "https://www.kkday.com/api/_nuxt/category/get-search-products"
csrf_token = "410730b3-5977-4246-8966-fec4214f0a5a"

headers = {
    "accept-language": "ko-KR,ko;q=0.9,en-US;q=0.8,en;q=0.7",
    "referer": "https://www.kkday.com/ko/category/kr-south-korea/experiences/list",
    "user-agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "x-csrf-token": csrf_token,
    "content-type": "application/json"
}

cookies = {
    "csrf_token": csrf_token
}

payload = {"productCategory":"CATEGORY_018","destination":"D-KR-120","keyword":"","filters":{},"sort":"prec","page":1,"count":10}

response = requests.post(url, headers=headers, cookies=cookies, json=payload)
if response.status_code == 200:
    data = response.json()
    print("Keys in data:", list(data.keys()))
    if 'total_count' in data:
        print("total_count:", data['total_count'])
    if 'total_page' in data:
        print("total_page:", data['total_page'])
    if 'meta' in data:
        print("meta:", data['meta'])
