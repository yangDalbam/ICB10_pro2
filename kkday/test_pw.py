from playwright.sync_api import sync_playwright
import time

with sync_playwright() as p:
    browser = p.chromium.launch(headless=True)
    context = browser.new_context(
        user_agent="Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
        locale="ko-KR"
    )
    
    def handle_request(request):
        if 'api' in request.url and request.method == 'POST':
            print("POST API Request:", request.url)
            print("Headers keys:", request.headers.keys())

    context.on("request", handle_request)
    
    page = context.new_page()
    page.goto("https://www.kkday.com/ko/category/kr-south-korea/experiences/list?currency=KRW")
    page.wait_for_timeout(3000)
    
    print("Evaluating scroll and click...")
    try:
        # scroll down
        page.evaluate("window.scrollTo(0, document.body.scrollHeight)")
        page.wait_for_timeout(2000)
        # Try to click any element with class containing 'next' or 'page' or just the 2nd page
        page.evaluate('''() => {
            const btns = Array.from(document.querySelectorAll('button, a'));
            const nextBtn = btns.find(b => b.textContent.trim() === '2' || b.textContent.includes('다음'));
            if(nextBtn) nextBtn.click();
        }''')
        page.wait_for_timeout(3000)
    except Exception as e:
        print("Failed:", e)
        
    browser.close()



