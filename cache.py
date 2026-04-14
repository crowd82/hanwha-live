import time
from typing import Any, Optional

_store: dict = {}

def set_cache(key: str, data: Any) -> None:
    _store[key] = {"data": data, "updated_at": time.time()}

def get_cache(key: str) -> Optional[Any]:
    entry = _store.get(key)
    return entry["data"] if entry else None

def is_stale(key: str, max_age: int) -> bool:
    entry = _store.get(key)
    if not entry:
        return True
    return (time.time() - entry["updated_at"]) > max_age
