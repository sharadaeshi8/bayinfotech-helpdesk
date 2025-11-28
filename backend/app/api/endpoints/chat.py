from fastapi import APIRouter, HTTPException, Depends
from app.models.schemas import ChatRequest, ChatResponse, Role
from app.services.llm.openai_provider import OpenAIProvider
from app.services.rag.vector_store import get_vector_store
from app.services.rag.retrieval import RAGService
from app.services.guardrails.engine import GuardrailEngine
from app.services.routing.tier_classifier import TierClassifier
from app.services.analytics.tracker import analytics_tracker
from app.core.logging import get_logger

logger = get_logger(__name__)

router = APIRouter()

from app.core.config import settings
from app.services.llm.mock_provider import MockLLMProvider

# Dependency injection (simplified for this demo)
def get_rag_service():
    if not settings.OPENAI_API_KEY:
        logger.warning("using_mock_llm", reason="no_api_key")
        llm = MockLLMProvider()
    else:
        llm = OpenAIProvider()
        
    vector_store = get_vector_store()
    return RAGService(llm, vector_store)

def get_guardrail_engine():
    if not settings.OPENAI_API_KEY:
        llm = MockLLMProvider()
    else:
        llm = OpenAIProvider()
    return GuardrailEngine(llm)

@router.post("/", response_model=ChatResponse)
async def chat(
    request: ChatRequest,
    rag_service: RAGService = Depends(get_rag_service),
    guardrail_engine: GuardrailEngine = Depends(get_guardrail_engine)
):
    logger.info("chat_request_received", session_id=request.session_id, role=request.role)

    # 1. Track conversation start and save user message
    await analytics_tracker.track_conversation_start(request.session_id)
    await analytics_tracker.track_message(
        session_id=request.session_id,
        role="user",
        content=request.message
    )

    # 2. Guardrail Check
    is_safe, refusal_reason = await guardrail_engine.check_safety(request.message, request.role)
    if not is_safe:
        logger.warning("guardrail_blocked", session_id=request.session_id, reason=refusal_reason)
        await analytics_tracker.track_guardrail_activation()
        # Trigger 4: Guardrail Violation (Security)
        # If refusal reason indicates security issue, escalate
        action = "none"
        if "security" in refusal_reason.lower() or "injection" in refusal_reason.lower() or "jailbreak" in refusal_reason.lower():
             action = "escalation"
        
        # Save assistant response
        await analytics_tracker.track_message(
            session_id=request.session_id,
            role="assistant",
            content=refusal_reason,
            confidence_score=0.0
        )
        
        return ChatResponse(
            response=refusal_reason,
            session_id=request.session_id,
            sources=[],
            confidence_score=0.0,
            action=action
        )

    # 3. Tier/Severity Classification (for context, not blocking chat)
    tier, severity = TierClassifier.classify_tier_and_severity(request.message, request.role)
    logger.info("tier_classification", session_id=request.session_id, tier=tier, severity=severity)
    await analytics_tracker.track_tier(tier)
    
    # 3.5 Intent Detection for Ticket Creation & Escalation
    # Check if "ticket" is present AND one of the action verbs
    msg_lower = request.message.lower()
    ticket_verbs = ["create", "raise", "open", "file", "generate", "make", "submit"]
    
    # Check for direct phrases like "want a ticket", "need a ticket"
    direct_phrases = ["want a ticket", "need a ticket", "create a ticket", "raise a ticket", "open a ticket", "report an issue", "report a problem", "report a bug"]
    
    is_ticket_intent = (
        "ticket" in msg_lower and 
        any(verb in msg_lower for verb in ticket_verbs)
    ) or any(phrase in msg_lower for phrase in direct_phrases)
    
    # Escalation Triggers
    escalation_keywords = ["human", "agent", "supervisor", "representative", "live support"]
    is_escalation_intent = any(kw in msg_lower for kw in escalation_keywords)

    # Trigger 1: Critical Severity
    from app.models.schemas import TicketPriority
    if severity == TicketPriority.CRITICAL:
        is_escalation_intent = True
        logger.info("critical_severity_escalation_trigger", session_id=request.session_id)
    
    action = "none"
    
    if is_escalation_intent:
        action = "escalation"
        logger.info("escalation_triggered", session_id=request.session_id, reason="explicit_or_critical")
        
        response_text = "I understand this is urgent. I am connecting you with a live agent immediately."
        
        # Save assistant response
        await analytics_tracker.track_message(
            session_id=request.session_id,
            role="assistant",
            content=response_text,
            confidence_score=1.0,
            tier=tier,
            sentiment="neutral"
        )
        
        return ChatResponse(
            response=response_text,
            session_id=request.session_id,
            sources=[],
            confidence_score=1.0,
            sentiment="neutral",
            tier=tier,
            severity=severity,
            action=action
        )

    if is_ticket_intent:
        action = "ticket_details_request"
        logger.info("ticket_intent_detected", session_id=request.session_id)
        
        # Customize response based on trigger
        response_text = "I can certainly help you with that. Could you please provide the details for the ticket, specifically the Subject and a brief Description?"
        
        # Save assistant response
        await analytics_tracker.track_message(
            session_id=request.session_id,
            role="assistant",
            content=response_text,
            confidence_score=1.0,
            tier=tier,
            sentiment="neutral"
        )
        
        return ChatResponse(
            response=response_text,
            session_id=request.session_id,
            sources=[],
            confidence_score=1.0,
            sentiment="neutral",
            tier=tier,
            severity=severity,
            action=action
        )
    
    # 4. RAG Generation
    try:
        # Use conversation history from frontend if provided, otherwise load from database
        history = []
        
        if request.history:
            # Frontend provided history - use it directly
            history = [{"role": msg.role, "content": msg.content} for msg in request.history]
        else:
            # Load from database as fallback
            from app.core.database import AsyncSessionLocal
            from app.models.models import Conversation, Message
            from sqlalchemy import select
            
            async with AsyncSessionLocal() as db:
                # Get conversation
                conv_result = await db.execute(
                    select(Conversation).where(Conversation.session_id == request.session_id)
                )
                conversation = conv_result.scalar_one_or_none()
                
                if conversation:
                    # Get last 10 messages for context
                    msg_result = await db.execute(
                        select(Message)
                        .where(Message.conversation_id == conversation.id)
                        .order_by(Message.created_at.desc())
                        .limit(10)
                    )
                    messages = msg_result.scalars().all()
                    
                    # Reverse to chronological order and format for LLM
                    for msg in reversed(messages):
                        history.append({
                            "role": msg.role,
                            "content": msg.content
                        })
        
        # Generate response with conversation history
        result = await rag_service.generate_response(request.message, history=history)
        
        # Calculate confidence score
        # Formula: 0.4 * retrieval + 0.3 * coverage + 0.2 * llm_certainty + 0.1 * recency
        
        components = result.get("components", {})
        retrieval_score = components.get("retrieval_score", 0.0)
        coverage_score = components.get("coverage_score", 0.0)
        recency_score = components.get("recency_score", 0.0)
        llm_certainty = 0.8 # Heuristic default for now
        
        confidence_score = (0.4 * retrieval_score) + (0.3 * coverage_score) + (0.2 * llm_certainty) + (0.1 * recency_score)
        
        # Cap at 0.99
        confidence_score = min(confidence_score, 0.99)
        
        logger.info("response_generated", 
                    session_id=request.session_id, 
                    confidence_score=confidence_score,
                    components=components)

        # Trigger 2: KB No Solution (3 attempts)
        if confidence_score < 0.6:
            await analytics_tracker.track_low_confidence(request.session_id)
            streak = await analytics_tracker.get_low_confidence_streak(request.session_id)
            if streak >= 3:
                logger.info("low_confidence_escalation_trigger", session_id=request.session_id, streak=streak)
                response_text = "I apologize, but I'm having trouble finding the right solution for you. Let me connect you with a human agent who can assist you better."
                
                # Save assistant response
                await analytics_tracker.track_message(
                    session_id=request.session_id,
                    role="assistant",
                    content=response_text,
                    confidence_score=confidence_score,
                    tier=tier,
                    sentiment="neutral"
                )
                
                return ChatResponse(
                    response=response_text,
                    session_id=request.session_id,
                    sources=[],
                    confidence_score=confidence_score,
                    sentiment="neutral",
                    tier=tier,
                    severity=severity,
                    action="escalation"
                )
        else:
            await analytics_tracker.reset_low_confidence(request.session_id)

        # Save successful assistant response
        await analytics_tracker.track_message(
            session_id=request.session_id,
            role="assistant",
            content=result["answer"],
            confidence_score=confidence_score,
            tier=tier,
            sentiment="neutral"
        )

        return ChatResponse(
            response=result["answer"],
            session_id=request.session_id,
            sources=result["sources"],
            confidence_score=confidence_score,
            sentiment="neutral", # Mock sentiment
            tier=tier,
            severity=severity
        )
    except Exception as e:
        logger.error("rag_error", session_id=request.session_id, error=str(e))
        # Fallback to Mock Provider if primary fails (e.g. Rate Limit, Auth Error)
        from app.services.llm.mock_provider import MockLLMProvider
        mock_llm = MockLLMProvider()
        fallback_response = await mock_llm.generate_answer(request.message, "", [])
        
        response_text = f"[System Notification: Primary AI Service Unavailable - Switched to Offline Backup]\n\n{fallback_response}"
        
        # Save fallback response
        await analytics_tracker.track_message(
            session_id=request.session_id,
            role="assistant",
            content=response_text,
            confidence_score=0.0,
            tier=tier,
            sentiment="neutral"
        )
        
        return ChatResponse(
            response=response_text,
            session_id=request.session_id,
            sources=[],
            confidence_score=0.0,
            sentiment="neutral",
            tier=tier,
            severity=severity
        )
