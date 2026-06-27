"""
Klook 상세 페이지 스크래핑 테스트 (curl_cffi)
"""
from curl_cffi import requests
from bs4 import BeautifulSoup

url = "https://www.klook.com/ko/activity/96156-everland-ticket-korea/"

response = requests.get(url, impersonate="chrome110")
print(f"Status Code: {response.status_code}")

if response.status_code == 200:
    soup = BeautifulSoup(response.text, 'html.parser')
    title = soup.find('h1')
    print("Title:", title.text if title else 'Not found')
    
    # Check for state
    scripts = soup.find_all('script')
    for s in scripts:
        if s.string and 'window.__INITIAL_STATE__' in s.string:
            print("Found window.__INITIAL_STATE__")
            break
