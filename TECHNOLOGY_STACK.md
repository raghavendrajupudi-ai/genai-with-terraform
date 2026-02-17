# Technology Stack Summary

## Project Overview

**GenAI Terraform Chatbot** - An intelligent AI-powered chatbot application that provides context-aware assistance for Terraform infrastructure as code using Retrieval-Augmented Generation (RAG) and Google Gemini AI.

---

## 🎨 Frontend Technologies

### **Streamlit** (v1.28.0+)
- **Purpose**: Web application framework and UI rendering
- **Key Features**:
  - Real-time interactive web interface
  - Session state management for conversation persistence
  - Responsive layout with sidebar navigation
  - Custom CSS styling for branded UI (EGEN theme with navy blue #001f3f)
  - Chat-style message display with user/assistant differentiation
  - Form inputs with validation and error handling

### **Frontend Architecture**
- **Pattern**: Modular component-based design
- **File**: `frontend.py` - ChatbotUI class
- **Components**:
  - Page configuration and styling
  - Header and branding
  - Sidebar with model parameters
  - Chat history display
  - User input area with submit handling
  - Error/success message rendering

---

## ⚙️ Backend Technologies

### **LangChain Framework** (v0.1.0+)
- **Purpose**: LLM application orchestration and workflow management
- **Components Used**:
  - `ChatGoogleGenerativeAI` - Gemini model integration
  - `PromptTemplate` - Structured prompt engineering
  - `ConversationBufferMemory` - Conversation history management
  - Document processing and text splitting utilities
  - Vector store integration for RAG

### **Google Generative AI (Gemini)** (v0.3.0+)
- **Models Supported**:
  - `gemini-2.0-flash` (Default) - Fast, efficient responses
  - `gemini-1.5-pro` - Advanced reasoning capabilities
  - `gemini-1.5-flash` - Balanced performance
- **Features**:
  - Natural language understanding and generation
  - Context-aware responses (up to 500 tokens default)
  - Temperature control (0.0-2.0) for response creativity
  - Streaming support for real-time responses

### **Backend Architecture**
- **Pattern**: Service layer with dependency injection
- **File**: `backend.py` - AIBackend class
- **Capabilities**:
  - LLM initialization and configuration
  - RAG query processing
  - Conversation memory management
  - Dynamic prompt template construction
  - Error handling and validation

---

## 🧠 RAG (Retrieval-Augmented Generation) System

### **Purpose**
Enhance AI responses with context from Terraform infrastructure files, providing accurate, project-specific guidance.

### **RAG Configuration** (`RAG_CONFIG.py`)

| Parameter | Value | Purpose |
|-----------|-------|---------|
| **Chunk Size** | 1000 characters | Size of each document segment |
| **Chunk Overlap** | 100 characters | Context continuity between chunks |
| **Retrieval Count** | 4 documents | Number of relevant chunks retrieved per query |
| **Embedding Model** | `text-embedding-004` | Google's optimized embedding model |
| **Vector Store** | FAISS | Fast similarity search |

### **Document Processing Pipeline** (`rag_loader.py`)
1. **Document Loading**
   - Terraform (.tf) files from `terraform_files/` directory
   - PDF documentation support via PyPDF
   - Automatic encoding detection (UTF-8)

2. **Intelligent Chunking**
   - **Terraform-Aware Splitting**: Preserves resource blocks, variables, and modules
   - **Recursive Character Text Splitter**: Multi-level chunking strategy
   - Custom separators for Terraform syntax:
     - Resource blocks (`resource "type" "name"`)
     - Variable definitions
     - Output blocks
     - Module declarations

3. **Semantic Chunking Options**
   - Small chunks (500 chars): Precise retrieval for specific resources
   - Medium chunks (1000 chars): Balanced context (default)
   - Large chunks (2000 chars): Comprehensive resource understanding

---

## 🔍 FAISS Vector Store

### **Technology**: Facebook AI Similarity Search (FAISS-CPU v1.7.4+)

### **Purpose**
High-performance vector similarity search for document retrieval in RAG pipeline.

### **Key Features**
- **Local Vector Storage**: No external database dependencies
- **Fast K-Nearest Neighbors**: Sub-millisecond similarity search
- **In-Memory Operation**: Cached for optimal performance
- **Scalability**: Handles thousands of document chunks efficiently

### **Workflow**
1. **Embedding Generation**: Text → 768-dimensional vectors (via `text-embedding-004`)
2. **Index Building**: FAISS creates optimized search index
3. **Query Processing**: User question → vector → similarity search
4. **Retrieval**: Top-K most relevant document chunks returned
5. **Context Augmentation**: Retrieved docs injected into LLM prompt

### **Performance Optimization**
- Vector store caching enabled by default
- Lazy loading on first query
- Automatic reindexing on file changes

---

## 📦 Core Dependencies

### **Language & Runtime**
- **Python** 3.8+ (Recommended: 3.10+)

### **AI/ML Libraries**
```
langchain==0.1.0+                    # LLM orchestration framework
langchain-core==0.1.0+               # Core LangChain abstractions
langchain-google-genai==0.0.1+       # Google Gemini integration
langchain-text-splitters==0.0.1+     # Document chunking utilities
langchain-community==0.0.1+          # Community components
google-generativeai==0.3.0+          # Google AI SDK
faiss-cpu==1.7.4+                    # Vector similarity search
```

### **Web & Utilities**
```
streamlit==1.28.0+                   # Web UI framework
python-dotenv==1.0.0+                # Environment variable management
pyarrow==14.0.1+                     # Columnar data serialization
pypdf==3.0.0+                        # PDF document processing
```

---

## 🏗️ Architecture & Design Patterns

### **Layered Architecture**
```
┌─────────────────────────────────────┐
│   Presentation Layer (Streamlit)    │
│         frontend.py                  │
├─────────────────────────────────────┤
│   Business Logic Layer               │
│   backend.py + rag_loader.py        │
├─────────────────────────────────────┤
│   AI Services Layer                  │
│   LangChain + Gemini + FAISS        │
├─────────────────────────────────────┤
│   Data Layer                         │
│   Terraform Files + Vector Store    │
└─────────────────────────────────────┘
```

### **Design Patterns**
- **Singleton**: Backend instance management via Streamlit session state
- **Strategy**: Interchangeable LLM models and embedding strategies
- **Factory**: Dynamic chain creation based on configuration
- **Repository**: Document loading and vector store abstraction
- **Observer**: Streamlit reactive updates on user interaction

### **Key Principles**
- ✅ Separation of Concerns (UI ↔ Logic ↔ Data)
- ✅ Single Responsibility (Each class has one clear purpose)
- ✅ Dependency Injection (Configurable components)
- ✅ Open/Closed (Extensible without modification)

---

## 🔐 Security & Configuration

### **Environment Variables**
- `GOOGLE_API_KEY`: Gemini API authentication (required)
- Secure loading via `python-dotenv` from `.env` file
- Fallback to Streamlit sidebar input

### **Secret Management**
- **Local Development**: `.env` file (git-ignored)
- **Cloud Deployment**: Google Cloud Secret Manager
- Cloud Run retrieves secrets at runtime
- No hardcoded credentials in codebase

### **Configuration Management** (`RAG_CONFIG.py`)
- Centralized settings for easy tuning
- Environment-specific configurations
- Performance vs. accuracy trade-offs
- Feature flags (RAG toggle, metadata display, etc.)

---

## 🚀 Deployment & Infrastructure

### **Containerization**
- **Docker**: Multi-stage builds for optimized images
- **Base Image**: Python 3.10-slim
- **Port**: 8501 (Streamlit default)
- **Health Checks**: HTTP endpoint monitoring

### **Cloud Platform: Google Cloud**
- **Service**: Cloud Run (serverless containers)
- **Artifact Registry**: Docker image storage
- **Secret Manager**: API key and credentials
- **CI/CD**: GitHub Actions with Workload Identity Federation

### **Infrastructure as Code**
- **Terraform Files**: Located in `terraform_files/`
  - `provider.tf` - GCP provider configuration
  - `compute.tf` - Cloud Run service definition
  - `network.tf` - Networking resources
  - `variables.tf` - Configurable parameters
  - `outputs.tf` - Service endpoints

---

## 📊 Performance Characteristics

### **Response Time**
- **Without RAG**: 1-2 seconds (direct LLM query)
- **With RAG**: 2-4 seconds (includes vector search + retrieval)
- **First Request**: +1-2 seconds (vector store initialization)

### **Scalability**
- **Concurrent Users**: Handled by Cloud Run auto-scaling
- **Vector Store**: Supports 10,000+ document chunks
- **Memory Usage**: ~500MB-1GB per instance
- **CPU**: 2 vCPUs recommended for optimal performance

### **Cost Optimization**
- Gemini API: Pay-per-token pricing
- Cloud Run: Scale to zero when idle (min instances = 0)
- FAISS: Local processing (no external DB costs)
- Caching: Reduces redundant API calls

---

## 🔄 Data Flow

### **User Query Processing**
```
User Input (Streamlit)
    ↓
Frontend Validation
    ↓
Backend.generate_response()
    ↓
┌─────────────────────────┐
│   RAG Enabled?          │
├─────────────────────────┤
│ YES              │  NO  │
│  ↓               │   ↓  │
│ Vector Search    │ Direct│
│  ↓               │ Query │
│ Retrieve Docs    │   ↓  │
│  ↓               │   ↓  │
│ Build Context    │   ↓  │
└────↓─────────────┴───↓──┘
     ↓                 ↓
  LLM Prompt Construction
     ↓
  Gemini API Call
     ↓
  Response Generation
     ↓
  Memory Update
     ↓
  Frontend Display
```

---

## 📈 Future Enhancements Roadmap

### **Planned Features**
- Multi-modal support (images, diagrams in RAG)
- Real-time Terraform file monitoring and auto-indexing
- Advanced chunking strategies (semantic, agentic)
- Multi-language embedding support
- Chat export and session management
- User feedback loop for answer quality
- Integration with Terraform Cloud API

### **Scalability Improvements**
- Redis caching for distributed deployments
- PostgreSQL with pgvector for persistent storage
- Horizontal scaling with load balancing
- CDN integration for static assets

---

## 📞 Technical Contacts

**For Questions or Support:**
- **Architecture**: Review this document and `ARCHITECTURE_DIAGRAMS.md`
- **Setup**: See `README.md` and `README_DOCKER.md`
- **Deployment**: Refer to `GITHUB_ACTIONS_SETUP.md`
- **Configuration**: Modify `RAG_CONFIG.py` and `config.py`

---

## 📝 Document Version

- **Version**: 1.0.0
- **Last Updated**: February 18, 2026
- **Project**: GenAI Terraform Chatbot
- **Tech Stack**: LangChain + Gemini + FAISS + Streamlit + Terraform + Google Cloud

---

**© 2026 EGEN Solutions - Enterprise AI Infrastructure**
