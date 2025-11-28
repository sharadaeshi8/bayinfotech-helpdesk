from fastapi import APIRouter
from app.services.analytics.tracker import analytics_tracker
from typing import Dict, Any

router = APIRouter()

@router.get("/summary")
async def get_summary() -> Dict[str, Any]:
    return await analytics_tracker.get_summary()

@router.get("/trends")
async def get_trends() -> Dict[str, Any]:
    return await analytics_tracker.get_trends()
