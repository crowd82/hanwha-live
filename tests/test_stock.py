from unittest.mock import patch, MagicMock
import pandas as pd
from services.stock import get_current_price, get_chart_data

def test_get_current_price_returns_required_fields():
    with patch("services.stock.fdr.DataReader") as mock_fdr:
        mock_df = pd.DataFrame({
            "Close": [3480.0],
            "Open": [3400.0],
            "High": [3500.0],
            "Low": [3380.0],
            "Volume": [1240500],
        }, index=pd.to_datetime(["2026-04-14"]))
        mock_fdr.return_value = mock_df

        result = get_current_price()

        assert "price" in result
        assert "change_pct" in result
        assert "volume" in result
        assert result["price"] == 3480.0

def test_get_chart_data_annual_returns_list():
    with patch("services.stock.fdr.DataReader") as mock_fdr:
        dates = pd.date_range("2025-01-01", periods=10, freq="D")
        mock_df = pd.DataFrame({"Close": range(2890, 2900)}, index=dates)
        mock_fdr.return_value = mock_df

        result = get_chart_data("annual")

        assert isinstance(result, list)
        assert len(result) == 10
        assert "time" in result[0]
        assert "value" in result[0]

def test_get_chart_data_monthly():
    with patch("services.stock.fdr.DataReader") as mock_fdr:
        dates = pd.date_range("2026-03-01", periods=30, freq="D")
        mock_df = pd.DataFrame({"Close": range(3400, 3430)}, index=dates)
        mock_fdr.return_value = mock_df

        result = get_chart_data("monthly")
        assert len(result) == 30

def test_get_chart_data_weekly():
    with patch("services.stock.fdr.DataReader") as mock_fdr:
        dates = pd.date_range("2026-04-07", periods=5, freq="D")
        mock_df = pd.DataFrame({"Close": range(3450, 3455)}, index=dates)
        mock_fdr.return_value = mock_df

        result = get_chart_data("weekly")
        assert len(result) == 5
