import urllib.request
import re
import os

draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合議会_全員協議会"

req = urllib.request.Request("https://gikai.minami.nagano.jp/", headers={"User-Agent": "Mozilla/5.0"})
html = urllib.request.urlopen(req, timeout=10).read().decode("utf-8", errors="ignore")
links = re.findall(r'href=["\'](https://gikai\.minami\.nagano\.jp/[^"\']+)["\']', html)
for l in sorted(set(links)):
    if not any(x in l for x in ["wp-content/plugins", "wp-includes", "wp-json", "xmlrpc", "feed"]):
        print("Link:", l)
        if "member" in l or "giin" in l or "introduce" in l or "about" in l or "list" in l or l.count("/") == 4:
            try:
                sub = urllib.request.urlopen(urllib.request.Request(l, headers={"User-Agent": "Mozilla/5.0"}), timeout=10).read().decode("utf-8", errors="ignore")
                pdfs = re.findall(r'href=["\']([^"\']+\.pdf)["\']', sub, re.I)
                if pdfs:
                    print("  PDFs on", l, ":", pdfs)
                    for idx, pdf_url in enumerate(pdfs):
                        out_pdf = os.path.join(draft_dir, f"roster_{idx}.pdf")
                        urllib.request.urlretrieve(pdf_url, out_pdf)
                        print("  Downloaded:", out_pdf)
                sub_clean = re.sub(r'<script.*?</script>', '', sub, flags=re.S)
                sub_clean = re.sub(r'<style.*?</style>', '', sub_clean, flags=re.S)
                sub_clean = re.sub(r'<[^>]+>', ' ', sub_clean)
                sub_clean = re.sub(r'\s+', ' ', sub_clean)
                if "竹村" in sub_clean or "議員" in sub_clean:
                    print("  Text:", sub_clean[:1000])
            except Exception as e:
                print("  Err:", e)
