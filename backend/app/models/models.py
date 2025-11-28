from sqlalchemy import Column, String, Text, DateTime, Index, Boolean, Float, ForeignKey, Integer
from sqlalchemy.dialects.postgresql import UUID, JSONB
from sqlalchemy.orm import relationship
from pgvector.sqlalchemy import Vector
from datetime import datetime
import uuid
from app.core.database import Base

class Document(Base):
    """Document model for storing text chunks with embeddings."""
    
    __tablename__ = "documents"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    content = Column(Text, nullable=False)
    embedding = Column(Vector(1536), nullable=False)  # OpenAI text-embedding-3-small dimension
    doc_metadata = Column(JSONB, default={})  # Renamed from 'metadata' to avoid SQLAlchemy conflict
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    __table_args__ = (
        Index(
            'idx_embedding_cosine',
            embedding,
            postgresql_using='ivfflat',
            postgresql_with={'lists': 100},
            postgresql_ops={'embedding': 'vector_cosine_ops'}
        ),
    )
    
    def __repr__(self):
        return f"<Document(id={self.id}, content={self.content[:50]}...)>"

class Conversation(Base):
    """Conversation model for tracking chat sessions."""
    
    __tablename__ = "conversations"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    session_id = Column(String, unique=True, nullable=False, index=True)
    start_time = Column(DateTime, default=datetime.utcnow, nullable=False)
    last_active = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    message_count = Column(Integer, default=0)
    deflected = Column(Boolean, default=True)
    consecutive_low_confidence = Column(Integer, default=0)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    messages = relationship("Message", back_populates="conversation", cascade="all, delete-orphan")
    ticket = relationship("Ticket", back_populates="conversation", uselist=False)
    
    def __repr__(self):
        return f"<Conversation(session_id={self.session_id}, messages={self.message_count})>"

class Message(Base):
    """Message model for storing individual chat messages."""
    
    __tablename__ = "messages"
    
    id = Column(UUID(as_uuid=True), primary_key=True, default=uuid.uuid4)
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=False)
    role = Column(String, nullable=False)  # 'user', 'assistant', 'system'
    content = Column(Text, nullable=False)
    confidence_score = Column(Float, default=0.0)
    tier = Column(String)
    sentiment = Column(String)
    created_at = Column(DateTime, default=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="messages")
    
    def __repr__(self):
        return f"<Message(role={self.role}, content={self.content[:30]}...)>"

class Ticket(Base):
    """Ticket model for storing support tickets."""
    
    __tablename__ = "tickets"
    
    id = Column(String, primary_key=True)  # Format: INC-xxxxxxxx
    conversation_id = Column(UUID(as_uuid=True), ForeignKey("conversations.id"), nullable=True)
    title = Column(String, nullable=False)
    description = Column(Text, nullable=False)
    priority = Column(String, nullable=False)
    status = Column(String, default="Open")
    tier = Column(String, default="Tier 0")
    tags = Column(JSONB, default=[])
    sentiment = Column(String, default="Neutral")
    sentiment_score = Column(Float, default=0.0)
    kb_match = Column(String)
    sla_risk = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
    
    # Relationships
    conversation = relationship("Conversation", back_populates="ticket")
    
    __table_args__ = (
        Index('idx_ticket_status', status),
        Index('idx_ticket_priority', priority),
        Index('idx_ticket_created_at', created_at),
    )
    
    def __repr__(self):
        return f"<Ticket(id={self.id}, title={self.title}, status={self.status})>"
