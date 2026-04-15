from unittest.mock import patch, MagicMock
from services.gemini import build_prompt, parse_predicted_price

def test_build_prompt_contains_required_sections():
    ctx = {
        "price": 3480, "change_pct": 2.35,
        "foreigner": 870000, "institution": 210000, "individual": -1040000,
        "short_ratio": 1.24,
        "naver_board": "외인이 쓸어담는다",
        "stock_gallery": "3600 간다",
        "sentiment_score": 74,
    }
    prompt = build_prompt(ctx)
    assert "한화생명" in prompt
    assert "3,480" in prompt
    assert "파트1" in prompt
    assert "파트2" in prompt

def test_parse_predicted_price_extracts_number():
    text = "예상 마감가: 3,510원 (신뢰도 72%, 범위 3,380~3,620원)"
    result = parse_predicted_price(text)
    assert result["price"] == 3510
    assert result["confidence"] == 72
    assert result["low"] == 3380
    assert result["high"] == 3620

def test_parse_predicted_price_fallback():
    text = "분석 결과 상승이 예상됩니다."
    result = parse_predicted_price(text)
    assert result["price"] is None
