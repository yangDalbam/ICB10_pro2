from scrapling import StealthyFetcher
import time
import os

url = "https://kr.trip.com/hotels/detail/?cityEnName=Seoul&cityId=274&hotelId=58635410&checkIn=2026-06-22&checkOut=2026-06-23&adult=2&children=0&crn=1&ages=&curr=KRW&barcurr=KRW&hoteluniquekey=H4sIAAAAAAAA_-M6wcTFJMEkdZCJo3XuntdsQoxGBiv5La5mOR7-qhHTX1Tg4Nn6OnCHnGSRQwBPIQMYuDjMYJz08pf0RkbNmP5DXzOsHHYwMp1gbGtmWcD050OzwykWZo6XepdYDjFGVytlp1YqWZnoKJVkluSkKlkpvd7W8GoDCL3ZOeNNyw4lHaWU1OJkoASQlZibX5pXAmSbWloa6xkYAIVKEis8U8AGJCfmJJfmJJakhlQWAA0y01HKLHYuKcosCErNzSwpSQWqSkvMKU4FiQelFgNlksGCSn5AY4qgApn5eRDtBihiYYk5pakQNwAtdEuF2mFYG_uIhSk69hMLwy-gn1a5NrEydLEyTGJl4QB6dhcrR4iRc6CHka7hBdYNJ1ikFA0NDAyMTE2NzHUNEi0Tk40NknRNLE0NjE11DY1NDQ0szDR65y7_8c7YSPYUo5ShuamJpYWpubG5oaWhnqWFuXmeYXBOkkdOiQdjEJuloYWbi1uUDRezd1C4YMam-nlsPEX2UiCeIoynBeIZwniBsjtV9sYFuNpHwkSSWLPzdb2DMlaKFjA2MDJ1MXILMHowRjBWAHmMqxgZNjAy7mD8DwOMrxhB5gEA1rgozBECAAA&masterhotelid_tracelogid=100025527-0a9ac30b-495035-1351086&detailFilters=17%7C1%7E17%7E1*80%7C2%7C1%7E80%7E2*29%7C1%7E29%7E1%7C2&hotelType=normal&display=incavg&subStamp=714&isCT=true&isFlexible=F&locale=ko-KR"

def inspect():
    # Use StealthyFetcher which now uses camoufox
    # We shouldn't use headless=True with StealthyFetcher config if it doesn't support it, but camoufox defaults to headless=True
    fetcher = StealthyFetcher()
    print("Fetching page with StealthyFetcher (Camoufox)...")
    
    response = fetcher.fetch(url)
    
    # Wait for dynamic rendering (StealthyFetcher using camoufox under the hood can execute JS)
    # Actually wait, camoufox is a playwright wrapper. Does `StealthyFetcher` return a dynamic response?
    # According to scrapling docs, StealthyFetcher works like requests but with camoufox bypassing. Wait, no. `DynamicFetcher` uses playwright. 
    # If `StealthyFetcher` just returns the HTML without executing JS, we might not get reviews if they are JS-rendered!
    # Let's save it anyway.
    
    html = response.text
    data_dir = os.path.join(os.path.dirname(os.path.dirname(__file__)), "data")
    os.makedirs(data_dir, exist_ok=True)
    with open(os.path.join(data_dir, "camoufox_page.html"), "w", encoding="utf-8") as f:
        f.write(html)
    print(f"HTML saved. Length: {len(html)}")
    
    if '__NEXT_DATA__' in html:
        print("__NEXT_DATA__ found in HTML.")

if __name__ == "__main__":
    inspect()
