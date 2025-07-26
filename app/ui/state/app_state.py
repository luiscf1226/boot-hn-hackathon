"""
Application state management for the Textual UI.
"""

from dataclasses import dataclass
from typing import Optional, Any


@dataclass
class AppState:
    """Manages application state for the welcome screen."""
    
    # Setup state
    setup_step: Optional[str] = None
    setup_waiting_for_api_key: bool = False
    
    # Models state
    models: list[str] = None
    current_command: Optional[str] = None
    
    # Init state
    init_waiting_for_path: bool = False
    
    # Clean state
    clean_waiting_for_action: bool = False
    pending_clean_action: Optional[str] = None
    
    # Commit state
    commit_waiting_for_confirmation: bool = False
    pending_commit_message: Optional[str] = None
    
    # Review state
    review_waiting_for_confirmation: bool = False
    pending_review_data: Optional[dict] = None
    
    # Explain state
    explain_waiting_for_input: bool = False
    explain_input_type: Optional[str] = None
    
    def __post_init__(self):
        """Initialize mutable defaults."""
        if self.models is None:
            self.models = []
    
    def reset(self):
        """Reset all state to initial values."""
        self.setup_step = None
        self.setup_waiting_for_api_key = False
        self.models = []
        self.current_command = None
        self.init_waiting_for_path = False
        self.clean_waiting_for_action = False
        self.pending_clean_action = None
        self.commit_waiting_for_confirmation = False
        self.pending_commit_message = None
        self.review_waiting_for_confirmation = False
        self.pending_review_data = None
        self.explain_waiting_for_input = False
        self.explain_input_type = None
    
    def is_waiting_for_input(self) -> bool:
        """Check if app is waiting for user input."""
        return (
            self.setup_waiting_for_api_key or
            self.setup_step == "model_selection" or
            self.init_waiting_for_path or
            self.clean_waiting_for_action or
            self.commit_waiting_for_confirmation or
            self.review_waiting_for_confirmation or
            self.explain_waiting_for_input
        )
    
    def get_placeholder_text(self) -> str:
        """Get appropriate placeholder text based on current state."""
        if self.setup_waiting_for_api_key:
            return "Paste your Gemini API key here..."
        elif self.setup_step == "model_selection":
            return "Enter number (1-4)"
        elif self.init_waiting_for_path:
            return "Enter project path"
        elif self.clean_waiting_for_action:
            if self.pending_clean_action:
                return "Type 'yes' to confirm deletion"
            return "Enter action (1-3 or clean/stats/vacuum)"
        elif self.commit_waiting_for_confirmation:
            return "yes/no/edit"
        elif self.review_waiting_for_confirmation:
            return "yes/no"
        elif self.explain_waiting_for_input:
            if self.explain_input_type == "option":
                return "Enter 1-3, paste, file <path>, or current"
            elif self.explain_input_type == "code_paste":
                return "Paste your code here..."
            elif self.explain_input_type == "file_path":
                return "Enter file path..."
        
        return "Type /setup, /models, /init, /clean, /commit, /review-changes, /explain, or /clear"