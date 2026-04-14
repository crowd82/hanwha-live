from datetime import datetime, timedelta
import FinanceDataReader as fdr
import pandas as pd

TICKER = "088350"  # 한화생명 KRX 코드

def get_current_price() -> dict:
    """현재가, 등락률, 거래량, 보조 지표 반환"""
    today = datetime.now().strftime("%Y-%m-%d")
    week_ago = (datetime.now() - timedelta(days=7)).strftime("%Y-%m-%d")

    df = fdr.DataReader(TICKER, week_ago, today)
    if df.empty:
        return {"price": 0, "change": 0, "change_pct": 0.0, "volume": 0, "open": 0,
                "high_52w": 0, "low_52w": 0, "market_cap_billion": 0}

    latest = df.iloc[-1]
    prev = df.iloc[-2] if len(df) >= 2 else df.iloc[-1]

    price = float(latest["Close"])
    prev_close = float(prev["Close"])
    change = price - prev_close
    change_pct = round((change / prev_close) * 100, 2) if prev_close else 0.0

    # 52주 고저
    year_ago = (datetime.now() - timedelta(days=365)).strftime("%Y-%m-%d")
    df_year = fdr.DataReader(TICKER, year_ago, today)
    if not df_year.empty and "High" in df_year.columns and "Low" in df_year.columns:
        high_52w = float(df_year["High"].max())
        low_52w = float(df_year["Low"].min())
    else:
        high_52w = price
        low_52w = price

    return {
        "price": price,
        "change": round(change, 0),
        "change_pct": change_pct,
        "volume": int(latest.get("Volume", 0)),
        "open": float(latest.get("Open", price)),
        "high_52w": high_52w,
        "low_52w": low_52w,
        "market_cap_billion": round(price * 467_000_000 / 1_0000_0000, 0),  # 발행주식수 기준 추정
    }

def get_chart_data(period: str) -> list:
    """period: 'annual' | 'monthly' | 'weekly' → Lightweight Charts 형식 반환"""
    today = datetime.now()
    if period == "annual":
        start = (today - timedelta(days=365)).strftime("%Y-%m-%d")
    elif period == "monthly":
        start = (today - timedelta(days=30)).strftime("%Y-%m-%d")
    else:  # weekly
        start = (today - timedelta(days=7)).strftime("%Y-%m-%d")

    df = fdr.DataReader(TICKER, start, today.strftime("%Y-%m-%d"))
    if df.empty:
        return []

    result = []
    for date, row in df.iterrows():
        result.append({
            "time": date.strftime("%Y-%m-%d"),
            "value": float(row["Close"]),
            "volume": int(row.get("Volume", 0)),
        })
    return result
