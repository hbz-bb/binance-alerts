from __future__ import annotations
import json
from pathlib import Path
from typing import Set

DEFAULT_PATH = Path("data/seen.json")

def load_seen(path: Path = DEFAULT_PATH) -> Set[str]:
    path.parent.mkdir(parents=True, exist_ok=True)
    if not path.exists():
        return set()
    try:
        data = json.loads(path.read_text(encoding="utf-8"))
        if isinstance(data, list):
            return set(str(x) for x in data)
    except Exception:
        pass
    return set()

def save_seen(seen: Set[str], path: Path = DEFAULT_PATH) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    path.write_text(json.dumps(sorted(seen), ensure_ascii=False, indent=2), encoding="utf-8")
