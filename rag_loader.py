"""
RAG (Retrieval-Augmented Generation) module for Terraform files
Loads and processes Terraform files for context-aware responses
Uses Terraform-aware chunking to preserve resource and block structure
Supports both .tf files and PDF documents
"""

import os
import re
from pathlib import Path
from typing import List, Optional
from langchain_text_splitters import CharacterTextSplitter, RecursiveCharacterTextSplitter
from langchain_community.vectorstores import FAISS
from langchain_google_genai import GoogleGenerativeAIEmbeddings
from langchain.schema import Document
try:
    from langchain_community.document_loaders import PyPDFLoader
except ImportError:
    PyPDFLoader = None


class TerraformRAG:
    """
    RAG class for loading and processing Terraform files
    """
    
    def __init__(self, terraform_dir: str = "terraform_files"):
        """
        Initialize the RAG loader with terraform directory
        
        Args:
            terraform_dir: Path to the terraform files directory
        """
        self.terraform_dir = terraform_dir
        self.vector_store = None
        self.documents = []
        self.embeddings = None
    
    def load_terraform_files(self) -> List[Document]:
        """
        Load all Terraform files and PDF documents from the specified directory
        
        Returns:
            List of LangChain Document objects
        """
        documents = []
        terraform_path = Path(self.terraform_dir)
        
        # Get all .tf files and .pdf files
        if not terraform_path.exists():
            raise ValueError(f"Terraform directory not found: {self.terraform_dir}")
        
        tf_files = list(terraform_path.glob("*.tf"))
        pdf_files = list(terraform_path.glob("*.pdf"))
        
        if not tf_files and not pdf_files:
            raise ValueError(f"No .tf or .pdf files found in {self.terraform_dir}")
        
        # Load .tf files
        for tf_file in tf_files:
            try:
                with open(tf_file, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Create a document for each file
                doc = Document(
                    page_content=content,
                    metadata={
                        "source": tf_file.name,
                        "path": str(tf_file),
                        "file_type": "terraform"
                    }
                )
                documents.append(doc)
                
            except Exception as e:
                print(f"Error reading Terraform file {tf_file}: {str(e)}")
        
        # Load PDF files
        for pdf_file in pdf_files:
            try:
                if PyPDFLoader is None:
                    print(f"PyPDF2 not installed. Skipping PDF file {pdf_file.name}")
                    continue
                
                loader = PyPDFLoader(str(pdf_file))
                pdf_docs = loader.load()
                
                # Add metadata to PDF documents
                for pdf_doc in pdf_docs:
                    pdf_doc.metadata["source"] = pdf_file.name
                    pdf_doc.metadata["path"] = str(pdf_file)
                    pdf_doc.metadata["file_type"] = "pdf"
                
                documents.extend(pdf_docs)
                print(f"Successfully loaded PDF: {pdf_file.name} ({len(pdf_docs)} pages)")
                
            except Exception as e:
                print(f"Error reading PDF file {pdf_file}: {str(e)}")
        
        self.documents = documents
        return documents
    
    def split_documents(self, chunk_size: int = 1000, chunk_overlap: int = 100) -> List[Document]:
        """
        Split documents into chunks for better retrieval
        Uses Terraform-aware chunking for .tf files and standard chunking for PDFs
        
        Args:
            chunk_size: Size of each chunk in characters
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of split documents
        """
        if not self.documents:
            self.load_terraform_files()
        
        split_docs = []
        
        for doc in self.documents:
            file_type = doc.metadata.get('file_type', 'terraform')
            
            # Use Terraform-aware chunking for .tf files
            if file_type == 'terraform' and doc.metadata.get('source', '').endswith('.tf'):
                chunks = self._terraform_aware_split(
                    doc.page_content,
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap
                )
            else:
                # Use standard splitting for PDF and other files
                text_splitter = RecursiveCharacterTextSplitter(
                    chunk_size=chunk_size,
                    chunk_overlap=chunk_overlap,
                    separators=["\n\n", "\n", ". ", " ", ""]
                )
                chunks = text_splitter.split_text(doc.page_content)
            
            # Create documents for each chunk
            for i, chunk in enumerate(chunks):
                split_doc = Document(
                    page_content=chunk,
                    metadata={
                        **doc.metadata,
                        "chunk": i,
                        "chunk_type": self._identify_chunk_type(chunk)
                    }
                )
                split_docs.append(split_doc)
        
        return split_docs
    
    def _terraform_aware_split(self, content: str, chunk_size: int = 1000, 
                               chunk_overlap: int = 100) -> List[str]:
        """
        Split Terraform content while preserving resource blocks and structure
        
        Priority order:
        1. Split on resource/data block boundaries
        2. Split on variable/output boundaries
        3. Split on provider/terraform block boundaries
        4. Fall back to character-based splitting
        
        Args:
            content: Terraform file content
            chunk_size: Target chunk size in characters
            chunk_overlap: Overlap between chunks
            
        Returns:
            List of chunks
        """
        chunks = []
        
        # Split on major block boundaries (resource, data, variable, output, provider, terraform)
        block_pattern = r'((?:resource|data|variable|output|provider|terraform|locals|module)\s*"[^"]*"\s*\{|terraform\s*\{)'
        blocks = re.split(f'({block_pattern})', content)
        
        current_chunk = ""
        
        for i, block in enumerate(blocks):
            if not block.strip():
                continue
            
            # Check if this is a block header
            if re.match(block_pattern, block.strip()):
                # If current chunk is getting large, save it
                if len(current_chunk) > chunk_size * 0.7:
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())
                    current_chunk = block
                else:
                    current_chunk += block
            else:
                # Regular content - try to add to current chunk
                potential_chunk = current_chunk + block
                
                if len(potential_chunk) > chunk_size:
                    # Current chunk is full, save it with overlap preparation
                    if current_chunk.strip():
                        chunks.append(current_chunk.strip())
                    # Start new chunk with overlap from previous
                    overlap_text = current_chunk[-chunk_overlap:] if len(current_chunk) > chunk_overlap else current_chunk
                    current_chunk = overlap_text + block
                else:
                    current_chunk = potential_chunk
        
        # Add remaining content
        if current_chunk.strip():
            chunks.append(current_chunk.strip())
        
        # Clean up chunks and ensure they're reasonable size
        cleaned_chunks = []
        for chunk in chunks:
            if chunk and len(chunk) > 50:  # Minimum chunk size
                cleaned_chunks.append(chunk)
        
        return cleaned_chunks if cleaned_chunks else [content]
    
    def _identify_chunk_type(self, chunk: str) -> str:
        """
        Identify the type of Terraform chunk for better metadata
        
        Args:
            chunk: Terraform code chunk
            
        Returns:
            Type of chunk (resource, variable, output, provider, etc.)
        """
        chunk_lower = chunk.lower().strip()
        
        if chunk_lower.startswith('resource'):
            return "resource"
        elif chunk_lower.startswith('data'):
            return "data_source"
        elif chunk_lower.startswith('variable'):
            return "variable"
        elif chunk_lower.startswith('output'):
            return "output"
        elif chunk_lower.startswith('provider'):
            return "provider"
        elif chunk_lower.startswith('terraform'):
            return "terraform_config"
        elif chunk_lower.startswith('module'):
            return "module"
        elif chunk_lower.startswith('locals'):
            return "locals"
        else:
            return "general"
    
    def create_vector_store(self, google_api_key: str) -> FAISS:
        """
        Create a FAISS vector store from Terraform files
        
        Args:
            google_api_key: Google API key for embeddings
            
        Returns:
            FAISS vector store
        """
        # Split documents
        split_docs = self.split_documents()
        
        if not split_docs:
            raise ValueError("No documents to create vector store")
        
        # Create embeddings
        self.embeddings = GoogleGenerativeAIEmbeddings(
            model="models/gemini-embedding-001",
            google_api_key=google_api_key
        )
        
        # Create vector store
        self.vector_store = FAISS.from_documents(
            split_docs,
            self.embeddings
        )
        
        return self.vector_store
    
    def get_retriever(self, k: int = 6):
        """
        Get a retriever from the vector store
        
        Args:
            k: Number of documents to retrieve
            
        Returns:
            Retriever object
        """
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Call create_vector_store first.")
        
        return self.vector_store.as_retriever(search_kwargs={"k": k})
    
    def retrieve_context(self, query: str, k: int = 6) -> str:
        """
        Retrieve relevant context from Terraform files and PDF documents for a query
        Enhanced with metadata and relevance filtering
        
        Args:
            query: User query
            k: Number of documents to retrieve
            
        Returns:
            Combined context as string with metadata
        """
        if self.vector_store is None:
            raise ValueError("Vector store not initialized. Call create_vector_store first.")
        
        retriever = self.get_retriever(k=k)
        docs = retriever.invoke(query)
        
        # Don't filter too aggressively - include both Terraform and PDF content
        relevant_docs = docs  # Accept all retrieved documents
        
        # If no relevant docs found, return empty context to trigger "no information" response
        if not relevant_docs:
            return "No relevant Terraform configuration found for this query."
        
        # Combine retrieved documents with metadata
        context_parts = []
        
        for i, doc in enumerate(relevant_docs, 1):
            source = doc.metadata.get('source', 'unknown')
            file_type = doc.metadata.get('file_type', 'unknown')
            chunk_type = doc.metadata.get('chunk_type', 'general')
            chunk_num = doc.metadata.get('chunk', 0)
            page_num = doc.metadata.get('page', None)
            
            # Format header based on file type
            if file_type == 'pdf' and page_num is not None:
                header = f"[From {source} (PDF) - Page {page_num}]"
            elif file_type == 'pdf':
                header = f"[From {source} (PDF)]"
            else:
                header = f"[From {source} - {chunk_type}]"
            
            context_parts.append(f"{header}\n{doc.page_content}")
        
        combined_context = "\n\n---\n\n".join(context_parts)
        
        # Add a note about the context
        if relevant_docs:
            combined_context = f"Retrieved {len(relevant_docs)} relevant document(s) from Terraform files and documentation:\n\n{combined_context}"
        
        return combined_context
    
    def get_resources_summary(self) -> dict:
        """
        Extract a summary of all Terraform resources and their types
        
        Returns:
            Dictionary with resource types and counts
        """
        summary = {
            "total_files": len(self.documents),
            "resource_types": {},
            "variables": [],
            "outputs": [],
            "providers": []
        }
        
        for doc in self.documents:
            content = doc.page_content
            
            # Extract resources
            resource_matches = re.findall(r'resource\s+"([^"]+)"\s+"([^"]+)"', content)
            for res_type, res_name in resource_matches:
                if res_type not in summary["resource_types"]:
                    summary["resource_types"][res_type] = []
                summary["resource_types"][res_type].append(res_name)
            
            # Extract variables
            var_matches = re.findall(r'variable\s+"([^"]+)"', content)
            summary["variables"].extend(var_matches)
            
            # Extract outputs
            output_matches = re.findall(r'output\s+"([^"]+)"', content)
            summary["outputs"].extend(output_matches)
            
            # Extract providers
            provider_matches = re.findall(r'provider\s+"([^"]+)"', content)
            summary["providers"].extend(provider_matches)
        
        # Remove duplicates
        summary["variables"] = list(set(summary["variables"]))
        summary["outputs"] = list(set(summary["outputs"]))
        summary["providers"] = list(set(summary["providers"]))
        
        return summary
    
    def get_resource_details(self, resource_type: Optional[str] = None) -> dict:
        """
        Get detailed information about resources in Terraform files
        
        Args:
            resource_type: Optional filter by resource type
            
        Returns:
            Dictionary with resource details
        """
        details = {}
        
        for doc in self.documents:
            content = doc.page_content
            source = doc.metadata.get('source', 'unknown')
            
            # Extract resources with their details
            resource_pattern = r'resource\s+"([^"]+)"\s+"([^"]+)"\s*\{([^}]+)\}'
            matches = re.finditer(resource_pattern, content, re.DOTALL)
            
            for match in matches:
                res_type, res_name, res_body = match.groups()
                
                # Filter by type if specified
                if resource_type and res_type != resource_type:
                    continue
                
                key = f"{res_type}/{res_name}"
                if key not in details:
                    details[key] = {
                        "type": res_type,
                        "name": res_name,
                        "source_file": source,
                        "properties": []
                    }
                
                # Extract properties (simplified)
                properties = re.findall(r'(\w+)\s*=', res_body)
                details[key]["properties"].extend(properties)
        
        return details
