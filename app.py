"""
Main application file for AI Chatbot
Combines frontend and backend modules for a complete chatbot experience
"""

import os
import streamlit as st
from dotenv import load_dotenv
from frontend import ChatbotUI
from backend import AIBackend

# Load environment variables from .env file
load_dotenv()

# Configure the page
ChatbotUI.configure_page()

# Apply custom CSS styles
ChatbotUI.apply_styles()

# Render sidebar and get configuration
api_key, model_name, temperature, max_tokens, clear_clicked = ChatbotUI.render_sidebar()

# If API key is not provided in sidebar, try to load from environment
if not api_key:
    api_key = os.getenv("GOOGLE_API_KEY", "")

# Render main header
ChatbotUI.render_header()

# Initialize session state
ChatbotUI.initialize_session_state()

# Handle clear conversation button
if clear_clicked:
    st.session_state.backend.clear_memory()
    st.session_state.messages = []
    st.rerun()

# Display chat history
ChatbotUI.render_chat_history(st.session_state.messages)

# Render input area
user_input, submit_button = ChatbotUI.render_input_area()

# Process user input
if submit_button and user_input:
    # Validate API key
    if not api_key:
        ChatbotUI.show_error("Please set your GOOGLE_API_KEY environment variable to continue.")
    else:
        try:
            # Initialize backend if needed
            if not st.session_state.backend.is_ready():
                st.session_state.backend.initialize_chain(
                    api_key=api_key,
                    model_name=model_name,
                    temperature=temperature,
                    max_tokens=max_tokens
                )
            
            # Add user message to chat history
            st.session_state.messages.append({
                "role": "user",
                "content": user_input
            })
            
            # Generate response
            with st.spinner("🤔 Thinking..."):
                response = st.session_state.backend.generate_response(user_input)
            
            # Add assistant message to chat history
            st.session_state.messages.append({
                "role": "assistant",
                "content": response
            })
            
            # Rerun to display the new messages
            st.rerun()
            
        except Exception as e:
            ChatbotUI.show_error(f"An error occurred: {str(e)}")
            # Remove the user message if there was an error
            if st.session_state.messages and st.session_state.messages[-1]["role"] == "user":
                st.session_state.messages.pop()

# Render footer
#ChatbotUI.render_footer()
