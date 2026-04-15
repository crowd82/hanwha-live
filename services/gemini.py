import os
import re
import json
from typing import Generator
from dotenv import load_dotenv
from google import genai
from google.genai import types

load_dotenv()

_client = None

def _get_client():
    global _client
    if _client is None:
        _client = genai.Client(api_key=os.getenv("GEMINI_API_KEY"))
    return _client

def build_prompt(ctx: dict) -> str:
    foreigner_str = f"+{ctx['foreigner']:,}" if ctx['foreigner'] > 0 else f"{ctx['foreigner']:,}"
    institution_str = f"+{ctx['institution']:,}" if ctx['institution'] > 0 else f"{ctx['institution']:,}"
    individual_str = f"+{ctx['individual']:,}" if ctx['individual'] > 0 else f"{ctx['individual']:,}"

    return f"""당신은 한국 주식시장 전문 애널리스트입니다. Google Search를 활용해 최신 정보를 검색하세요.

현재 데이터 (한화생명 088350):
- 현재가: {ctx['price']:,}원 (전일 대비 {ctx['change_pct']:+.2f}%)
- 외국인 수급: {foreigner_str}주
- 기관 수급: {institution_str}주
- 개인 수급: {individual_str}주
- 공매도 잔고율: {ctx['short_ratio']}%
- 시장 감성 점수: {ctx['sentiment_score']}/100
- 커뮤니티 (네이버 토론방): {ctx['naver_board']}
- 커뮤니티 (주식갤러리): {ctx['stock_gallery']}

Google Search로 다음을 검색하세요:
1. "한화생명 088350 오늘" - 오늘 주가 관련 뉴스
2. "한국은행 기준금리 동향" - 금리 관련 최신 뉴스
3. "한화생명 공시 최근" - 최근 공시 내용

위 데이터와 검색 결과를 종합해 다음 형식으로 정확히 답하세요:

[예상마감가]
예상 마감가: X,XXX원 (신뢰도 XX%, 범위 X,XXX~X,XXX원)

[파트1: 지금 {'오르는' if ctx['change_pct'] > 0 else '내리는'} 이유]
(3~4문장. 인과관계 중심. 구체적 수치 포함. 한국어.)

[파트2: 마감 예상 근거]
(3~4문장. 예측가 도출 근거, 오후 시나리오, 주요 리스크 변수. 한국어.)

전문적이되 읽기 쉬운 한국어로 작성하세요.
"""

def parse_predicted_price(text: str) -> dict:
    price_match = re.search(r"예상\s*마감가[:\s]*([0-9,]+)원", text)
    confidence_match = re.search(r"신뢰도\s*(\d+)%", text)
    range_match = re.search(r"범위\s*([0-9,]+)~([0-9,]+)원", text)

    price = int(price_match.group(1).replace(",", "")) if price_match else None
    confidence = int(confidence_match.group(1)) if confidence_match else 60
    low = int(range_match.group(1).replace(",", "")) if range_match else None
    high = int(range_match.group(2).replace(",", "")) if range_match else None

    return {"price": price, "confidence": confidence, "low": low, "high": high}

def stream_analysis(ctx: dict) -> Generator:
    client = _get_client()
    prompt = build_prompt(ctx)

    try:
        response = client.models.generate_content_stream(
            model="gemini-1.5-flash",
            contents=prompt,
            config=types.GenerateContentConfig(
                tools=[types.Tool(google_search=types.GoogleSearch())],
                temperature=0.7,
            ),
        )

        full_text = ""
        for chunk in response:
            if chunk.text:
                full_text += chunk.text
                yield f"data: {json.dumps({'type': 'text', 'content': chunk.text}, ensure_ascii=False)}\n\n"

        predicted = parse_predicted_price(full_text)
        yield f"data: {json.dumps({'type': 'predicted_price', **predicted}, ensure_ascii=False)}\n\n"
        yield f"data: {json.dumps({'type': 'done'})}\n\n"

    except Exception as e:
        yield f"data: {json.dumps({'type': 'error', 'message': str(e)})}\n\n"
