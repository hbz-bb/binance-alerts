from __future__ import annotations
from datetime import datetime
from typing import List

from config import load_config
from fetch_binance import fetch_sources, Item
from notify_telegram import send_telegram
#from notify_email import send_email
from store import load_seen, save_seen

def format_item(it: Item) -> str:
    d = f" ({it.date})" if it.date else ""
    return f"- {it.title}{d}\n  {it.url}"

def run() -> int:
    cfg = load_config()
    if not cfg.tg_token or not cfg.tg_chat_id:
        raise SystemExit("Missing TELEGRAM_BOT_TOKEN / TELEGRAM_CHAT_ID in .env")

    seen = load_seen()
    items = fetch_sources()
    #抓取完发个信息提示
    send_telegram(cfg.tg_token, cfg.tg_chat_id, f"✅ binance-alerts ran. items_found={len(items)}")

    # 只推送“没见过的”
    new_items: List[Item] = [it for it in items if it.url not in seen]

    if not new_items:
        return 0

    # 为了避免一次推太多，按抓到的顺序取前 N 条
    new_items = new_items[:10]

    now = datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
    text = "🟡 Binance update detected\n" + f"Time: {now}\n\n" + "\n\n".join(format_item(it) for it in new_items)

    send_telegram(cfg.tg_token, cfg.tg_chat_id, text)


    for it in new_items:
        seen.add(it.url)
    save_seen(seen)
    return 0

if __name__ == "__main__":
    raise SystemExit(run())
