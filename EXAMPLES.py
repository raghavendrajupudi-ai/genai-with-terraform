"""
Example Usage of RAG System
Demonstrates how to use the TerraformRAG class directly
"""

# ============================================================================
# Example 1: Basic RAG Setup
# ============================================================================

from rag_loader import TerraformRAG

# Initialize RAG loader
rag = TerraformRAG(terraform_dir="terraform_files")

# Load Terraform files
documents = rag.load_terraform_files()
print(f"Loaded {len(documents)} Terraform files")

# Create vector store (requires API key)
api_key = "your_google_api_key_here"
vector_store = rag.create_vector_store(api_key)
print("Vector store created successfully!")


# ============================================================================
# Example 2: Retrieve Context for a Query
# ============================================================================

# Ask a question and get relevant context
query = "What compute resources are defined?"
context = rag.retrieve_context(query, k=4)

print(f"\n--- Context for query: '{query}' ---")
print(context)


# ============================================================================
# Example 3: Use with Backend
# ============================================================================

from backend import AIBackend

# Initialize backend
backend = AIBackend()

# Configure with API key and model settings
backend.initialize_chain(
    api_key=api_key,
    model_name="gemini-2.0-flash",
    temperature=0.7,
    max_tokens=500
)

# Generate response (automatically uses RAG)
response = backend.generate_response("What resources are in my Terraform files?")
print(f"\n--- AI Response ---")
print(response)


# ============================================================================
# Example 4: Custom RAG Configuration
# ============================================================================

from rag_loader import TerraformRAG

# Create RAG with custom settings
rag = TerraformRAG(terraform_dir="terraform_files")

# Load and split documents with custom chunk size
docs = rag.load_terraform_files()
split_docs = rag.split_documents(
    chunk_size=800,        # Smaller chunks for more granular retrieval
    chunk_overlap=150      # More overlap for context continuity
)

print(f"Split into {len(split_docs)} chunks")

# Create vector store
vector_store = rag.create_vector_store(api_key)

# Retrieve with custom count
context = rag.retrieve_context(
    "Explain the network configuration",
    k=6  # Get more documents for comprehensive context
)


# ============================================================================
# Example 5: Advanced - Direct Retriever Usage
# ============================================================================

from rag_loader import TerraformRAG

rag = TerraformRAG(terraform_dir="terraform_files")
rag.load_terraform_files()
rag.create_vector_store(api_key)

# Get a retriever object for direct use
retriever = rag.get_retriever(k=4)

# Retrieve documents directly
docs = retriever.invoke("What variables are defined?")

# Process results
for i, doc in enumerate(docs, 1):
    source = doc.metadata.get('source', 'unknown')
    content = doc.page_content[:200] + "..."
    print(f"\n--- Result {i} (from {source}) ---")
    print(content)


# ============================================================================
# Example 6: Complete Workflow with Error Handling
# ============================================================================

from rag_loader import TerraformRAG
from backend import AIBackend

def chat_with_terraform(api_key: str, question: str) -> str:
    """
    Complete workflow: Load RAG, initialize backend, get response
    """
    try:
        # Initialize RAG
        rag = TerraformRAG(terraform_dir="terraform_files")
        rag.load_terraform_files()
        rag.create_vector_store(api_key)
        
        # Initialize backend with RAG
        backend = AIBackend()
        backend.initialize_chain(
            api_key=api_key,
            model_name="gemini-2.0-flash",
            temperature=0.7,
            max_tokens=500
        )
        
        # Generate response
        response = backend.generate_response(question)
        return response
        
    except Exception as e:
        return f"Error: {str(e)}"

# Usage
answer = chat_with_terraform(api_key, "Tell me about my infrastructure")
print(f"\nAnswer: {answer}")


# ============================================================================
# Example 7: Batch Processing - Ask Multiple Questions
# ============================================================================

from backend import AIBackend

backend = AIBackend()
backend.initialize_chain(
    api_key=api_key,
    model_name="gemini-2.0-flash",
    temperature=0.7,
    max_tokens=500
)

questions = [
    "What compute resources are defined?",
    "Explain the network configuration",
    "What variables are used?",
    "What are the main outputs?"
]

print("\n--- Batch Processing Example ---\n")

