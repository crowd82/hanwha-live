import requests
from bs4 import BeautifulSoup

HEADERS = {
    "User-Agent": "Mozilla/5.0 (iPhone; CPU iPhone OS 17_0 like Mac OS X) AppleWebKit/605.1.15"
}
TICKER = "088350"

POSITIVE_KEYWORDS = ["매수", "상승", "급등", "돌파", "외인", "기관", "금리인하", "실적", "좋다", "오른다", "추천"]
NEGATIVE_KEYWORDS = ["매도", "하락", "급락", "손절", "리스크", "위험", "조정", "떨어진다", "위기"]

def _calc_sentiment(texts: list) -> int:
    """키워드 기반 감성 점수 0~100 산출"""
    if not texts:
        return 50
    pos = sum(1 for t in texts for k in POSITIVE_KEYWORDS if k in t)
    neg = sum(1 for t in texts for k in NEGATIVE_KEYWORDS if k in t)
    total = pos + neg
    if total == 0:
        return 50
    score = int((pos / total) * 100)
    return max(0, min(100, score))

def _scrape_naver_board() -> list:
    """네이버 종목토론방 최근 글 제목 수집"""
    try:
        url = f"https://finance.naver.com/item/board.nhn?code={TICKER}"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        titles = []
        for a in soup.select("td.title a"):
            title = a.get_text().strip()
            if title:
                titles.append(title)
        return titles[:10]
    except Exception:
        return []

def _scrape_stock_gallery() -> list:
    """DC 주식 갤러리 한화생명 관련 글 제목 수집"""
    try:
        url = "https://gall.dcinside.com/board/lists/?id=stock_main&s_type=search_subject_memo&s_keyword=한화생명"
        resp = requests.get(url, headers=HEADERS, timeout=10)
        soup = BeautifulSoup(resp.text, "html.parser")

        titles = []
        for a in soup.select("td.gall_tit a:not(.reply_num)"):
            title = a.get_text().strip()
            if title and "한화생명" in title:
                titles.append(title)
        return titles[:5]
    except Exception:
        return []

def get_community_sentiment() -> dict:
    """커뮤니티 민심 요약 및 감성 점수 반환"""
    naver_titles = _scrape_naver_board()
    gallery_titles = _scrape_stock_gallery()

    all_titles = naver_titles + gallery_titles
    sentiment_score = _calc_sentiment(all_titles)

    # 대표 글 2개씩 요약
    naver_summary = " | ".join(naver_titles[:2]) if naver_titles else "수집 중..."
    gallery_summary = " | ".join(gallery_titles[:2]) if gallery_titles else "수집 중..."

    return {
        "naver_board": naver_summary,
        "stock_gallery": gallery_summary,
        "sentiment_score": sentiment_score,
        "raw_titles": all_titles[:10],
    }
