"""
=====================================================
BLISSFINITY SIGNAL
FastAPI Server
=====================================================
"""

from fastapi import FastAPI
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware

from database.repository import (
    get_statistics,
    get_open_trades,
    get_trade_history,
)

app = FastAPI(
    title="Blissfinity API",
    version="1.0.0",
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=[
        "http://localhost:3000",
        "http://127.0.0.1:3000",
    ],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.get("/")
async def root():
    return {
        "message": "Blissfinity API Running"
    }


@app.get("/api/health")
async def health():
    return {
        "status": "online",
        "bot": "running",
    }


@app.get("/api/dashboard")
async def dashboard():
    try:
        return get_statistics()

    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "endpoint": "dashboard",
                "error": str(error),
            },
        )


@app.get("/api/signals")
async def signals():
    try:
        return get_open_trades()

    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "endpoint": "signals",
                "error": str(error),
            },
        )


@app.get("/api/trade-history")
async def trade_history():
    try:
        return get_trade_history()

    except Exception as error:
        return JSONResponse(
            status_code=500,
            content={
                "success": False,
                "endpoint": "trade-history",
                "error": str(error),
            },
        )