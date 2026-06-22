from bs4 import BeautifulSoup
import json
import re

with open('trip_com/data/page.html', encoding='utf-8') as f:
    soup = BeautifulSoup(f, 'html.parser')

results = []
# Find all text nodes that have some length and look like a review
for el in soup.find_all(['p', 'div', 'span']):
    text = el.get_text(strip=True)
    if len(text) > 30 and len(text) < 500:
        cls = el.get('class')
        if cls:
            results.append({"tag": el.name, "class": " ".join(cls), "text": text[:50]})

# Write to a JSON file to view
with open('trip_com/data/classes.json', 'w', encoding='utf-8') as f:
    json.dump(results, f, ensure_ascii=False, indent=2)
