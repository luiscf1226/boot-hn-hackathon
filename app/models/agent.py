"""
Agent and conversation models for storing AI interactions in SQLite.
"""

from sqlalchemy import Column, Integer, String, DateTime, Text, ForeignKey, Boolean
from sqlalchemy.sql import func
from sqlalchemy.orm import Session, relationship
from typing import List, Dict, Any, Optional
import json

from app.core.database import Base


class AgentSession(Base):
    """Model for storing agent conversation sessions."""
    
    __tablename__ = "agent_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    title = Column(String(200), nullable=True)  # Optional session title
    model_used = Column(String(100), nullable=False)  # AI model used
    is_active = Column(Boolean, default=True)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    updated_at = Column(DateTime(timezone=True), onupdate=func.now())
    
    # Relationship to messages
    messages = relationship("AgentMessage", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<AgentSession(id={self.id}, model={self.model_used}, messages={len(self.messages)})>"
    
    @classmethod
    def create_session(cls, db: Session, user_id: int, model: str, title: str = None) -> 'AgentSession':
        """Create a new agent session."""
        session = cls(
            user_id=user_id,
            title=title,
            model_used=model
        )
        db.add(session)
        db.commit()
        db.refresh(session)
        return session
    
    @classmethod
    def get_user_sessions(cls, db: Session, user_id: int, limit: int = 10) -> List['AgentSession']:
        """Get recent sessions for a user."""
        return db.query(cls).filter(
            cls.user_id == user_id
        ).order_by(cls.updated_at.desc()).limit(limit).all()
    
    def add_message(self, db: Session, role: str, content: str, metadata: Dict[str, Any] = None) -> 'AgentMessage':
        """Add a message to this session."""
        message = AgentMessage(
            session_id=self.id,
            role=role,
            content=content,
            message_metadata=json.dumps(metadata) if metadata else None
        )
        db.add(message)
        db.commit()
        db.refresh(message)
        
        # Update session timestamp
        self.updated_at = func.now()
        db.commit()
        
        return message
    
    def get_conversation_history(self) -> List[Dict[str, str]]:
        """Get conversation history in format for AI service."""
        return [
            {
                "role": msg.role,
                "content": msg.content
            }
            for msg in sorted(self.messages, key=lambda x: x.created_at)
        ]
    
    def get_summary(self) -> Dict[str, Any]:
        """Get session summary."""
        return {
            "id": self.id,
            "title": self.title or f"Session {self.id}",
            "model": self.model_used,
            "message_count": len(self.messages),
            "created_at": self.created_at,
            "updated_at": self.updated_at,
            "is_active": self.is_active
        }


class AgentMessage(Base):
    """Model for storing individual messages in agent conversations."""
    
    __tablename__ = "agent_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("agent_sessions.id"), nullable=False)
    role = Column(String(20), nullable=False)  # 'user' or 'assistant'
    content = Column(Text, nullable=False)
    message_metadata = Column(Text, nullable=True)  # JSON string for additional data
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    # Relationship to session
    session = relationship("AgentSession", back_populates="messages")
    
    def __repr__(self):
        preview = self.content[:50] + "..." if len(self.content) > 50 else self.content
        return f"<AgentMessage(role={self.role}, content='{preview}')>"
    
    def get_metadata(self) -> Dict[str, Any]:
        """Get parsed metadata."""
        if self.message_metadata:
            try:
                return json.loads(self.message_metadata)
            except json.JSONDecodeError:
                return {}
        return {}
    
    def to_dict(self) -> Dict[str, Any]:
        """Convert message to dictionary."""
        return {
            "id": self.id,
            "role": self.role,
            "content": self.content,
            "metadata": self.get_metadata(),
            "created_at": self.created_at
        }
