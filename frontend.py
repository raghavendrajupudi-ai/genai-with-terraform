"""
Frontend module for AI Chatbot
Handles Streamlit UI and user interactions
"""

import streamlit as st
from typing import Tuple, Dict, Any


class ChatbotUI:
    """
    Frontend class for managing the chatbot user interface
    """
    
    @staticmethod
    def configure_page() -> None:
        """Configure Streamlit page settings"""
        st.set_page_config(
            page_title="AI Chatbot",
            page_icon="🤖",
            layout="wide",
            initial_sidebar_state="expanded"
        )
    
    @staticmethod
    def apply_styles() -> None:
        """Apply custom CSS styling to the application"""
        st.markdown("""
            <style>
                /* Navigation bar styling */
                header {
                    background-color: #001f3f !important;
                }
                header * {
                    color: white !important;
                }
                
                /* Title styling - Navy Blue */
                h1 {
                    color: #001f3f !important;
                }
                
                /* EGEN card styling */
                .egen-card {
                    font-family: Calibri, sans-serif;
                    font-size: 28px;
                    font-weight: bold;
                    color: #001f3f;
                    margin-bottom: 10px;
                    letter-spacing: 2px;
                }
                
                /* Title and header text styling */
                .main > div:first-child h1 {
                    color: #001f3f !important;
                }
                .main > div:first-child p {
                    color: white !important;
                }
                
                /* Chat message styling */
                .chat-message {
                    padding: 1.5rem;
                    border-radius: 0.5rem;
                    margin-bottom: 1rem;
                    display: flex;
                    gap: 1rem;
                }
                .chat-message.user {
                    background-color: #e3f2fd;
                    justify-content: flex-end;
                }
                .chat-message.assistant {
                    background-color: #f5f5f5;
                }
                .chat-message.error {
                    background-color: #ffebee;
                    color: #c62828;
                }
                .message-content {
                    max-width: 70%;
                }
                .user .message-content {
                    background-color: #1976d2;
                    color: white;
                    padding: 1rem;
                    border-radius: 1rem;
                }
                .assistant .message-content {
                    background-color: white;
                    padding: 1rem;
                    border-radius: 1rem;
                    border: 1px solid #e0e0e0;
                }
            </style>
        """, unsafe_allow_html=True)
    
    @staticmethod
    def render_sidebar() -> Tuple[str, str, float, int, bool]:
        """
        Render sidebar configuration panel
        
        Returns:
            Tuple containing (api_key, model_name, temperature, max_tokens, clear_clicked)
        """
        import os
        
        st.sidebar.title("⚙️ Settings")
        
        # Get API key from environment only (no user input field)
        api_key = os.getenv("GOOGLE_API_KEY", "")
        
        # Model selection
        model_name = st.sidebar.selectbox(
            "Select Model",
            ["gemini-2.0-flash"],
            help="Choose the Gemini model to use"
        )
        
        # Temperature slider
        temperature = st.sidebar.slider(
            "Temperature",
            min_value=0.0,
            max_value=2.0,
            value=0.7,
            step=0.1,
            help="Higher values make output more creative, lower values more deterministic"
        )
        
        # Max tokens slider
        max_tokens = st.sidebar.slider(
            "Max Tokens",
            min_value=50,
            max_value=2000,
            value=500,
            step=50,
            help="Maximum length of generated response"
        )
        
        # Clear conversation button
        clear_clicked = st.sidebar.button("🗑️ Clear Conversation", key="clear_conversation")
        
        # # Display info
        # st.sidebar.markdown("---")
        # st.sidebar.info(
        #     "🤖 **AI Chatbot with RAG**\n\n"
        #     "This is a generative AI chatbot powered by LangChain and Google Gemini. "
        #     "The conversation history is maintained during the session.\n\n"
        #     "📁 **RAG Integration**: The chatbot uses Retrieval-Augmented Generation "
        #     "to answer questions about your Terraform infrastructure files. "
        #     "It retrieves relevant context from the terraform_files folder to provide "
        #     "accurate and context-aware responses."
        # )
        
        return api_key, model_name, temperature, max_tokens, clear_clicked
    
    @staticmethod
    def render_header() -> None:
        """Render the main header of the application with EGEN branding"""
        # Display EGEN card above title
        st.markdown('<div class="egen-card">EGEN</div>', unsafe_allow_html=True)
        
        # Display main title
        st.title("🤖 Terraform AI Chatbot with RAG")
    
    @staticmethod
    def render_chat_history(messages: list) -> None:
        """
        Render chat message history
        
        Args:
            messages: List of message dictionaries with 'role' and 'content' keys
        """
        for message in messages:
            if message["role"] == "user":
                st.markdown(
                    f'<div class="chat-message user"><div class="message-content">{message["content"]}</div></div>',
                    unsafe_allow_html=True
                )
            else:
                st.markdown(
                    f'<div class="chat-message assistant"><div class="message-content">{message["content"]}</div></div>',
                    unsafe_allow_html=True
                )
    
    @staticmethod
    def render_input_area() -> Tuple[str, bool]:
        """
        Render the user input area
        
        Returns:
            Tuple containing (user_input, submit_button_clicked)
        """
        col1, col2 = st.columns([5, 1])
        
        with col1:
            user_input = st.text_input(
                "Type your message:",
                placeholder="Ask me anything...",
                label_visibility="collapsed"
            )
        
        with col2:
            submit_button = st.button("Send", use_container_width=True)
        
        return user_input, submit_button
    
    @staticmethod
    def show_error(message: str) -> None:
        """
        Display an error message
        
        Args:
            message: Error message to display
        """
        st.error(f"❌ {message}")
    
    @staticmethod
    def show_success(message: str) -> None:
        """
        Display a success message
        
        Args:
            message: Success message to display
        """
        st.success(f"✅ {message}")
    
    @staticmethod
    def show_info(message: str) -> None:
        """
        Display an info message
        
        Args:
            message: Info message to display
        """
        st.info(f"ℹ️ {message}")
    
    #@staticmethod
    # def render_footer() -> None:
    #     """Render the footer of the application"""
    #     st.markdown("---")
    #     st.markdown(
    #         """
    #         <div style='text-align: center; color: gray; font-size: 12px;'>
    #             Powered by <b>LangChain</b> • <b>Google Gemini</b> • <b>Streamlit</b> • <b>RAG</b><br>
    #             © 2024 AI Chatbot with Terraform RAG. All rights reserved.
    #         </div>
    #         """,
    #         unsafe_allow_html=True
    #     )
    
    @staticmethod
    def initialize_session_state() -> None:
        """Initialize session state variables if not already present"""
        if "messages" not in st.session_state:
            st.session_state.messages = []
        
        if "backend" not in st.session_state:
            from backend import AIBackend
            st.session_state.backend = AIBackend()
    
    @staticmethod
    def get_session_state() -> Dict[str, Any]:
        """
        Get the current session state
        
        Returns:
            Dictionary containing session state variables
        """
        return {
            "messages": st.session_state.get("messages", []),
            "backend": st.session_state.get("backend"),
        }
    
    @staticmethod
    def update_session_messages(messages: list) -> None:
        """
        Update session messages
        
        Args:
            messages: New messages list
        """
        st.session_state.messages = messages
