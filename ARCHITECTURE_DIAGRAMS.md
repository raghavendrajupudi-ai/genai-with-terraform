# RAG Architecture & System Diagrams

## 1. High-Level System Architecture

```
┌─────────────────────────────────────────────────────────────────┐
│                     STREAMLIT WEB INTERFACE                      │
│                         (frontend.py)                             │
├─────────────────────────────────────────────────────────────────┤
│  ┌──────────────┐  ┌──────────────┐  ┌──────────────────────┐   │
│  │  API Key     │  │  Model       │  │  Temperature & Tokens│   │
│  │  Input       │  │  Selection   │  │  Configuration       │   │
│  └──────────────┘  └──────────────┘  └──────────────────────┘   │
│                                                                   │
│  ┌────────────────────────────────────────────────────────────┐  │
│  │ Chat Display & Input                                       │  │
│  └────────────────────────────────────────────────────────────┘  │
└─────────────────────────────────────────────────────────────────┘
                              ↓
                        (app.py Logic)
                              ↓
┌─────────────────────────────────────────────────────────────────┐
│                    BACKEND PROCESSING                            │
│                      (backend.py)                                │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌─────────────────────┐            ┌──────────────────────┐    │
│  │  User Query Input   │            │  Conversation Memory │    │
│  └──────────┬──────────┘            │  (ConversationChain) │    │
│             │                       └──────────────────────┘    │
│             ├─ Route to RAG if available                        │
│             │                                                    │
│             ↓                                                    │
│  ┌─────────────────────────────────────────────────────────┐   │
│  │              RAG PIPELINE (rag_loader.py)               │   │
│  ├─────────────────────────────────────────────────────────┤   │
│  │                                                           │   │
│  │  ┌─────────────────┐  ┌─────────────────────────────┐   │   │
│  │  │ Query Vector    │  │ FAISS Vector Store          │   │   │
│  │  │ Embedding       │→→│ (All Terraform Files)       │   │   │
│  │  └─────────────────┘  └──────────┬──────────────────┘   │   │
│  │                                   │                       │   │
│  │                      ┌────────────▼────────────┐         │   │
│  │                      │ Similarity Search       │         │   │
│  │                      │ (Retrieve k=4 chunks)   │         │   │
│  │                      └────────────┬────────────┘         │   │
│  │                                   │                       │   │
│  │                      ┌────────────▼────────────┐         │   │
│  │                      │ Relevant Context        │         │   │
│  │                      │ (Source metadata incl.) │         │   │
│  │                      └────────────┬────────────┘         │   │
│  │                                   │                       │   │
│  └───────────────────────────────────┼───────────────────────┘   │
│                                       │                           │
└───────────────────────────────────────┼───────────────────────────┘
                                        ↓
┌─────────────────────────────────────────────────────────────────┐
│                   LLM REQUEST (Gemini API)                       │
├─────────────────────────────────────────────────────────────────┤
│                                                                   │
│  ┌──────────────────────────────────────────────────────────┐   │
│  │ System Prompt + Retrieved Context + User Query           │   │
│  │                                                            │   │
│  │ "You are a Terraform expert. Use this context:           │   │
│  │  [Retrieved Terraform file chunks]                       │   │
│  │  User asked: [Original question]"                        │   │
│  └──────────────────┬───────────────────────────────────────┘   │
│                     │                                             │
│                     ↓                                             │
│            ┌─────────────────┐                                   │
│            │ Gemini 2.0 Flash│                                   │
│            │ (LLM Processing)│                                   │
│            └────────┬────────┘                                   │
│                     │                                             │
│                     ↓                                             │
│            ┌─────────────────┐                                   │
│            │ Generated       │                                   │
│            │ Response        │                                   │
│            └─────────────────┘                                   │
│                                                                   │
└─────────────────────────────────────────────────────────────────┘
                          ↓
              Save to Conversation Memory
                          ↓
┌─────────────────────────────────────────────────────────────────┐
│              RESPONSE DISPLAY (frontend.py)                      │
│         Show to user with formatting & styling                   │
└─────────────────────────────────────────────────────────────────┘
```

## 2. RAG Processing Flow

