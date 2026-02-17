"""
Script to check all available models in Google Generative AI API
Run this to see what models are available for your API key
"""

import os
from dotenv import load_dotenv
import google.generativeai as genai

# Load environment variables
load_dotenv()

# Get API key
api_key = os.getenv("GOOGLE_API_KEY", "")

if not api_key:
    print("❌ ERROR: GOOGLE_API_KEY not found in environment variables")
    print("Please set your API key in the .env file or environment")
    exit(1)

print("🔑 API Key found! Checking available models...\n")

# Configure the API
genai.configure(api_key=api_key)

print("=" * 80)
print("AVAILABLE MODELS IN GOOGLE GENERATIVE AI API")
print("=" * 80)

try:
    # List all available models
    all_models = list(genai.list_models())
    
    print(f"\n✅ Total models found: {len(all_models)}\n")
    
    # Categorize models
    embedding_models = []
    chat_models = []
    other_models = []
    
    for model in all_models:
        model_name = model.name
        display_name = model.display_name
        
        model_info = f"{model_name} ({display_name})"
        
        # Categorize by name
        if "embedding" in model_name.lower() or "embed" in model_name.lower():
            embedding_models.append((model_name, model_info, model))
        elif "gemini" in model_name.lower() or "chat" in model_name.lower():
            chat_models.append((model_name, model_info, model))
        else:
            other_models.append((model_name, model_info, model))
    
    # Print embedding models
    print("📊 EMBEDDING MODELS:")
    print("-" * 80)
    if embedding_models:
        for model_name, model_info, model_obj in embedding_models:
            print(f"  ✓ {model_info}")
    else:
        print("  (None found)")
    
    # Print chat/generation models
    print("\n💬 CHAT/GENERATION MODELS:")
    print("-" * 80)
    if chat_models:
        for model_name, model_info, model_obj in chat_models:
            print(f"  ✓ {model_info}")
    else:
        print("  (None found)")
    
    # Print other models
    if other_models:
        print("\n🔧 OTHER MODELS:")
        print("-" * 80)
        for model_name, model_info, model_obj in other_models:
            print(f"  ✓ {model_info}")
    
    print("\n" + "=" * 80)
    print("DETAILED MODEL INFORMATION:")
    print("=" * 80 + "\n")
    
    for model in all_models:
        print(f"Model Name: {model.name}")
        print(f"Display Name: {model.display_name}")
        print(f"Description: {model.description}")
        
        # Show token limits if available
        if hasattr(model, 'input_token_limit'):
            print(f"Input Token Limit: {model.input_token_limit}")
        if hasattr(model, 'output_token_limit'):
            print(f"Output Token Limit: {model.output_token_limit}")
        
        print("-" * 80 + "\n")
    
    # Recommendations
    print("\n" + "=" * 80)
    print("RECOMMENDATIONS FOR RAG SYSTEM:")
    print("=" * 80)
    print("""
For your RAG system, use the EMBEDDING models from the list above.
Common embedding models:
  - models/embedding-001
  - models/text-embedding-004 (newer)

Update rag_loader.py with the correct model name from the list above.
For example:
    self.embeddings = GoogleGenerativeAIEmbeddings(
        model="YOUR_MODEL_NAME_HERE",
        google_api_key=google_api_key
    )
""")
    
    
except Exception as e:
    print(f"❌ ERROR: {str(e)}")
    print("\nMake sure:")
    print("  1. Your GOOGLE_API_KEY is correct")
    print("  2. You have internet connection")
    print("  3. The API is enabled in your Google Cloud project")
