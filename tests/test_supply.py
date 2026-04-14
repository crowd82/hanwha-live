from unittest.mock import patch
from services.supply import get_supply_demand, _parse_number

MOCK_HTML = """
<table class="type2">
<tr>
  <td class="num">+870,000</td>
  <td class="num">+210,000</td>
  <td class="num">-1,040,000</td>
</tr>
</table>
"""

def test_get_supply_demand_returns_required_fields():
    with patch("services.supply.requests.get") as mock_get:
        mock_get.return_value.text = MOCK_HTML
        mock_get.return_value.status_code = 200

        result = get_supply_demand()

        assert "foreigner" in result
        assert "institution" in result
        assert "individual" in result
        assert "short_ratio" in result
        assert "short_trend" in result

def test_get_supply_demand_fallback_on_error():
    with patch("services.supply.requests.get") as mock_get:
        mock_get.side_effect = Exception("Network error")

        result = get_supply_demand()

        assert result["foreigner"] == 0
        assert result["institution"] == 0
        assert result["individual"] == 0
        assert result["short_ratio"] == 0.0
        assert result["short_trend"] == "unknown"


def test_parse_number():
    assert _parse_number("+870,000") == 870000
    assert _parse_number("-1,040,000") == -1040000
    assert _parse_number("0") == 0
