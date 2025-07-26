"""
Agent class that combines AI service with conversation management and storage.
"""

from typing import List, Dict, Any, Optional
from sqlalchemy.orm import Session

from app.services.ai_service import AIService
from app.models.agent import AgentSession, AgentMessage
from app.models.user import User


class Agent:
    """
    High-level agent class that manages AI conversations with persistence.
    Combines AIService with conversation storage and management.
    """

    def __init__(self, db_session: Session):
        self.db = db_session
        self.ai_service = AIService(db_session)
        self.current_session: Optional[AgentSession] = None

    def start_new_session(self, title: str = None) -> AgentSession:
        """Start a new conversation session."""
        user = User.get_or_create_default_user(self.db)
        model = self.ai_service.get_current_model()

        self.current_session = AgentSession.create_session(
            db=self.db, user_id=user.id, model=model, title=title
        )
        return self.current_session

    def load_session(self, session_id: int) -> Optional[AgentSession]:
        """Load an existing conversation session."""
        session = (
            self.db.query(AgentSession).filter(AgentSession.id == session_id).first()
        )
        if session:
            self.current_session = session
        return session

    def get_user_sessions(self, limit: int = 10) -> List[AgentSession]:
        """Get recent sessions for the current user."""
        user = User.get_or_create_default_user(self.db)
        return AgentSession.get_user_sessions(self.db, user.id, limit)

    async def send_message(
        self, message: str, save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Send a message to the AI and optionally save the conversation.

        Args:
            message: User message to send
            save_to_db: Whether to save the conversation to database

        Returns:
            Dict with AI response and metadata
        """
        try:
            # Create session if none exists and we're saving to DB
            if save_to_db and not self.current_session:
                self.start_new_session()

            # Get conversation history if we have an active session
            conversation_history = []
            if self.current_session:
                conversation_history = self.current_session.get_conversation_history()

            # Send message to AI
            ai_response = await self.ai_service.send_message(
                message, conversation_history
            )

            if not ai_response["success"]:
                return {
                    "success": False,
                    "error": ai_response["error"],
                    "session_id": self.current_session.id
                    if self.current_session
                    else None,
                }

            # Save to database if requested and session exists
            if save_to_db and self.current_session:
                # Save user message
                user_msg = self.current_session.add_message(
                    db=self.db, role="user", content=message
                )

                # Save AI response
                ai_msg = self.current_session.add_message(
                    db=self.db,
                    role="assistant",
                    content=ai_response["response"],
                    metadata={
                        "model": ai_response["model"],
                        "usage": ai_response.get("usage", {}),
                    },
                )

            return {
                "success": True,
                "response": ai_response["response"],
                "model": ai_response["model"],
                "usage": ai_response.get("usage", {}),
                "session_id": self.current_session.id if self.current_session else None,
                "message_id": ai_msg.id
                if save_to_db and self.current_session
                else None,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "session_id": self.current_session.id if self.current_session else None,
            }

    async def send_system_message(
        self, system_prompt: str, user_message: str, save_to_db: bool = True
    ) -> Dict[str, Any]:
        """
        Send a message with system instructions.

        Args:
            system_prompt: System instructions
            user_message: User message
            save_to_db: Whether to save the conversation to database

        Returns:
            Dict with AI response and metadata
        """
        try:
            # Create session if none exists and we're saving to DB
            if save_to_db and not self.current_session:
                self.start_new_session(title="System Chat")

            # Send system message to AI
            ai_response = await self.ai_service.send_system_message(
                system_prompt, user_message
            )

            if not ai_response["success"]:
                return {
                    "success": False,
                    "error": ai_response["error"],
                    "session_id": self.current_session.id
                    if self.current_session
                    else None,
                }

            # Save to database if requested and session exists
            if save_to_db and self.current_session:
                # Save combined message (system + user)
                combined_message = f"System: {system_prompt}\n\nUser: {user_message}"
                user_msg = self.current_session.add_message(
                    db=self.db,
                    role="user",
                    content=combined_message,
                    metadata={"type": "system_message", "system_prompt": system_prompt},
                )

                # Save AI response
                ai_msg = self.current_session.add_message(
                    db=self.db,
                    role="assistant",
                    content=ai_response["response"],
                    metadata={
                        "model": ai_response["model"],
                        "usage": ai_response.get("usage", {}),
                        "type": "system_response",
                    },
                )

            return {
                "success": True,
                "response": ai_response["response"],
                "model": ai_response["model"],
                "usage": ai_response.get("usage", {}),
                "session_id": self.current_session.id if self.current_session else None,
                "message_id": ai_msg.id
                if save_to_db and self.current_session
                else None,
            }

        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "session_id": self.current_session.id if self.current_session else None,
            }

    def get_session_messages(self, session_id: int = None) -> List[Dict[str, Any]]:
        """Get messages from a session (current session if no ID provided)."""
        session = None
        if session_id:
            session = (
                self.db.query(AgentSession)
                .filter(AgentSession.id == session_id)
                .first()
            )
        else:
            session = self.current_session

        if not session:
            return []

        return [
            msg.to_dict()
            for msg in sorted(session.messages, key=lambda x: x.created_at)
        ]

    def delete_session(self, session_id: int) -> bool:
        """Delete a conversation session and all its messages."""
        try:
            session = (
                self.db.query(AgentSession)
                .filter(AgentSession.id == session_id)
                .first()
            )
            if session:
                self.db.delete(session)
                self.db.commit()

                # Clear current session if it was deleted
                if self.current_session and self.current_session.id == session_id:
                    self.current_session = None

                return True
            return False
        except Exception:
            self.db.rollback()
            return False

    def refresh_ai_config(self) -> None:
        """Refresh AI service configuration (useful after model changes)."""
        self.ai_service.refresh_config()
