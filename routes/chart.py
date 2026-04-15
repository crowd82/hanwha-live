from fastapi import APIRouter, HTTPException
from fastapi.responses import JSONResponse
import cache
from services.stock import get_chart_data

router = APIRouter()

VALID_PERIODS = {"annual", "monthly", "weekly"}

@router.get("/api/chart/{period}")
async def chart(period: str):
    if period not in VALID_PERIODS:
        raise HTTPException(status_code=400, detail=f"period must be one of {VALID_PERIODS}")
    data = cache.get_cache(f"chart_{period}")
    if not data:
        data = get_chart_data(period)
        cache.set_cache(f"chart_{period}", data)
    return JSONResponse(data)
