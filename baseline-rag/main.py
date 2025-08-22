#!/usr/bin/env python3
"""
LangChain + ChromaDB RAG Baseline System

This implements the industry-standard RAG approach using:
- LangChain for orchestration
- ChromaDB for vector storage (same as Nancy)
- FastEmbed for embeddings (same as Nancy) 
- Ollama/Gemma for LLM (same as Nancy)

This creates an apples-to-apples comparison with Nancy's Four-Brain architecture.
"""

import os
import time
import hashlib
from pathlib import Path
from typing import List, Dict, Any, Optional
from fastapi import FastAPI, UploadFile, File, HTTPException
from pydantic import BaseModel
import uvicorn
import pandas as pd

# LangChain imports - using simpler approach
from langchain.schema import Document
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.prompts import PromptTemplate
from langchain.llms.base import LLM
import requests

# Direct imports for vector operations
import chromadb
from fastembed import TextEmbedding

app = FastAPI(title="Baseline RAG System", version="1.0.0")

def textify_spreadsheet(file_path: Path) -> List[str]:
    """
    Convert spreadsheet rows into coherent sentences for text-based RAG processing.
    
    This implements "textification" - converting tabular data into natural language
    sentences that can be embedded and searched using standard RAG techniques.
    
    Args:
        file_path: Path to CSV or Excel file
        
    Returns:
        List of natural language sentences representing spreadsheet content
    """
    sentences = []
    
    try:
        # Determine file type and read accordingly
        if file_path.suffix.lower() == '.csv':
            df = pd.read_csv(file_path)
            sheet_name = "CSV"
        elif file_path.suffix.lower() in ['.xlsx', '.xls']:
            # For Excel files, process all sheets
            excel_file = pd.ExcelFile(file_path)
            for sheet_name in excel_file.sheet_names:
                df = pd.read_excel(file_path, sheet_name=sheet_name)
                sheet_sentences = _convert_dataframe_to_sentences(df, file_path.name, sheet_name)
                sentences.extend(sheet_sentences)
            return sentences
        else:
            return []
        
        # For CSV files, process single dataframe
        sheet_sentences = _convert_dataframe_to_sentences(df, file_path.name, sheet_name)
        sentences.extend(sheet_sentences)
        
    except Exception as e:
        print(f"Error processing spreadsheet {file_path}: {e}")
        # Return basic file info even if processing fails
        sentences.append(f"Spreadsheet file {file_path.name} could not be processed: {str(e)}")
    
    return sentences

def _convert_dataframe_to_sentences(df: pd.DataFrame, filename: str, sheet_name: str) -> List[str]:
    """
    Convert a pandas DataFrame into natural language sentences.
    
    Each row becomes a sentence with column headers as descriptive labels.
    """
    sentences = []
    
    # Add header information
    if len(df.columns) > 0:
        column_names = ", ".join(df.columns.tolist())
        sentences.append(f"Spreadsheet {filename} sheet {sheet_name} contains columns: {column_names}.")
    
    # Convert each row to a sentence
    for row_idx, row in df.iterrows():
        sentence_parts = []
        
        for col, value in row.items():
            if pd.notna(value) and str(value).strip():  # Skip empty/null values
                # Clean column name and value for readability
                clean_col = str(col).strip().replace('_', ' ').replace('-', ' ')
                clean_value = str(value).strip()
                sentence_parts.append(f"{clean_col} is {clean_value}")
        
        if sentence_parts:  # Only create sentence if there's content
            # Add context about source
            sentence = f"In {filename} sheet {sheet_name} row {row_idx + 1}: " + ", ".join(sentence_parts) + "."
            sentences.append(sentence)
    
    # Add summary information
    sentences.append(f"Spreadsheet {filename} sheet {sheet_name} contains {len(df)} rows and {len(df.columns)} columns.")
    
    return sentences

class Gemma3BaselineLLM(LLM):
    """Custom LangChain LLM wrapper for Gemma 3 1B via Google AI API for baseline"""
    
    def __init__(self):
        super().__init__()
        # Check API key availability but don't store as field to avoid Pydantic validation
        api_key = os.getenv("GEMINI_API_KEY")
        if not api_key:
            raise ValueError("GEMINI_API_KEY environment variable required")
    
    def _get_api_key(self):
        """Get API key when needed"""
        return os.getenv("GEMINI_API_KEY")
    
    @property
    def _llm_type(self) -> str:
        return "gemma-3n-e4b-it-baseline"
    
    def _call(self, prompt: str, stop: Optional[List[str]] = None, **kwargs) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/gemma-3n-e4b-it:generateContent?key={self._get_api_key()}"
        
        data = {
            "contents": [{
                "parts": [{"text": prompt}]
            }]
        }
        
        try:
            response = requests.post(url, json=data, timeout=30)
            response.raise_for_status()
            result = response.json()
            return result["candidates"][0]["content"]["parts"][0]["text"]
        except Exception as e:
            return f"Error calling Gemma 3: {str(e)}"

