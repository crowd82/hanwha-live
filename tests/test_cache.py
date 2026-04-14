from cache import get_cache, set_cache, is_stale
import time

def test_set_and_get():
    set_cache("price", {"value": 3480})
    data = get_cache("price")
    assert data["value"] == 3480

def test_is_stale_when_empty():
    assert is_stale("nonexistent_key", max_age=60) is True

def test_is_stale_when_fresh():
    set_cache("fresh_key", {"value": 1})
    assert is_stale("fresh_key", max_age=60) is False

def test_is_stale_when_old(monkeypatch):
    set_cache("old_key", {"value": 1})
    # 캐시 타임스탬프를 100초 전으로 조작
    import cache as c
    c._store["old_key"]["updated_at"] -= 100
    assert is_stale("old_key", max_age=60) is True
