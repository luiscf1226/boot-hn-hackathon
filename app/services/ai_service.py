"""
Consolidated AI service for all AI API calls using Gemini.
Handles API key management, model selection, and message formatting.
"""

import google.generativeai as genai
from typing import List, Dict, Any
from sqlalchemy.orm import Session

from app.models.user import User
from app.core.config import settings


class AIService:
    """Consolidated service for all AI interactions."""
    
    def __init__(self, db_session: Session):
        self.db = db_session
        self._client = None
        self._current_model = None
        
    def _get_user_config(self) -> tuple[str, str]:
        """Get user's API key and selected model."""
        user = User.get_or_create_default_user(self.db)
        
        api_key = user.gemini_api_key or settings.gemini_api_key
        if not api_key or api_key == "your_gemini_api_key_here":
            raise ValueError("No valid API key found. Please run /setup first.")
            
        model = user.selected_model or "gemini-2.0-flash-exp"
        return api_key, model
    
    def _initialize_client(self) -> None:
        """Initialize the Gemini client with user configuration."""
        api_key, model = self._get_user_config()
        
        # Configure the API key
        genai.configure(api_key=api_key)
        
        # Initialize the model
        self._client = genai.GenerativeModel(model)
        self._current_model = model
    
    async def send_message(self, message: str, conversation_history: List[Dict[str, str]] = None) -> Dict[str, Any]:
        """
        Send a message to the AI and get response.
        
        Args:
            message: User message to send
            conversation_history: Previous messages in format [{"role": "user/assistant", "content": "..."}]
            
        Returns:
            Dict with response data
        """
        try:
            if not self._client:
                self._initialize_client()
            
            # Format conversation history for Gemini
            chat_history = []
            if conversation_history:
                for msg in conversation_history:
                    role = "user" if msg["role"] == "user" else "model"
                    chat_history.append({"role": role, "parts": [msg["content"]]})
            
            # Start chat with history
            chat = self._client.start_chat(history=chat_history)
            
            # Send message and get response
            response = chat.send_message(message)
            
            return {
                "success": True,
                "response": response.text,
                "model": self._current_model,
                "usage": {
                    "prompt_tokens": getattr(response.usage_metadata, 'prompt_token_count', 0) if hasattr(response, 'usage_metadata') else 0,
                    "completion_tokens": getattr(response.usage_metadata, 'candidates_token_count', 0) if hasattr(response, 'usage_metadata') else 0,
                }
            }
            
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "model": self._current_model
            }
    
    async def send_system_message(self, system_prompt: str, user_message: str) -> Dict[str, Any]:
        """
        Send a message with system instructions.
        
        Args:
            system_prompt: System instructions
            user_message: User message
            
        Returns:
            Dict with response data
        """
        # Combine system prompt with user message
        combined_message = f"System: {system_prompt}\n\nUser: {user_message}"
        return await self.send_message(combined_message)
    
    def get_current_model(self) -> str:
        """Get the currently selected model."""
        try:
            _, model = self._get_user_config()
            return model
        except Exception:
            return "gemini-2.0-flash-exp"
    
    def refresh_config(self) -> None:
        """Refresh the client configuration (useful after model changes)."""
        self._client = None
        self._current_model = None