```
TERRAFORM FILES IN FOLDER
    ├── main.tf
    ├── compute.tf
    ├── network.tf
    ├── variables.tf
    ├── outputs.tf
    └── provider.tf
              ↓
    ┌─────────────────────┐
    │ TerraformRAG        │
    │ .load_terraform_    │
    │  files()            │
    └──────────┬──────────┘
               ↓
    ┌─────────────────────────────────────────┐
    │ Document Objects                        │
    │ - page_content: file content            │
    │ - metadata: {source: "main.tf", ...}    │
    └──────────┬──────────────────────────────┘
               ↓
    ┌─────────────────────────────────────────┐
    │ .split_documents()                      │
    │ (chunk_size=1000, overlap=100)          │
    └──────────┬──────────────────────────────┘
               ↓
    ┌─────────────────────────────────────────┐
    │ Split Documents (e.g., 50-100 chunks)   │
    │ Each chunk: ~1000 chars with metadata   │
    └──────────┬──────────────────────────────┘
               ↓
    ┌─────────────────────────────────────────┐
    │ GoogleGenerativeAIEmbeddings             │
    │ (models/embedding-001)                  │
    └──────────┬──────────────────────────────┘
               ↓
    ┌─────────────────────────────────────────┐
    │ Vector Embeddings                       │
    │ Each chunk → 768-dim vector             │
    └──────────┬──────────────────────────────┘
               ↓
    ┌─────────────────────────────────────────┐
    │ FAISS Vector Store                      │
    │ Indexed & optimized for search          │
    └──────────┬──────────────────────────────┘
               ↓
    USER QUERY: "What resources are defined?"
               ↓
    ┌─────────────────────────────────────────┐
    │ Query → Embedding                       │
    │ (same model/method)                     │
    └──────────┬──────────────────────────────┘
               ↓
    ┌─────────────────────────────────────────┐
    │ Similarity Search                       │
    │ Find k=4 most similar vectors           │
    └──────────┬──────────────────────────────┘
               ↓
    ┌─────────────────────────────────────────┐
    │ Retrieved Chunks (with source files)    │
    │ 1. From compute.tf (similarity: 0.92)   │
    │ 2. From main.tf (similarity: 0.85)      │
    │ 3. From variables.tf (similarity: 0.78) │
    │ 4. From outputs.tf (similarity: 0.72)   │
    └──────────┬──────────────────────────────┘
               ↓
    ┌─────────────────────────────────────────┐
    │ Context String Formatted                │
    │ "From compute.tf:                       │
    │  [chunk content]                        │
    │  ---                                    │
    │  From main.tf:                          │
    │  [chunk content]"                       │
    └──────────┬──────────────────────────────┘
               ↓
    PASSED TO LLM WITH PROMPT TEMPLATE
```

## 3. RAG Chain Prompt Flow

```
┌─────────────────────────────────────────────┐
│         RAG_PROMPT_TEMPLATE                 │
├─────────────────────────────────────────────┤
│                                             │
│ "You are an expert Terraform assistant.    │
│  Use the following context from            │
│  Terraform files to answer:                │
│                                             │
│  [Context from Terraform files]            │
│                                             │
│  [User Question]                           │
│                                             │
│  Answer based on context..."                │
│                                             │
└──────────────────┬──────────────────────────┘
                   ↓
        Input Variables Filled:
        1. context = Retrieved Terraform chunks
        2. question = User's original query
                   ↓
        ┌──────────────────────────────────┐
        │ Final Prompt to Gemini           │
        │ (Max tokens configured: 500)     │
        └──────────────────┬───────────────┘
                          ↓
                    ┌────────────┐
                    │   Gemini   │
                    │   LLM      │
                    └──────┬─────┘
                           ↓
                    ┌──────────────────┐
                    │ Terraform-Aware  │
                    │ Response         │
                    │ (Context-based)  │
                    └──────────────────┘
```

## 4. Data Flow - Conversation with Memory

```
SESSION START
    ↓
┌──────────────────────┐
│ Initialize Backend   │
│ - LLM (Gemini)       │
│ - RAG (if enabled)   │
│ - Memory (empty)     │
└──────────┬───────────┘
           ↓
┌──────────────────────────────────────────┐
│ USER QUESTION 1                          │
│ "What resources are defined?"            │
└──────────┬───────────────────────────────┘
           ↓
    ┌─────────────────────────────────────┐
    │ RAG Retrieval                       │
    │ + Conversation History (empty)      │
    └──────────┬──────────────────────────┘
               ↓
    ┌──────────────────────────────────────┐
    │ Gemini Response 1 + Context          │
    └──────────┬──────────────────────────┘
               ↓
    ┌──────────────────────────────────────┐
    │ STORE IN MEMORY                      │
    │ {                                    │
    │   "input": "What resources...",      │
    │   "output": "Response 1..."          │
    │ }                                    │
    └──────────┬──────────────────────────┘
               ↓
         DISPLAY TO USER
               ↓
┌──────────────────────────────────────────┐
│ USER QUESTION 2                          │
│ "Tell me about networking"               │
└──────────┬───────────────────────────────┘
           ↓
    ┌─────────────────────────────────────┐
    │ RAG Retrieval                       │
    │ + Conversation History:             │
    │   Q1: "What resources..."           │
    │   A1: "Resources include..."        │
    └──────────┬──────────────────────────┘
               ↓
    ┌──────────────────────────────────────┐
    │ Gemini Response 2 (aware of context) │
    └──────────┬──────────────────────────┘
               ↓
    ┌──────────────────────────────────────┐
    │ STORE IN MEMORY                      │
    │ {                                    │
    │   "input": "Tell me about...",       │
    │   "output": "Response 2..."          │
    │ }                                    │
    └──────────┬──────────────────────────┘
               ↓
         DISPLAY TO USER
               ↓
    ... CONVERSATION CONTINUES WITH CONTEXT ...
```

