import json
import time
from scrapling import Fetcher

base_url = "https://www.klook.com/v1/cardinfocenterservicesrv/search/platform/complete_search_v3?location=158%2C157%2C156%2C25723%2C5031%2C8928%2C24975%2C28741%2C545%2C6166%2C6268%2C703649%2C703648%2C705582%2C6955%2C15088%2C701102%2C16467%2C707516%2C26374%2C7204%2C20296%2C28972%2C28785%2C8898%2C23546%2C30633%2C15378%2C16365%2C28742%2C10956%2C26961%2C10093%2C16560%2C25178%2C30570%2C7558%2C7741%2C11925%2C24865%2C25140%2C707332%2C8989%2C10706%2C11364%2C11745%2C13523%2C14446%2C15281%2C15603%2C16655%2C18214%2C18323%2C20392%2C22390%2C22675%2C23237%2C24520%2C24762%2C25060%2C26454%2C27895%2C29136%2C29872%2C30051%2C30265%2C30376%2C30466%2C31247%2C7030%2C705101%2C9079&sort=most_relevant&tab_key=0&start=1&query=%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD&size=15&search_scope=main_search&k_lang=ko_KR&k_currency=KRW"

headers = {
    "priority": "u=1, i",
    "referer": "https://www.klook.com/ko/search/result/?query=%EB%8C%80%ED%95%9C%EB%AF%BC%EA%B5%AD&search_scope=main_search&location=158,157,156,25723,5031,8928,24975,28741,545,6166,6268,703649,703648,705582,6955,15088,701102,16467,707516,26374,7204,20296,28972,28785,8898,23546,30633,15378,16365,28742,10956,26961,10093,16560,25178,30570,7558,7741,11925,24865,25140,707332,8989,10706,11364,11745,13523,14446,15281,15603,16655,18214,18323,20392,22390,22675,23237,24520,24762,25060,26454,27895,29136,29872,30051,30265,30376,30466,31247,7030,705101,9079&sort=most_relevant&tab_key=0&start=1",
    "sec-ch-ua": "\"Google Chrome\";v=\"149\", \"Chromium\";v=\"149\", \"Not)A;Brand\";v=\"24\"",
    "user-agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/149.0.0.0 Safari/537.36",
    "x-klook-market": "global",
    "x-platform": "desktop",
    "x-requested-with": "XMLHttpRequest"
}

fetcher = Fetcher()
response = fetcher.get(base_url, headers=headers)

if response.status == 200:
    data = response.json()
    with open("test_klook.json", "w", encoding="utf-8") as f:
        json.dump(data, f, ensure_ascii=False, indent=2)
    print("Saved test_klook.json")
else:
    print("Error:", response.status)
