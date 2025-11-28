from fastapi import APIRouter
from app.api.endpoints import chat, tickets, metrics

api_router = APIRouter()
api_router.include_router(chat.router, prefix="/chat", tags=["chat"])
api_router.include_router(tickets.router, prefix="/tickets", tags=["tickets"])
api_router.include_router(metrics.router, prefix="/metrics", tags=["metrics"])
