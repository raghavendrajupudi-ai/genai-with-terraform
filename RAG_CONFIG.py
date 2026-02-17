"""
Configuration file for RAG and application settings
Customize these values to optimize performance based on your needs
"""

# ============================================================================
# RAG (Retrieval-Augmented Generation) Configuration
# ============================================================================

# Document Chunk Size
# How many characters in each document chunk
# Smaller = more chunks, more retrieval calls
# Larger = fewer chunks, potentially missing context
RAG_CHUNK_SIZE = 1000

# Document Chunk Overlap
# How many characters overlap between consecutive chunks
# Helps maintain context continuity between chunks
RAG_CHUNK_OVERLAP = 100

# Number of Documents to Retrieve
# How many relevant document chunks to retrieve for context
# More documents = more context but slower processing
# Fewer documents = faster but potentially less relevant context
RAG_RETRIEVAL_COUNT = 4

# Terraform Files Directory
# Path to your Terraform files (relative to app root)
TERRAFORM_FILES_DIR = "terraform_files"

# ============================================================================
# LLM Configuration
# ============================================================================

# Default Model Name
# Options: "gemini-2.0-flash", "gemini-1.5-pro", etc.
DEFAULT_MODEL = "gemini-2.0-flash"

# Default Temperature
# 0.0 = deterministic (most consistent)
# 0.7 = balanced (default)
# 2.0 = creative (most random)
DEFAULT_TEMPERATURE = 0.7

# Default Max Tokens
# Maximum length of generated response in tokens
# 1 token ≈ 4 characters
DEFAULT_MAX_TOKENS = 500

# ============================================================================
# Vector Store Configuration
# ============================================================================

# Embedding Model
# Used for converting text to vectors
EMBEDDING_MODEL = "text-embedding-004"  # Gemini embedding model optimized for small text
# Vector Store Type
# Using FAISS for local vector similarity search
VECTOR_STORE_TYPE = "FAISS"

# ============================================================================
# Streamlit UI Configuration
# ============================================================================

# Page Layout
PAGE_LAYOUT = "wide"

# Sidebar State
SIDEBAR_STATE = "expanded"

# Chat Message Colors
CHAT_MESSAGE_USER_BG = "#e3f2fd"
CHAT_MESSAGE_ASSISTANT_BG = "#f5f5f5"
CHAT_MESSAGE_ERROR_BG = "#ffebee"

# ============================================================================
# Application Behavior
# ============================================================================

# Enable RAG by Default
USE_RAG_BY_DEFAULT = True

# Enable Conversation Memory
USE_CONVERSATION_MEMORY = True

# Show Metadata in Responses
# Shows which Terraform file the context came from
SHOW_SOURCE_METADATA = True

# ============================================================================
# Performance Tuning
# ============================================================================

# Cache Vector Store
# Keep vector store in memory to avoid rebuilding
# Trade-off: More memory usage for faster queries
CACHE_VECTOR_STORE = True

# Verbose Logging
# Set to True for debugging, False for production
VERBOSE_LOGGING = False

# ============================================================================
# Advanced RAG Settings
# ============================================================================

# RAG Prompt Template
# Customize how RAG augments the prompt
RAG_SYSTEM_PROMPT = """You are an expert Terraform assistant. 
Use the following context from Terraform files to answer questions accurately.
If the context doesn't contain relevant information, say so and provide general knowledge if helpful.
Always explain Terraform concepts clearly."""

# Fallback Behavior
# What to do if RAG fails
FALLBACK_TO_STANDARD_CHAT = True

# Context Window Size
# How much context to keep in conversation history
CONTEXT_WINDOW = 5

# ============================================================================
# Feature Flags
# ============================================================================

# Enable RAG System
FEATURE_RAG_ENABLED = True

# Enable Conversation Memory
FEATURE_MEMORY_ENABLED = True

# Enable Dark Mode
FEATURE_DARK_MODE = False

# Show Help in Sidebar
FEATURE_SHOW_HELP = True

# ============================================================================
# Security Configuration
# ============================================================================

# API Key Validation
# Whether to validate API keys before using them
VALIDATE_API_KEY = True

# Max API Calls per Session
# Limit to prevent excessive API usage
MAX_API_CALLS_PER_SESSION = 100

# Rate Limiting
# Delay between API calls in seconds
RATE_LIMIT_DELAY = 0.1

# ============================================================================
# Logging Configuration
# ============================================================================

# Log File Path
LOG_FILE_PATH = "logs/chatbot.log"

# Log Level
# Options: DEBUG, INFO, WARNING, ERROR, CRITICAL
LOG_LEVEL = "INFO"

# ============================================================================
# Custom RAG Optimization
# ============================================================================

# For Large Terraform Projects
# Optimize settings for projects with 50+ Terraform files
LARGE_PROJECT_CONFIG = {
    "chunk_size": 800,
    "chunk_overlap": 150,
    "retrieval_count": 6,
    "cache_enabled": True
}

# For Small Terraform Projects
# Optimize settings for minimal projects (5-10 files)
SMALL_PROJECT_CONFIG = {
    "chunk_size": 1500,
    "chunk_overlap": 50,
    "retrieval_count": 2,
    "cache_enabled": False
}

# ============================================================================
# Import Configuration
# ============================================================================

def get_rag_config():
    """Get RAG configuration as a dictionary"""
    return {
        "chunk_size": RAG_CHUNK_SIZE,
        "chunk_overlap": RAG_CHUNK_OVERLAP,
        "retrieval_count": RAG_RETRIEVAL_COUNT,
        "terraform_dir": TERRAFORM_FILES_DIR,
        "embedding_model": EMBEDDING_MODEL,
        "use_rag": FEATURE_RAG_ENABLED
    }

def get_llm_config():
    """Get LLM configuration as a dictionary"""
    return {
        "model": DEFAULT_MODEL,
        "temperature": DEFAULT_TEMPERATURE,
        "max_tokens": DEFAULT_MAX_TOKENS,
        "verbose": VERBOSE_LOGGING
    }

def get_ui_config():
    """Get UI configuration as a dictionary"""
    return {
        "layout": PAGE_LAYOUT,
        "sidebar_state": SIDEBAR_STATE,
        "show_help": FEATURE_SHOW_HELP,
        "dark_mode": FEATURE_DARK_MODE
    }

# ============================================================================
# Usage Examples
# ============================================================================

"""
In your application code, use configurations like:

    # In backend.py
    from config import get_rag_config, get_llm_config
    
    rag_config = get_rag_config()
    terraform_rag = TerraformRAG(
        terraform_dir=rag_config["terraform_dir"]
    )
    
    # In rag_loader.py
    context = self.retrieve_context(
        query=user_input,
        k=rag_config["retrieval_count"]
    )
    
    # In frontend.py
    from config import get_ui_config
    
    ui_config = get_ui_config()
    st.set_page_config(layout=ui_config["layout"])

For quick adjustments:
    1. Edit values in this file
    2. Restart the Streamlit app
    3. Changes take effect immediately

Performance Tips:
    - If responses are slow: Reduce RAG_RETRIEVAL_COUNT
    - If context is missing: Increase RAG_CHUNK_OVERLAP
    - If memory is tight: Set CACHE_VECTOR_STORE = False
    - For large projects: Use LARGE_PROJECT_CONFIG values
"""
