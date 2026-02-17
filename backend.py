"""
Backend module for AI Chatbot
Handles LangChain integration and Gemini API communication with RAG
"""

from langchain_google_genai import ChatGoogleGenerativeAI
from langchain_core.prompts import PromptTemplate
from typing import Optional
import os
from rag_loader import TerraformRAG

# Simple memory implementation for conversation history
class ConversationBufferMemory:
    def __init__(self):
        self.messages = []
        
    def save_context(self, inputs, outputs):
        self.messages.append({"input": inputs.get("input", ""), "output": outputs.get("output", "")})
        
    def clear(self):
        self.messages = []
        
    @property
    def buffer_as_messages(self):
        return self.messages


class AIBackend:
    """
    Backend class for managing LLM interactions with Google Gemini and RAG
    """
    
    def __init__(self):
        """Initialize the backend with default values"""
        self.llm = None  # Store the LLM instance
        self.rag_prompt_template = None  # Store the RAG prompt template
        self.memory: ConversationBufferMemory = ConversationBufferMemory()
        self.current_api_key: Optional[str] = None
        self.current_model: Optional[str] = None
        self.current_temperature: float = 0.7
        self.current_max_tokens: int = 500
        self.terraform_rag: Optional[TerraformRAG] = None
        self.use_rag: bool = True
    
    def initialize_chain(
        self,
        api_key: str,
        model_name: str,
        temperature: float,
        max_tokens: int
    ) -> None:
        """
        Initialize the conversation chain with specified parameters
        Also initializes RAG with Terraform files
        
        Args:
            api_key: Google API key for authentication
            model_name: Name of the Gemini model to use
            temperature: Temperature parameter for creativity (0.0-2.0)
            max_tokens: Maximum tokens in the response
        """
        # Check if we need to reinitialize (model or key changed)
        if (
            self.llm is None
            or self.current_api_key != api_key
            or self.current_model != model_name
            or self.current_temperature != temperature
            or self.current_max_tokens != max_tokens
        ):
            try:
                # Set environment variable
                os.environ["GOOGLE_API_KEY"] = api_key
                
                # Initialize LLM
                self.llm = ChatGoogleGenerativeAI(
                    model=model_name,
                    temperature=temperature,
                    max_output_tokens=max_tokens,
                    google_api_key=api_key
                )
                
                # Initialize RAG with Terraform files
                try:
                    self.terraform_rag = TerraformRAG(terraform_dir="terraform_files")
                    self.terraform_rag.create_vector_store(api_key)
                    
                    # Create RAG prompt template
                    self.rag_prompt_template = PromptTemplate(
                        input_variables=["context", "question"],
                        template="""You are a Terraform documentation assistant. Use only the provided Terraform configuration context to answer the question. Present the answer clearly. 

                    Terraform Configuration Context:
                    {context}

                    Question:
                    {question}

                    Answer:"""
                    )
                except Exception as e:
                    print(f"Warning: RAG initialization failed: {str(e)}. Continuing without RAG.")
                    self.use_rag = False
                
                # Store current configuration
                self.current_api_key = api_key
                self.current_model = model_name
                self.current_temperature = temperature
                self.current_max_tokens = max_tokens
                
            except Exception as e:
                raise Exception(f"Failed to initialize LLM: {str(e)}")
    
    def generate_response(self, user_input: str) -> str:
        """
        Generate a response from the AI based on user input
        Uses RAG to provide context from Terraform files ONLY
        Does NOT generate generic answers if RAG fails
        
        Args:
            user_input: The user's input message
            
        Returns:
            The AI's response as a string (only from Terraform files)
            
        Raises:
            Exception: If the conversation chain is not initialized
        """
        if self.llm is None:
            raise Exception("LLM not initialized. Please provide API key and settings.")
        
        # RAG must be available and initialized - do not fall back to generic LLM
        if not (self.use_rag and self.terraform_rag and self.rag_prompt_template):
            raise Exception("RAG system not initialized. Cannot generate response without Terraform context.")
        
        try:
            # Retrieve relevant context from Terraform files (k=6 to get all 6 files)
            context = self.terraform_rag.retrieve_context(user_input, k=6)
            
            # Check if we actually got relevant context
            if "No relevant Terraform configuration found" in context:
                # No relevant context found - return message indicating this
                response = "I cannot answer this question as it is not covered in the provided Terraform files. Please ask about resources and configurations defined in your GCP Terraform files."
            else:
                # Generate response using LLM with formatted prompt
                formatted_prompt = self.rag_prompt_template.format(
                    context=context,
                    question=user_input
                )
                response = self.llm.invoke(formatted_prompt).content
            
            # Also store in conversation memory
            self.memory.save_context({"input": user_input}, {"output": response})
            
            return response
        except Exception as e:
            raise Exception(f"Failed to retrieve context from Terraform files: {str(e)}")
    
    def clear_memory(self) -> None:
        """Clear the conversation memory and reset the chain"""
        self.memory.clear()
        self.llm = None
    
    def get_conversation_history(self) -> dict:
        """
        Get the current conversation history from memory
        
        Returns:
            Dictionary containing conversation buffer variables
        """
        return self.memory.buffer_as_messages if hasattr(self.memory, 'buffer_as_messages') else {}
    
    def is_ready(self) -> bool:
        """
        Check if the backend is ready to generate responses
        
        Returns:
            True if LLM is initialized, False otherwise
        """
        return self.llm is not None
    
    def get_infrastructure_summary(self) -> dict:
        """
        Get a summary of the infrastructure from Terraform files
        Uses Terraform-aware analysis
        
        Returns:
            Dictionary with infrastructure summary
        """
        if self.terraform_rag is None:
            raise Exception("RAG not initialized")
        
        try:
            return self.terraform_rag.get_resources_summary()
        except Exception as e:
            print(f"Could not get infrastructure summary: {str(e)}")
            return {}
    
    def get_resource_details(self, resource_type: str = None) -> dict:
        """
        Get detailed information about resources
        
        Args:
            resource_type: Optional filter by resource type
            
        Returns:
            Dictionary with resource details
        """
        if self.terraform_rag is None:
            raise Exception("RAG not initialized")
        
        try:
            return self.terraform_rag.get_resource_details(resource_type)
        except Exception as e:
            print(f"Could not get resource details: {str(e)}")
            return {}
