from __future__ import annotations
import requests
from dataclasses import dataclass
from typing import List, Optional
import os

DEBUG = os.getenv("DEBUG_BINANCE", "0") == "1"

def dprint(*args, **kwargs):
    if DEBUG:
        print(*args, **kwargs)

BASE = "https://www.binance.com"

@dataclass(frozen=True)
class Item:
    title: str
    url: str
    date: Optional[str] = None

def _get_json(url: str) -> dict:
    headers = {
        "User-Agent": "Mozilla/5.0 (Macintosh; Intel Mac OS X) AppleWebKit/537.36 (KHTML, like Gecko) Chrome Safari",
        "Accept-Language": "en-US,en;q=0.9",
        "Accept": "application/json,text/plain,*/*",
    }
    r = requests.get(url, headers=headers, timeout=20)
    # print("HTTP", r.status_code, "url=", r.url, "len=", len(r.content), "ct=", r.headers.get("content-type"))
    dprint("HTTP", r.status_code, "url=", r.url, "len=", len(r.content), "ct=", r.headers.get("content-type"))
    r.raise_for_status()
    return r.json()

def fetch_sources() -> List[Item]:
    api = f"{BASE}/bapi/composite/v1/public/cms/article/list/query?type=1&pageNo=1&pageSize=50"
    payload = _get_json(api)

    # Binance bapi 常见结构：{"code":"000000","message":null,"data":{...}}
    data = payload.get("data")

    if not isinstance(data, dict):
        print("Unexpected: payload.data is not dict:", type(data))
        return []

    # 可能的文章列表字段名集合（不同版本/不同type会变）
    candidates = [
        "articles",
        "articleList",
        "rows",
        "list",
        "data",         # 有时会嵌一层 data
        "catalogs",     # 有时是按目录返回 catalogs -> articles
        "result",
    ]

    articles = None

    # 1) 直接命中
    for k in candidates:
        v = data.get(k)
        if isinstance(v, list) and v and isinstance(v[0], dict) and ("title" in v[0] or "code" in v[0]):
            articles = v
            break

    # 2) catalogs 结构：catalogs = [{..., "articles":[...]}]
    if articles is None and isinstance(data.get("catalogs"), list):
        merged = []
        for c in data["catalogs"]:
            if isinstance(c, dict) and isinstance(c.get("articles"), list):
                merged.extend([a for a in c["articles"] if isinstance(a, dict)])
        if merged:
            articles = merged

    # 3) 嵌套一层 data：data["data"]["articles"]
    if articles is None and isinstance(data.get("data"), dict):
        inner = data["data"]
        for k in candidates:
            v = inner.get(k)
            if isinstance(v, list) and v and isinstance(v[0], dict) and ("title" in v[0] or "code" in v[0]):
                articles = v
                break

    if articles is None:
        # print("Could not locate articles list. data_keys=", list(data.keys()))
        # # 打印一小段帮助你在 Actions 日志里定位
        # print("data_preview=", str(data)[:1200])
        dprint("Could not locate articles list. data_keys=", list(data.keys()))
        dprint("data_preview=", str(data)[:1200])
        return []

    items: List[Item] = []
    for a in articles:
        title = (a.get("title") or a.get("headline") or "").strip()

        # 常见标识字段
        code = a.get("code") or a.get("id") or a.get("articleCode")

        # 有的直接给 url
        url = a.get("url")

        # 有的给 "releaseDate"/"releaseTime"/"publishDate"
        date = a.get("releaseDate") or a.get("releaseTime") or a.get("publishDate")

        if not url and code:
            # detail 路径可能不是这个，但先留着；如果 JSON 有 url 字段会优先用
            url = f"{BASE}/en/support/announcement/detail/{code}"

        if title and url:
            items.append(Item(title=title, url=url, date=str(date) if date else None))

    # print("parsed_items=", len(items))
    dprint("parsed_items=", len(items))

    return items

