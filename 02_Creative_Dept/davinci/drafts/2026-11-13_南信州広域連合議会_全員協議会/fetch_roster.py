import urllib.request
import re

for url in ["https://gikai.minami.nagano.jp/", "https://gikai.minami.nagano.jp/?page_id=31"]:
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
        html = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", errors="ignore")
        print(f"=== {url} ===")
        # Find links to pdf or text
        pdfs = re.findall(r'href=["\']([^"\']+\.pdf)["\']', html, re.I)
        print("PDFs:", pdfs)
        # Strip tags and print text
        text = re.sub(r'<[^>]+>', ' ', html)
        text = re.sub(r'\s+', ' ', text)
        print(text[:3000])
    except Exception as e:
        print(url, e)
