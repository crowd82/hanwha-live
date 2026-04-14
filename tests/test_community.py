from unittest.mock import patch
from services.community import get_community_sentiment

NAVER_BOARD_HTML = """
<ul class="lst_article">
  <li><a>한화생명 오늘 진짜 외인이 쓸어담는 거 맞지?</a></li>
  <li><a>금통위 발표 이후 보험주 다 봐야 함</a></li>
  <li><a>3500 돌파하면 추격매수 들어간다</a></li>
</ul>
"""

def test_get_community_sentiment_returns_required_fields():
    with patch("services.community.requests.get") as mock_get:
        mock_get.return_value.text = NAVER_BOARD_HTML
        mock_get.return_value.status_code = 200

        result = get_community_sentiment()

        assert "naver_board" in result
        assert "stock_gallery" in result
        assert "sentiment_score" in result
        assert isinstance(result["sentiment_score"], int)
        assert 0 <= result["sentiment_score"] <= 100

def test_sentiment_score_high_on_positive_keywords():
    with patch("services.community.requests.get") as mock_get:
        mock_get.return_value.text = """
        <ul class="lst_article">
          <li><a>한화생명 매수 추천 상승 기대 좋다</a></li>
          <li><a>외국인 매수 금리인하 상승</a></li>
        </ul>
        """
        mock_get.return_value.status_code = 200

        result = get_community_sentiment()
        assert result["sentiment_score"] >= 50
