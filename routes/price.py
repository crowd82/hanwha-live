from fastapi import APIRouter
from fastapi.responses import JSONResponse
import cache
from services.stock import get_current_price
from services.supply import get_supply_demand
from services.community import get_community_sentiment

router = APIRouter()

@router.get("/api/price")
async def price():
    data = cache.get_cache("price")
    if not data:
        data = get_current_price()
        cache.set_cache("price", data)
    return JSONResponse(data)

@router.get("/api/supply")
async def supply():
    data = cache.get_cache("supply")
    if not data:
        data = get_supply_demand()
        cache.set_cache("supply", data)
    return JSONResponse(data)

@router.get("/api/community")
async def community():
    data = cache.get_cache("community")
    if not data:
        data = get_community_sentiment()
        cache.set_cache("community", data)
    return JSONResponse(data)
