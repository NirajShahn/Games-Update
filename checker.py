#!/usr/bin/env python3
"""
Free Fire Update Notifier
--------------------------
Checks a list of sources (official site, news pages, etc.) for new content.
If something new is found compared to last run, sends a Telegram message.

State (what we've already seen) is stored in state.json so the script only
alerts on things that are genuinely NEW.
"""

import json
import hashlib
import os
import sys
import time
import requests
from bs4 import BeautifulSoup

CONFIG_FILE = "config.json"
STATE_FILE = "state.json"

TELEGRAM_BOT_TOKEN = os.environ.get("TELEGRAM_BOT_TOKEN")
TELEGRAM_CHAT_ID = os.environ.get("TELEGRAM_CHAT_ID")

HEADERS = {
    "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
                  "(KHTML, like Gecko) Chrome/124.0 Safari/537.36"
}


def load_json(path, default):
    if os.path.exists(path):
        with open(path, "r", encoding="utf-8") as f:
            return json.load(f)
    return default


def save_json(path, data):
    with open(path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2, ensure_ascii=False)


def send_telegram(message: str):
    if not TELEGRAM_BOT_TOKEN or not TELEGRAM_CHAT_ID:
        print("[WARN] Telegram credentials not set. Message would have been:")
        print(message)
        return
    url = f"https://api.telegram.org/bot{TELEGRAM_BOT_TOKEN}/sendMessage"
    payload = {
        "chat_id": TELEGRAM_CHAT_ID,
        "text": message,
        "parse_mode": "HTML",
        "disable_web_page_preview": False,
    }
    try:
        r = requests.post(url, data=payload, timeout=15)
        r.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Failed to send Telegram message: {e}")


def extract_items(source):
    """
    Fetch a source page and pull out a list of (title, link) candidate items.
    Uses a CSS selector defined per-source in config.json, since every site's
    HTML structure is different.
    """
    try:
        resp = requests.get(source["url"], headers=HEADERS, timeout=20)
        resp.raise_for_status()
    except Exception as e:
        print(f"[ERROR] Could not fetch {source['name']}: {e}")
        return []

    soup = BeautifulSoup(resp.text, "html.parser")
    items = []

    selector = source.get("item_selector")
    if selector:
        elements = soup.select(selector)
    else:
        # fallback: grab all links containing likely keywords
        elements = soup.find_all("a")

    for el in elements[: source.get("max_items", 15)]:
        text = el.get_text(strip=True)
        href = el.get("href") if el.name == "a" else (el.find("a")["href"] if el.find("a") else "")
        if not text or len(text) < 8:
            continue
        if href and href.startswith("/"):
            base = "/".join(source["url"].split("/")[:3])
            href = base + href
        items.append({"title": text, "link": href or source["url"]})

    return items


def item_id(item):
    return hashlib.sha256(item["title"].strip().lower().encode("utf-8")).hexdigest()


def main():
    config = load_json(CONFIG_FILE, {"sources": []})
    state = load_json(STATE_FILE, {"seen": {}, "initialized": False})
    is_first_run = not state.get("initialized", False)

    new_findings = []

    for source in config["sources"]:
        name = source["name"]
        seen_ids = set(state["seen"].get(name, []))
        items = extract_items(source)

        current_ids = []
        for item in items:
            iid = item_id(item)
            current_ids.append(iid)
            if iid not in seen_ids:
                new_findings.append((name, item))

        # Update state: keep only ids we currently see (bounded, avoids infinite growth)
        state["seen"][name] = current_ids

    if is_first_run:
        # Baseline silently on the very first run so you don't get a flood
        # of "new" items that were actually already old news.
        print(f"First run: baselined {len(new_findings)} existing items. No alert sent.")
        state["initialized"] = True
    elif new_findings:
        lines = ["🔥 <b>Free Fire Update Alert</b> 🔥", ""]
        for name, item in new_findings[:20]:  # cap message size
            lines.append(f"📌 <b>{name}</b>: {item['title']}")
            if item.get("link"):
                lines.append(item["link"])
            lines.append("")
        message = "\n".join(lines)
        print(message)
        send_telegram(message)
    else:
        print("No new updates found.")

    save_json(STATE_FILE, state)


if __name__ == "__main__":
    main()
