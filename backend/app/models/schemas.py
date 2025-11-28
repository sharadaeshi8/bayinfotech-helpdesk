from typing import List, Optional, Dict, Any
from pydantic import BaseModel, Field, validator
from datetime import datetime
from enum import Enum

class Role(str, Enum):
    USER = "user"
    SUPPORT = "support"
    ADMIN = "admin"

class MessageRole(str, Enum):
    USER = "user"
    ASSISTANT = "assistant"
    SYSTEM = "system"

class ChatMessage(BaseModel):
    role: str
    content: str

class ChatRequest(BaseModel):
    message: str
    session_id: str
    role: Role = Role.USER
    history: List[ChatMessage] = []  # Optional conversation history from frontend

class TicketPriority(str, Enum):
    LOW = "low"
    MEDIUM = "medium"
    HIGH = "high"
    CRITICAL = "critical"

class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

class ChatResponse(BaseModel):
    response: str
    session_id: str
    sources: List[Dict[str, Any]] = []
    confidence_score: float = 0.0
    sentiment: Optional[str] = None
    tier: Optional[str] = None
    severity: Optional[TicketPriority] = None
    action: Optional[str] = None # Enum: "ticket_details_request", "none"

class TicketTag(BaseModel):
    label: str
    confidence: float

class TicketCreate(BaseModel):
    id: Optional[str] = None # Allow frontend to generate ID
    title: Optional[str] = None  # Optional to support 'subject' mapping
    subject: Optional[str] = None  # Frontend compatibility
    description: str
    priority: str
    status: str = "Open"
    tier: Optional[str] = "Tier 0"
    tags: List[TicketTag] = []
    sentiment: Optional[str] = "Neutral"
    sentimentScore: float = 0.0  # Default value
    kbMatch: Optional[str] = None
    slaRisk: bool = False
    session_id: Optional[str] = None
    created: Optional[datetime] = None  # Frontend sends this, we'll ignore it
    
    @validator('title', always=True)
    def set_title_from_subject(cls, v, values):
        """Use subject as title if title is not provided."""
        if v is None and 'subject' in values:
            return values['subject']
        return v or values.get('subject', 'Untitled')

class TicketResponse(TicketCreate):
    id: str
    created_at: datetime
    updated_at: datetime = Field(default_factory=datetime.utcnow)

class MetricsResponse(BaseModel):
    total_conversations: int
    deflection_rate: float
    average_response_time: float
    top_issues: List[Dict[str, Any]]