for question in questions:
    try:
        response = backend.generate_response(question)
        print(f"Q: {question}")
        print(f"A: {response}\n")
        print("-" * 80 + "\n")
    except Exception as e:
        print(f"Error processing question: {e}\n")


# ============================================================================
# Example 8: Using Configuration Helpers
# ============================================================================

from RAG_CONFIG import get_rag_config, get_llm_config, get_ui_config

# Get configurations as dictionaries
rag_config = get_rag_config()
llm_config = get_llm_config()
ui_config = get_ui_config()

print("\n--- Configuration Loaded ---")
print(f"RAG Config: {rag_config}")
print(f"LLM Config: {llm_config}")
print(f"UI Config: {ui_config}")

# Use in initialization
rag = TerraformRAG(terraform_dir=rag_config["terraform_dir"])
rag.load_terraform_files()
rag.create_vector_store(api_key)

context = rag.retrieve_context(
    "What resources?",
    k=rag_config["retrieval_count"]
)


# ============================================================================
# Example 9: Conversation with Memory
# ============================================================================

from backend import AIBackend

backend = AIBackend()
backend.initialize_chain(
    api_key=api_key,
    model_name="gemini-2.0-flash",
    temperature=0.7,
    max_tokens=500
)

# Have a conversation that maintains history
print("\n--- Conversation with Memory ---\n")

conversation = [
    "What compute resources are in my Terraform?",
    "Can you explain more about the network configuration?",
    "How are these connected to each other?",
    "What are the security settings?"
]

for message in conversation:
    response = backend.generate_response(message)
    print(f"User: {message}")
    print(f"AI: {response}\n")
    print("-" * 80 + "\n")

# Get conversation history
history = backend.get_conversation_history()
print(f"Conversation Memory: {history}")


# ============================================================================
# Example 10: Performance Testing
# ============================================================================

import time
from rag_loader import TerraformRAG

rag = TerraformRAG(terraform_dir="terraform_files")
rag.load_terraform_files()
rag.create_vector_store(api_key)

# Test retrieval performance
test_queries = [
    "What compute resources?",
    "Network setup",
    "Variables definition",
    "Security configuration"
]

print("\n--- Performance Testing ---\n")

for query in test_queries:
    start_time = time.time()
    context = rag.retrieve_context(query, k=4)
    elapsed = time.time() - start_time
    
    print(f"Query: '{query}'")
    print(f"Retrieval Time: {elapsed:.3f}s")
    print(f"Context Size: {len(context)} characters\n")


# ============================================================================
# Tips and Best Practices
# ============================================================================

"""
BEST PRACTICES:

1. API Key Management
   - Use environment variables: export GOOGLE_API_KEY=your_key
   - Or use .env file: GOOGLE_API_KEY=your_key
   - Never hardcode in production

2. Error Handling
   - Always wrap RAG operations in try-except
   - Implement fallback to standard chat
   - Log errors for debugging

3. Performance
   - Cache vector store in memory (CACHE_VECTOR_STORE = True)
   - Adjust chunk size based on Terraform file complexity
   - Use appropriate retrieval count (k parameter)

4. Terraform Files
   - Keep files well-organized
   - Use clear variable names
   - Add comments to complex sections
   - Follow Terraform naming conventions

5. Prompt Engineering
   - Use specific, clear questions
   - Reference resource types when asking
   - Ask follow-up questions for clarity
   - Use technical Terraform terminology

6. Testing
   - Test with simple questions first
   - Verify answers against actual Terraform files
   - Check retrieval works across all files
   - Monitor API usage and costs

COMMON ISSUES & SOLUTIONS:

Issue: "No .tf files found"
Solution: Ensure terraform_files/ directory exists and has .tf files

Issue: "Vector store not initialized"
Solution: Check API key is valid and internet connection is active

Issue: "Slow retrieval"
Solution: Reduce RAG_CHUNK_SIZE or RAG_RETRIEVAL_COUNT

Issue: "Missing context"
Solution: Increase RAG_CHUNK_OVERLAP or RAG_RETRIEVAL_COUNT

Issue: "Memory issues"
Solution: Set CACHE_VECTOR_STORE = False or reduce chunk overlap
"""