## 5. Component Interaction Diagram

```
┌─────────────────────────────────────┐
│        STREAMLIT (frontend.py)      │
│                                     │
│  ┌─────────────────────────────┐   │
│  │ ChatbotUI                   │   │
│  │ - render_sidebar()          │   │
│  │ - render_header()           │   │
│  │ - render_chat_history()     │   │
│  │ - render_input_area()       │   │
│  │ - show_error/success/info() │   │
│  └──────────────┬──────────────┘   │
└─────────────────┼──────────────────┘
                  │
                  ↓
┌─────────────────────────────────────┐
│      APP (app.py)                   │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ Main Logic                   │  │
│  │ - Load environment variables │  │
│  │ - Handle button clicks       │  │
│  │ - Orchestrate flow           │  │
│  │ - Error handling             │  │
│  └──────────────┬───────────────┘  │
└─────────────────┼──────────────────┘
                  │
                  ↓
┌─────────────────────────────────────┐
│      BACKEND (backend.py)           │
│                                     │
│  ┌──────────────────────────────┐  │
│  │ AIBackend                    │  │
│  │ - initialize_chain()         │  │
│  │ - generate_response()        │  │
│  │ - clear_memory()             │  │
│  │ - is_ready()                 │  │
│  └──────────────┬───────────────┘  │
└─────────────────┼──────────────────┘
                  │
        ┌─────────┴─────────┐
        ↓                   ↓
┌──────────────────┐  ┌──────────────────┐
│  ConversationChain│  │ RAG Chain        │
│  (LangChain)     │  │ (If RAG enabled) │
└────────┬─────────┘  └────────┬─────────┘
         │                     │
         ↓                     ↓
    ┌─────────┐          ┌──────────────┐
    │  Gemini │          │ RAG Loader   │
    │  LLM    │          │              │
    └─────────┘          │ - Load files │
         │               │ - Embed      │
         │               │ - Retrieve   │
         │               └──────┬───────┘
         │                      │
         │                      ↓
         │               ┌──────────────┐
         │               │ FAISS Store  │
         │               │ + Embeddings │
         │               └──────────────┘
         │
         ↓
    ┌─────────────────────┐
    │ Response String     │
    └──────────┬──────────┘
               ↓
        Stored in Memory
               ↓
        Displayed in UI
```

## 6. Error Handling Flow

```
USER INPUT
    ↓
TRY: Process Query
    ├─ RAG Retrieval Attempt
    │  ├─ Success → Use Context
    │  └─ Error → Go to Catch Block
    │
    └─ Generate Response
       ├─ Success → Return Response
       └─ Error → Go to Catch Block
        ↓
    ├─ Log Error
    ├─ Fallback to Standard Chat
    │  (Without Terraform Context)
    │
    └─ Try Standard Response
       ├─ Success → Return Response
       └─ Still Error → Show Error Message
```

## 7. Configuration Architecture

```
RAG_CONFIG.py
    │
    ├─ RAG Parameters
    │  ├─ RAG_CHUNK_SIZE (1000)
    │  ├─ RAG_CHUNK_OVERLAP (100)
    │  ├─ RAG_RETRIEVAL_COUNT (4)
    │  └─ TERRAFORM_FILES_DIR ("terraform_files")
    │
    ├─ LLM Parameters
    │  ├─ DEFAULT_MODEL ("gemini-2.0-flash")
    │  ├─ DEFAULT_TEMPERATURE (0.7)
    │  └─ DEFAULT_MAX_TOKENS (500)
    │
    ├─ Feature Flags
    │  ├─ FEATURE_RAG_ENABLED (True)
    │  ├─ FEATURE_MEMORY_ENABLED (True)
    │  └─ FEATURE_SHOW_HELP (True)
    │
    └─ Helper Functions
       ├─ get_rag_config()
       ├─ get_llm_config()
       └─ get_ui_config()
```

## 8. Request/Response Cycle

```
┌─────────────────────┐
│ 1. User Input       │
│ "Explain network"   │
└──────────┬──────────┘
           ↓
┌─────────────────────────────┐
│ 2. Validate Input           │
│ - Check if input is not empty
│ - Check if API key is set   │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│ 3. Store in Chat History    │
│ {"role": "user", ...}       │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│ 4. Initialize Chain (if not)│
│ - LLM setup                 │
│ - RAG setup                 │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│ 5. Generate Response        │
│ - RAG context retrieval     │
│ - LLM inference             │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│ 6. Store Response           │
│ {"role": "assistant", ...}  │
└──────────┬──────────────────┘
           ↓
┌─────────────────────────────┐
│ 7. Display to User          │
│ - Formatted message         │
│ - Styled output             │
└─────────────────────────────┘
```

---

These diagrams show the complete architecture and flow of the RAG-enhanced Terraform chatbot system.
