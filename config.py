"""
Configuration module for AI Chatbot
Contains all configuration constants and default settings
"""

# Page Configuration
PAGE_TITLE = "AI Chatbot"
PAGE_ICON = "🤖"
PAGE_LAYOUT = "wide"
SIDEBAR_STATE = "expanded"

# Model Configuration
AVAILABLE_MODELS = ["gemini-2.0-flash"]
DEFAULT_MODEL = "gemini-2.0-flash"

# Temperature Configuration
TEMPERATURE_MIN = 0.0
TEMPERATURE_MAX = 2.0
TEMPERATURE_DEFAULT = 0.7
TEMPERATURE_STEP = 0.1

# Max Tokens Configuration
MAX_TOKENS_MIN = 50
MAX_TOKENS_MAX = 2000
MAX_TOKENS_DEFAULT = 500
MAX_TOKENS_STEP = 50

# API Configuration
GOOGLE_API_KEY_ENV_VAR = "GOOGLE_API_KEY"
GOOGLE_API_DOCS = "https://ai.google.dev/tutorials/setup"

# UI Messages
SIDEBAR_TITLE = "⚙️ Settings"
API_KEY_LABEL = "Google API Key"
API_KEY_HELP = f"Enter your Google API key for Gemini. Get one at {GOOGLE_API_DOCS}"
MODEL_LABEL = "Select Model"
MODEL_HELP = "Choose the Gemini model to use"
TEMPERATURE_LABEL = "Temperature"
TEMPERATURE_HELP = "Higher values make output more creative, lower values more deterministic"
MAX_TOKENS_LABEL = "Max Tokens"
MAX_TOKENS_HELP = "Maximum length of generated response"
CLEAR_BUTTON_LABEL = "🗑️ Clear Conversation"
SIDEBAR_INFO = (
    "This is a generative AI chatbot powered by LangChain and Google Gemini. "
    "The conversation history is maintained during the session."
)

# Main Header
APP_TITLE = "🤖 Generative AI Chatbot with Gemini"
APP_SUBTITLE = "Chat with Google's Gemini AI powered by LangChain"

# Input Area
INPUT_LABEL = "Type your message:"
INPUT_PLACEHOLDER = "Ask me anything..."

# Buttons
SEND_BUTTON_LABEL = "Send"

# Error Messages
ERROR_NO_API_KEY = "Please enter your Google API key in the sidebar to continue."
ERROR_GENERAL = "An error occurred"

# Footer
FOOTER_TEXT = "Powered by <b>LangChain</b> • <b>Google Gemini</b> • <b>Streamlit</b><br>© 2024 AI Chatbot. All rights reserved."
