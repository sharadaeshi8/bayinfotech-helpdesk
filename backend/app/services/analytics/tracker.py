from typing import Dict, Any, List
from datetime import datetime, timedelta
from collections import defaultdict
import uuid
from sqlalchemy import select, func, update
from sqlalchemy.ext.asyncio import AsyncSession
from app.core.database import AsyncSessionLocal
from app.models.models import Conversation, Message, Ticket

class AnalyticsTracker:
    """Analytics tracker using PostgreSQL for persistent storage."""
    
    def __init__(self):
        self.start_time = datetime.utcnow()
        # Removed all in-memory storage - everything is now in PostgreSQL

    async def track_conversation_start(self, session_id: str):
        """Create or update conversation record."""
        async with AsyncSessionLocal() as db:
            # Check if conversation exists
            result = await db.execute(
                select(Conversation).where(Conversation.session_id == session_id)
            )
            conversation = result.scalar_one_or_none()
            
            if not conversation:
                # Create new conversation
                conversation = Conversation(
                    session_id=session_id,
                    start_time=datetime.utcnow(),
                    last_active=datetime.utcnow(),
                    message_count=0,
                    deflected=True,
                    consecutive_low_confidence=0
                )
                db.add(conversation)
                await db.commit()

    async def track_message(self, session_id: str, role: str = "user", content: str = "", 
                           confidence_score: float = 0.0, tier: str = None, sentiment: str = None):
        """Track a message in the conversation."""
        async with AsyncSessionLocal() as db:
            # Get conversation
            result = await db.execute(
                select(Conversation).where(Conversation.session_id == session_id)
            )
            conversation = result.scalar_one_or_none()
            
            if not conversation:
                # Create conversation if it doesn't exist
                conversation = Conversation(session_id=session_id)
                db.add(conversation)
                await db.flush()
            
            # Create message
            message = Message(
                conversation_id=conversation.id,
                role=role,
                content=content,
                confidence_score=confidence_score,
                tier=tier,
                sentiment=sentiment
            )
            db.add(message)
            
            # Update conversation stats
            conversation.message_count += 1
            conversation.last_active = datetime.utcnow()
            
            await db.commit()
    
    async def track_low_confidence(self, session_id: str):
        """Increment low confidence counter for a conversation."""
        async with AsyncSessionLocal() as db:
            await db.execute(
                update(Conversation)
                .where(Conversation.session_id == session_id)
                .values(consecutive_low_confidence=Conversation.consecutive_low_confidence + 1)
            )
            await db.commit()

    async def reset_low_confidence(self, session_id: str):
        """Reset low confidence counter for a conversation."""
        async with AsyncSessionLocal() as db:
            await db.execute(
                update(Conversation)
                .where(Conversation.session_id == session_id)
                .values(consecutive_low_confidence=0)
            )
            await db.commit()

    async def get_low_confidence_streak(self, session_id: str) -> int:
        """Get consecutive low confidence count for a conversation."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(
                select(Conversation.consecutive_low_confidence)
                .where(Conversation.session_id == session_id)
            )
            count = result.scalar_one_or_none()
            return count if count is not None else 0
    
    async def track_tier(self, tier: str):
        """Track tier usage (for metrics)."""
        # This could be stored in a separate table if needed
        # For now, it's tracked via messages
        pass

    async def track_ticket_creation(self, ticket_data: Dict[str, Any]):
        """Create a ticket in the database."""
        async with AsyncSessionLocal() as db:
            # Generate ID if not provided
            ticket_id = ticket_data.get("id", f"INC-{str(uuid.uuid4())[:8]}")
            
            # Check if ticket already exists (handle duplicate ID from frontend retries)
            existing_ticket = await db.execute(
                select(Ticket).where(Ticket.id == ticket_id)
            )
            existing = existing_ticket.scalar_one_or_none()
            if existing:
                return existing  # Return existing ticket instead of erroring
            
            # Get conversation if session_id provided
            conversation_id = None
            if "session_id" in ticket_data:
                result = await db.execute(
                    select(Conversation).where(Conversation.session_id == ticket_data["session_id"])
                )
                conversation = result.scalar_one_or_none()
                if conversation:
                    conversation_id = conversation.id
                    conversation.deflected = False  # Mark as not deflected
            
            # Create ticket
            ticket = Ticket(
                id=ticket_id,
                conversation_id=conversation_id,
                title=ticket_data.get("title", "Untitled"),
                description=ticket_data.get("description", ""),
                priority=ticket_data.get("priority", "Medium"),
                status=ticket_data.get("status", "Open"),
                tier=ticket_data.get("tier", "Tier 0"),
                tags=ticket_data.get("tags", []),
                sentiment=ticket_data.get("sentiment", "Neutral"),
                sentiment_score=ticket_data.get("sentimentScore", 0.0),
                kb_match=ticket_data.get("kbMatch"),
                sla_risk=ticket_data.get("slaRisk", False)
            )
            db.add(ticket)
            await db.commit()
            await db.refresh(ticket)
            
            return ticket

    async def get_tickets(self) -> List[Dict[str, Any]]:
        """Get all tickets from database."""
        async with AsyncSessionLocal() as db:
            result = await db.execute(select(Ticket).order_by(Ticket.created_at.desc()))
            tickets = result.scalars().all()
            
            return [
                {
                    "id": t.id,
                    "title": t.title,
                    "description": t.description,
                    "priority": t.priority,
                    "status": t.status,
                    "tier": t.tier,
                    "tags": t.tags,
                    "sentiment": t.sentiment,
                    "sentimentScore": t.sentiment_score,
                    "kbMatch": t.kb_match,
                    "slaRisk": t.sla_risk,
                    "created_at": t.created_at,
                    "updated_at": t.updated_at
                }
                for t in tickets
            ]

    async def track_guardrail_activation(self):
        """Track guardrail activation (could be stored in a separate table)."""
        # For now, just pass - could implement a guardrail_events table if needed
        pass

    async def get_summary(self) -> Dict[str, Any]:
        """Get analytics summary from database."""
        async with AsyncSessionLocal() as db:
            # Total conversations
            total_convs_result = await db.execute(select(func.count(Conversation.id)))
            total_convs = total_convs_result.scalar() or 0
            
            # Deflected conversations
            deflected_result = await db.execute(
                select(func.count(Conversation.id)).where(Conversation.deflected == True)
            )
            deflected_convs = deflected_result.scalar() or 0
            
            # Deflection rate
            deflection_rate = (deflected_convs / total_convs) if total_convs > 0 else 0.0
            
            # Total tickets
            tickets_result = await db.execute(select(func.count(Ticket.id)))
            total_tickets = tickets_result.scalar() or 0
            
            # Active users (active in last 15 mins)
            active_threshold = datetime.utcnow() - timedelta(minutes=15)
            active_result = await db.execute(
                select(func.count(Conversation.id))
                .where(Conversation.last_active > active_threshold)
            )
            active_users = active_result.scalar() or 0
            
            # Tier distribution from messages
            tier_result = await db.execute(
                select(Message.tier, func.count(Message.id))
                .where(Message.tier.isnot(None))
                .group_by(Message.tier)
            )
            tier_distribution = {tier: count for tier, count in tier_result.all()}
            
            now = datetime.utcnow()
            uptime = (now - self.start_time).total_seconds()
            
            return {
                "total_conversations": total_convs,
                "deflection_rate": deflection_rate,
                "total_tickets": total_tickets,
                "guardrail_activations": 0,  # Could implement if needed
                "average_response_time": 0.5,  # Could calculate from message timestamps
                "system_uptime": uptime,
                "active_users": active_users,
                "tier_distribution": tier_distribution
            }

    async def get_trends(self) -> Dict[str, Any]:
        """Get trends data from database."""
        async with AsyncSessionLocal() as db:
            # Get conversations grouped by hour
            conv_result = await db.execute(
                select(
                    func.date_trunc('hour', Conversation.start_time).label('hour'),
                    func.count(Conversation.id).label('count')
                )
                .group_by('hour')
                .order_by('hour')
            )
            conversations = [
                {"time": hour.isoformat(), "count": count}
                for hour, count in conv_result.all()
            ]
            
            # Get tickets grouped by hour
            ticket_result = await db.execute(
                select(
                    func.date_trunc('hour', Ticket.created_at).label('hour'),
                    func.count(Ticket.id).label('count')
                )
                .group_by('hour')
                .order_by('hour')
            )
            tickets = [
                {"time": hour.isoformat(), "count": count}
                for hour, count in ticket_result.all()
            ]
            
            return {
                "conversations": conversations,
                "tickets": tickets
            }

# Singleton instance
analytics_tracker = AnalyticsTracker()
