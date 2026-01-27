from __future__ import annotations
import re
import requests
from bs4 import BeautifulSoup
from dataclasses import dataclass
from typing import List, Optional
from urllib.parse import urljoin

BASE = "https://www.binance.com"

@dataclass(frozen=True)
class Item:
    title: str
    url: str
    date: Optional[str] = None  # 页面上常见 YYYY-MM-DD

def _get(url: str) -> str:
    # 简单 UA，避免被当成机器人概率稍微低一点
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari",
        "Accept-Language": "en-US,en;q=0.9",
    }
    r = requests.get(url, headers=headers, timeout=20)
    r.raise_for_status()
    return r.text

def parse_announcement_list(list_url: str) -> List[Item]:
    html = _get(list_url)
    soup = BeautifulSoup(html, "lxml")

    items: List[Item] = []

    # Binance 公告页面结构可能会变。这里用“尽量稳”的策略：
    # 1) 找到所有指向 /support/announcement/detail/ 的链接
    # 2) 取链接文本当标题
    # 3) 在附近尝试提取日期
    for a in soup.select('a[href*="/support/announcement/detail/"]'):
        href = a.get("href") or ""
        title = " ".join(a.get_text(" ", strip=True).split())
        if not href or not title:
            continue
        full_url = urljoin(BASE, href)

        # 尝试在父节点/兄弟节点里找日期
        date = None
        container_text = a.parent.get_text(" ", strip=True) if a.parent else ""
        m = re.search(r"\b20\d{2}-\d{2}-\d{2}\b", container_text)
        if m:
            date = m.group(0)

        items.append(Item(title=title, url=full_url, date=date))

    # 去重（同 URL 保留第一个）
    uniq = {}
    for it in items:
        uniq.setdefault(it.url, it)
    return list(uniq.values())

def fetch_sources() -> List[Item]:
    sources = [
        # 公告中心总入口（包含所有分类）
        "https://www.binance.com/en/support/announcement",

        # 备用：如果总页结构变了，这个是所有公告的列表入口
        "https://www.binance.com/en/support/announcement/list/0",
    ]
    all_items: List[Item] = []
    for url in sources:
        try:
            all_items.extend(parse_announcement_list(url))
        except Exception as e:
            print(f"Failed to fetch {url}: {e}")

    return all_items
