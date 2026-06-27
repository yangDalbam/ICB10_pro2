"""
Klook 상세 페이지 스크래핑 테스트 (DrissionPage)
"""
from DrissionPage import ChromiumPage, ChromiumOptions
import time

try:
    co = ChromiumOptions()
    co.headless(True)
    co.set_argument('--no-sandbox')
    
    page = ChromiumPage(co)
    url = "https://www.klook.com/ko/activity/96156-everland-ticket-korea/"
    
    page.get(url)
    time.sleep(3) # Wait for potential JS challenge
    
    print("Page Title:", page.title)
    
    # Try to find window.__INITIAL_STATE__
    state = page.run_js("return window.__INITIAL_STATE__ ? Object.keys(window.__INITIAL_STATE__) : null;")
    print("Initial state keys:", state)
    
except Exception as e:
    print(f"Error: {e}")
finally:
    try:
        page.quit()
    except:
        pass
