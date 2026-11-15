import urllib.request
import urllib.parse
import os

draft_dir = r"g:\マイドライブ\git\nobuyukitakahashi\02_Creative_Dept\davinci\drafts\2026-11-13_南信州広域連合議会_全員協議会"

urls = {
    "roster.pdf": "https://gikai.minami.nagano.jp/wp-content/uploads/2026/06/名簿／【各委員会別】／R3～.pdf",
    "zenkyo_minutes.pdf": "https://gikai.minami.nagano.jp/wp-content/uploads/2026/09/南信州広域連合全員協議会R80525.pdf",
    "zenkyo_feb_minutes.pdf": "https://gikai.minami.nagano.jp/wp-content/uploads/2026/05/令和８年２月25日-全員協議会.pdf",
}

for fname, u in urls.items():
    p = urllib.parse.urlsplit(u)
    quoted_url = urllib.parse.urlunsplit((p.scheme, p.netloc, urllib.parse.quote(p.path), p.query, p.fragment))
    out_p = os.path.join(draft_dir, fname)
    req = urllib.request.Request(quoted_url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req, timeout=15) as resp, open(out_p, "wb") as f:
        f.write(resp.read())
    print("Downloaded:", out_p, os.path.getsize(out_p))
