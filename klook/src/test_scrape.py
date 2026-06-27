"""
Klook 상세 페이지 스크래핑 테스트 (Playwright)
"""
import asyncio
from playwright.async_api import async_playwright

async def main():
    async with async_playwright() as p:
        browser = await p.chromium.launch(headless=True)
        context = await browser.new_context(
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
        )
        page = await context.new_page()
        
        url = "https://www.klook.com/ko/activity/96156-everland-ticket-korea/"
        
        print("Navigating to:", url)
        response = await page.goto(url, wait_until="networkidle")
        
        print(f"Status Code: {response.status if response else 'Unknown'}")
        
        title = await page.title()
        print(f"Title: {title}")
        
        # Look for window.__INITIAL_STATE__
        state = await page.evaluate("() => { return window.__INITIAL_STATE__ ? Object.keys(window.__INITIAL_STATE__) : null }")
        print("Initial state keys:", state)
        
        await browser.close()

if __name__ == "__main__":
    asyncio.run(main())
