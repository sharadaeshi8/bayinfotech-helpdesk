from fastapi import APIRouter, HTTPException
from typing import List
from app.models.schemas import TicketCreate, TicketResponse
from app.services.analytics.tracker import analytics_tracker
from datetime import datetime
import uuid

router = APIRouter()

@router.post("/", response_model=TicketResponse)
async def create_ticket(ticket: TicketCreate):
    ticket_data = ticket.dict(exclude={'created'})  # Exclude 'created' field from frontend
    
    # Generate ID if not provided
    if not ticket_data.get("id"):
        ticket_data["id"] = f"INC-{str(uuid.uuid4())[:8]}"
    
    # Ensure title is set (validator should handle this, but be safe)
    if not ticket_data.get("title"):
        ticket_data["title"] = ticket_data.get("subject", "Untitled")
        
    # Track in analytics and save to database
    saved_ticket = await analytics_tracker.track_ticket_creation(ticket_data)
    
    # Return the saved ticket with all fields
    return {
        "id": saved_ticket.id,
        "title": saved_ticket.title,
        "description": saved_ticket.description,
        "priority": saved_ticket.priority,
        "status": saved_ticket.status,
        "tier": saved_ticket.tier,
        "tags": saved_ticket.tags,
        "sentiment": saved_ticket.sentiment,
        "sentimentScore": saved_ticket.sentiment_score,
        "kbMatch": saved_ticket.kb_match,
        "slaRisk": saved_ticket.sla_risk,
        "created_at": saved_ticket.created_at,
        "updated_at": saved_ticket.updated_at
    }

@router.get("/", response_model=List[TicketResponse])
async def get_tickets():
    tickets = await analytics_tracker.get_tickets()
    return tickets