class QueryRequest(BaseModel):
    query: str

class QueryResponse(BaseModel):
    response: str
    sources: List[str]
    query_time: float
    method: str = "langchain_rag"

class BaselineRAGSystem:
    """Standard LangChain + ChromaDB RAG implementation"""
    
    def __init__(self, 
                 chroma_host: str = None,
                 chroma_port: int = None,
                 chunk_size: int = 500,
                 chunk_overlap: int = 50):
        
        # Use environment variables or defaults
        chroma_host = chroma_host or os.getenv("CHROMA_HOST", "localhost")
        chroma_port = chroma_port or int(os.getenv("CHROMA_PORT", "8001"))
        
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        
        # Initialize embedding model (same as Nancy)
        print("Initializing FastEmbed embeddings...")
        self.embeddings = TextEmbedding(
            model_name="BAAI/bge-small-en-v1.5"
        )
        
        # Initialize text splitter
        self.text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=chunk_size,
            chunk_overlap=chunk_overlap,
            length_function=len,
            separators=["\n\n", "\n", " ", ""]
        )
        
        # Initialize LLM (Gemma 3 1B via Google AI API)
        print("Initializing Gemma 3 1B LLM via Google AI API...")
        self.llm = Gemma3BaselineLLM()
        
        # Initialize ChromaDB client
        print("Connecting to ChromaDB...")
        self.chroma_client = chromadb.HttpClient(host=chroma_host, port=chroma_port)
        
        # Initialize collection - use get_or_create
        collection_name = "baseline_rag"
        try:
            self.collection = self.chroma_client.get_or_create_collection(
                name=collection_name,
                metadata={"description": "Baseline RAG system collection"}
            )
            print(f"Initialized '{collection_name}' collection")
            
        except Exception as e:
            print(f"Failed to initialize collection: {e}")
            # If get_or_create fails, try simpler approach
            try:
                self.collection = self.chroma_client.get_or_create_collection(collection_name)
                print(f"Initialized '{collection_name}' collection (simple)")
            except Exception as e2:
                print(f"Failed simple initialization: {e2}")
                raise e2
        
        print("Baseline RAG system initialized successfully!")
    
    def create_rag_prompt(self, context: str, question: str) -> str:
        """Create RAG prompt template"""
        return f"""You are a helpful assistant that answers questions based on the provided context. 
        Use only the information from the context to answer the question. If the context doesn't contain 
        enough information to answer the question, say so clearly.

        Context:
        {context}

        Question: {question}

        Answer:"""
    
    def ingest_documents(self, data_dir: str = "benchmark_data") -> Dict[str, Any]:
        """Ingest documents using standard LangChain approach with spreadsheet support"""
        start_time = time.time()
        
        documents = []
        processed_files = []
        spreadsheet_files = []
        
        # Load text documents
        for file_path in Path(data_dir).glob("*.txt"):
            print(f"Processing text file {file_path.name}...")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Create document with minimal metadata (no author info like Nancy has)
            doc = Document(
                page_content=content,
                metadata={
                    "filename": file_path.name,
                    "source": str(file_path),
                    "file_type": "text"
                }
            )
            documents.append(doc)
            processed_files.append(file_path.name)
        
        # Load and process spreadsheet files (CSV and Excel)
        spreadsheet_patterns = ["*.csv", "*.xlsx", "*.xls"]
        for pattern in spreadsheet_patterns:
            for file_path in Path(data_dir).glob(pattern):
                print(f"Processing spreadsheet file {file_path.name}...")
                
                try:
                    # Convert spreadsheet to natural language sentences
                    sentences = textify_spreadsheet(file_path)
                    
                    if sentences:
                        # Create document from concatenated sentences
                        content = "\n\n".join(sentences)
                        
                        doc = Document(
                            page_content=content,
                            metadata={
                                "filename": file_path.name,
                                "source": str(file_path),
                                "file_type": "spreadsheet",
                                "original_format": file_path.suffix.lower()
                            }
                        )
                        documents.append(doc)
                        processed_files.append(file_path.name)
                        spreadsheet_files.append(file_path.name)
                        print(f"  Converted {file_path.name} to {len(sentences)} text sentences")
                    
                except Exception as e:
                    print(f"Error processing spreadsheet {file_path.name}: {e}")
                    # Still track it as processed but note the error
                    processed_files.append(f"{file_path.name} (error)")
        
        print(f"Processed {len(processed_files)} files total, including {len(spreadsheet_files)} spreadsheets")
        
        # Split documents into chunks
        print("Splitting documents into chunks...")
        texts = self.text_splitter.split_documents(documents)
        
        # Store in ChromaDB directly
        print(f"Adding {len(texts)} chunks to ChromaDB...")
        embeddings_list = list(self.embeddings.embed([doc.page_content for doc in texts]))
        
        self.collection.upsert(
            documents=[doc.page_content for doc in texts],
            metadatas=[doc.metadata for doc in texts],
            ids=[f"doc_{i}" for i in range(len(texts))],
            embeddings=embeddings_list
        )
        
        processing_time = time.time() - start_time
        
        return {
            "files_processed": len(processed_files),
            "text_files": len(processed_files) - len(spreadsheet_files),
            "spreadsheet_files": len(spreadsheet_files),
            "chunks_created": len(texts),
            "processing_time": processing_time,
            "files": processed_files,
            "spreadsheet_files_list": spreadsheet_files
        }
    
    def query(self, question: str) -> QueryResponse:
        """Process query using standard RAG approach"""
        start_time = time.time()
        
        try:
            # Generate query embedding
            query_embedding = list(self.embeddings.embed([question]))[0]
            
            # Retrieve relevant chunks
            results = self.collection.query(
                query_embeddings=[query_embedding],
                n_results=5
            )
            
            # Build context from retrieved chunks
            context_parts = []
            sources = set()
            
            if results['documents'] and results['documents'][0]:
                for i, doc in enumerate(results['documents'][0]):
                    filename = results['metadatas'][0][i].get('filename', 'unknown')
                    sources.add(filename)
                    context_parts.append(f"From {filename}: {doc}")
            
            context = '\n\n'.join(context_parts)
            
            # Generate response using LLM
            prompt = self.create_rag_prompt(context, question)
            response = self.llm.invoke(prompt)
            
            query_time = time.time() - start_time
            
            return QueryResponse(
                response=response,
                sources=list(sources),
                query_time=query_time
            )
            
        except Exception as e:
            query_time = time.time() - start_time
            return QueryResponse(
                response=f"Error processing query: {str(e)}",
                sources=[],
                query_time=query_time
            )

