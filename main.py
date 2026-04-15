from contextlib import asynccontextmanager
from fastapi import FastAPI
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse, JSONResponse
import logging

from routes.price import router as price_router
from routes.chart import router as chart_router
from routes.analysis import router as analysis_router
from scheduler import start_scheduler, stop_scheduler

logging.basicConfig(level=logging.INFO)

@asynccontextmanager
async def lifespan(app: FastAPI):
    start_scheduler()
    yield
    stop_scheduler()

app = FastAPI(lifespan=lifespan)

app.include_router(price_router)
app.include_router(chart_router)
app.include_router(analysis_router)

app.mount("/static", StaticFiles(directory="static"), name="static")

@app.get("/health")
async def health():
    return JSONResponse({"status": "ok"})

@app.get("/")
async def index():
    return FileResponse("static/index.html")

if __name__ == "__main__":
    import uvicorn
    import os
    port = int(os.getenv("PORT", 8000))
    uvicorn.run("main:app", host="0.0.0.0", port=port, reload=False)
