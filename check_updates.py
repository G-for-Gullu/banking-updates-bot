import requests
from bs4 import BeautifulSoup
import json
import os
import urllib3
urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

BOT_TOKEN = os.environ["BOT_TOKEN"]
CHAT_ID = os.environ["CHAT_ID"]

URLS = {
    "IBPS": "https://www.ibps.in",
    "SBI": "https://sbi.co.in/web/careers"
}

KEYWORDS = ["PO", "CLERK", "RRB", "RESULT", "SCORE", "SCORECARD", "CRP"]
DATA_FILE = "seen.json"
HEADERS = {"User-Agent": "Mozilla/5.0"}

def send(msg):
    url = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"
    requests.post(url, data={"chat_id": CHAT_ID, "text": msg})

def load_seen():
    if os.path.exists(DATA_FILE):
        with open(DATA_FILE) as f:
            return set(json.load(f))
    return set()

def save_seen(data):
    with open(DATA_FILE, "w") as f:
        json.dump(list(data), f)

def relevant(t):
    t = t.upper()
    return any(k in t for k in KEYWORDS)

def check():
    seen = load_seen()
    updates = []

    for site, url in URLS.items():
        r = requests.get(url, headers=HEADERS, timeout=20, verify=False)
        soup = BeautifulSoup(r.text, "html.parser")

        for a in soup.find_all("a", href=True):
            title = a.get_text(strip=True)
            if not title or not relevant(title):
                continue

            link = a["href"]
            full = link if link.startswith("http") else url + "/" + link
            uid = f"{site}|{title}|{full}"

            if uid not in seen:
                seen.add(uid)
                updates.append((site, title, full))

    if updates:
        for s, t, l in updates:
            send(f"📢 {s} UPDATE\n\n{t}\n{l}")
        save_seen(seen)

if __name__ == "__main__":
    check()