# Global RAG system instance
rag_system: Optional[BaselineRAGSystem] = None

@app.on_event("startup")
async def startup_event():
    """Initialize the RAG system on startup"""
    global rag_system
    try:
        rag_system = BaselineRAGSystem()
    except Exception as e:
        print(f"Failed to initialize RAG system: {e}")
        # Don't fail startup, but system won't work

@app.get("/health")
async def health_check():
    """Health check endpoint"""
    return {
        "status": "ok",
        "system": "baseline-rag",
        "rag_initialized": rag_system is not None
    }

@app.post("/api/ingest")
async def ingest_documents():
    """Ingest documents endpoint (processes benchmark_data directory)"""
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG system not initialized")
    
    try:
        result = rag_system.ingest_documents()
        return {
            "status": "success",
            "message": f"Ingested {result['files_processed']} files",
            "details": result
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Ingestion failed: {str(e)}")

@app.post("/api/query", response_model=QueryResponse)
async def query_documents(request: QueryRequest):
    """Query documents endpoint"""
    if not rag_system:
        raise HTTPException(status_code=500, detail="RAG system not initialized")
    
    return rag_system.query(request.query)

@app.get("/api/info")
async def system_info():
    """Get system information"""
    return {
        "system": "Baseline RAG",
        "framework": "LangChain",
        "vector_store": "ChromaDB",
        "llm": "Ollama/Gemma2:2b", 
        "embeddings": "FastEmbed/BAAI/bge-small-en-v1.5",
        "description": "Standard LangChain + ChromaDB RAG implementation for comparison with Nancy"
    }

if __name__ == "__main__":
    # For development - run with uvicorn
    uvicorn.run(
        "main:app",
        host="0.0.0.0",
        port=8002,  # Different port from Nancy (8000) and ChromaDB (8001)
        reload=True
    )