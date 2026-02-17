"""
Utility functions for AI Chatbot
Contains helper functions for validation, formatting, and common operations
"""

import os
from typing import Optional, Tuple
import re


class EnvironmentManager:
    """Class for managing environment variables"""
    
    @staticmethod
    def load_api_key() -> Optional[str]:
        """
        Load Google API key from environment
        
        Returns:
            API key string if found, None otherwise
        """
        # Try to load from environment variable
        api_key = os.getenv("GOOGLE_API_KEY")
        return api_key if api_key and api_key.strip() else None
    
    @staticmethod
    def get_api_key(fallback: str = "") -> str:
        """
        Get API key from environment with fallback
        
        Args:
            fallback: Fallback value if API key not found
            
        Returns:
            API key string or fallback value
        """
        return EnvironmentManager.load_api_key() or fallback
    
    @staticmethod
    def set_api_key(api_key: str) -> None:
        """
        Set API key in environment
        
        Args:
            api_key: The API key to set
        """
        if api_key:
            os.environ["GOOGLE_API_KEY"] = api_key


class InputValidator:
    """Class for validating user inputs"""
    
    @staticmethod
    def validate_api_key(api_key: str) -> Tuple[bool, Optional[str]]:
        """
        Validate the API key format
        
        Args:
            api_key: The API key to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not api_key:
            return False, "API key is required"
        
        if len(api_key.strip()) < 10:
            return False, "API key appears to be invalid (too short)"
        
        return True, None
    
    @staticmethod
    def validate_user_input(user_input: str) -> Tuple[bool, Optional[str]]:
        """
        Validate user input message
        
        Args:
            user_input: The user input to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if not user_input:
            return False, "Please enter a message"
        
        if len(user_input.strip()) == 0:
            return False, "Message cannot be empty"
        
        if len(user_input) > 5000:
            return False, "Message is too long (max 5000 characters)"
        
        return True, None
    
    @staticmethod
    def validate_temperature(temperature: float) -> Tuple[bool, Optional[str]]:
        """
        Validate temperature parameter
        
        Args:
            temperature: The temperature value to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if temperature < 0.0 or temperature > 2.0:
            return False, "Temperature must be between 0.0 and 2.0"
        
        return True, None
    
    @staticmethod
    def validate_max_tokens(max_tokens: int) -> Tuple[bool, Optional[str]]:
        """
        Validate max tokens parameter
        
        Args:
            max_tokens: The max tokens value to validate
            
        Returns:
            Tuple of (is_valid, error_message)
        """
        if max_tokens < 50 or max_tokens > 2000:
            return False, "Max tokens must be between 50 and 2000"
        
        return True, None


class MessageFormatter:
    """Class for formatting messages"""
    
    @staticmethod
    def format_message_for_display(message: str, max_length: Optional[int] = None) -> str:
        """
        Format message for display in the UI
        
        Args:
            message: The message to format
            max_length: Optional maximum length for truncation
            
        Returns:
            Formatted message string
        """
        # Remove extra whitespace
        formatted = message.strip()
        
        # Truncate if necessary
        if max_length and len(formatted) > max_length:
            formatted = formatted[:max_length] + "..."
        
        return formatted
    
    @staticmethod
    def escape_html(text: str) -> str:
        """
        Escape HTML characters in text
        
        Args:
            text: The text to escape
            
        Returns:
            Escaped text
        """
        replacements = {
            "&": "&amp;",
            "<": "&lt;",
            ">": "&gt;",
            '"': "&quot;",
            "'": "&#39;"
        }
        
        result = text
        for char, replacement in replacements.items():
            result = result.replace(char, replacement)
        
        return result


class SessionManager:
    """Class for managing session state"""
    
    @staticmethod
    def initialize_messages(session_state) -> list:
        """
        Initialize messages in session state
        
        Args:
            session_state: Streamlit session state
            
        Returns:
            List of messages
        """
        if "messages" not in session_state:
            session_state.messages = []
        return session_state.messages
    
    @staticmethod
    def add_message(session_state, role: str, content: str) -> None:
        """
        Add a message to session state
        
        Args:
            session_state: Streamlit session state
            role: Role of the message sender ('user' or 'assistant')
            content: Message content
        """
        if "messages" not in session_state:
            session_state.messages = []
        
        session_state.messages.append({
            "role": role,
            "content": content
        })
    
    @staticmethod
    def get_messages(session_state) -> list:
        """
        Get all messages from session state
        
        Args:
            session_state: Streamlit session state
            
        Returns:
            List of messages
        """
        return session_state.get("messages", [])
    
    @staticmethod
    def clear_messages(session_state) -> None:
        """
        Clear all messages from session state
        
        Args:
            session_state: Streamlit session state
        """
        session_state.messages = []


class APIKeyManager:
    """Class for managing API keys securely"""
    
    @staticmethod
    def mask_api_key(api_key: str) -> str:
        """
        Mask the API key for display purposes
        
        Args:
            api_key: The API key to mask
            
        Returns:
            Masked API key
        """
        if len(api_key) < 8:
            return "****"
        
        return f"{api_key[:4]}...{api_key[-4:]}"
    
    @staticmethod
    def extract_key_domain(api_key: str) -> Optional[str]:
        """
        Extract the domain/service from an API key if possible
        
        Args:
            api_key: The API key
            
        Returns:
            Domain if identifiable, None otherwise
        """
        # Google API keys typically start with 'AIza'
        if api_key.startswith("AIza"):
            return "Google"
        
        return None
