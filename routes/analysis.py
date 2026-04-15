from fastapi import APIRouter
from fastapi.responses import StreamingResponse
import cache
from services.gemini import stream_analysis

router = APIRouter()

@router.get("/stream/analysis")
async def analysis():
    price_data = cache.get_cache("price") or {}
    supply_data = cache.get_cache("supply") or {}
    community_data = cache.get_cache("community") or {}

    ctx = {
        "price": price_data.get("price", 0),
        "change_pct": price_data.get("change_pct", 0.0),
        "foreigner": supply_data.get("foreigner", 0),
        "institution": supply_data.get("institution", 0),
        "individual": supply_data.get("individual", 0),
        "short_ratio": supply_data.get("short_ratio", 0.0),
        "sentiment_score": community_data.get("sentiment_score", 50),
        "naver_board": community_data.get("naver_board", ""),
        "stock_gallery": community_data.get("stock_gallery", ""),
    }

    return StreamingResponse(
        stream_analysis(ctx),
        media_type="text/event-stream",
        headers={
            "Cache-Control": "no-cache",
            "X-Accel-Buffering": "no",
        },
    )
