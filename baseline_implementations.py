#!/usr/bin/env python3
"""
Baseline system implementations for Nancy benchmark comparison

Implements actual baseline systems that can be compared against Nancy:
- Vector-only search (ChromaDB)
- Simple file search (grep-based)
- Basic RAG (LangChain + vector store)
- Traditional wiki/search systems simulation
"""

import asyncio
import json
import time
import os
import subprocess
import requests
from typing import Dict, List, Any, Optional
from pathlib import Path
import sqlite3
import chromadb
from dataclasses import dataclass

@dataclass
class BaselineResult:
    """Standard result format for all baseline systems"""
    system_name: str
    query: str
    results: List[Dict[str, Any]]
    response_time: float
    metadata: Dict[str, Any]

class VectorOnlyBaseline:
    """Pure vector search using ChromaDB without LLM analysis"""
    
    def __init__(self, chromadb_endpoint: str = "http://localhost:8001"):
        self.endpoint = chromadb_endpoint
        self.client = chromadb.HttpClient(host="localhost", port=8001)
        
    def setup(self, documents: List[Dict[str, Any]]):
        """Initialize vector database with documents"""
        try:
            # Create or get collection
            collection = self.client.get_or_create_collection(
                name="baseline_vector",
                metadata={"description": "Baseline vector-only collection"}
            )
            
            # Add documents
            texts = [doc["content"] for doc in documents]
            metadatas = [{"filename": doc["filename"], "author": doc["author"]} for doc in documents]
            ids = [f"doc_{i}" for i in range(len(documents))]
            
            collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            return True
        except Exception as e:
            print(f"VectorOnlyBaseline setup failed: {e}")
            return False
    
    def query(self, query_text: str, n_results: int = 5) -> BaselineResult:
        """Execute vector-only query"""
        start_time = time.time()
        
        try:
            collection = self.client.get_collection("baseline_vector")
            results = collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            # Format results
            formatted_results = []
            if results["documents"] and results["documents"][0]:
                for i, doc in enumerate(results["documents"][0]):
                    formatted_results.append({
                        "text": doc,
                        "metadata": results["metadatas"][0][i] if results["metadatas"] else {},
                        "distance": results["distances"][0][i] if results["distances"] else None
                    })
            
            response_time = time.time() - start_time
            
            return BaselineResult(
                system_name="vector_only",
                query=query_text,
                results=formatted_results,
                response_time=response_time,
                metadata={
                    "collection_size": collection.count(),
                    "search_method": "vector_similarity"
                }
            )
            
        except Exception as e:
            return BaselineResult(
                system_name="vector_only",
                query=query_text,
                results=[],
                response_time=time.time() - start_time,
                metadata={"error": str(e)}
            )

class SimpleSearchBaseline:
    """Basic file system search using grep and text matching"""
    
    def __init__(self, data_directory: Path):
        self.data_dir = data_directory
        
    def setup(self, documents: List[Dict[str, Any]]):
        """Write documents to files for grep searching"""
        try:
            self.data_dir.mkdir(exist_ok=True)
            
            for doc in documents:
                file_path = self.data_dir / doc["filename"]
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Author: {doc['author']}\n")
                    f.write(f"Filename: {doc['filename']}\n")
                    f.write("---\n")
                    f.write(doc["content"])
            
            return True
        except Exception as e:
            print(f"SimpleSearchBaseline setup failed: {e}")
            return False
    
    def query(self, query_text: str, n_results: int = 5) -> BaselineResult:
        """Execute grep-based text search"""
        start_time = time.time()
        
        try:
            # Extract search terms from query
            search_terms = [term.lower() for term in query_text.split() if len(term) > 2]
            results = []
            
            # Search each file
            for file_path in self.data_dir.glob("*.txt"):
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read().lower()
                        
                    # Count term matches
                    matches = sum(1 for term in search_terms if term in content)
                    
                    if matches > 0:
                        # Read original content for result
                        with open(file_path, 'r', encoding='utf-8') as f:
                            full_content = f.read()
                            
                        # Extract relevant snippet around matches
                        snippet = self._extract_snippet(full_content, search_terms)
                        
                        results.append({
                            "text": snippet,
                            "metadata": {
                                "filename": file_path.name,
                                "matches": matches,
                                "match_score": matches / len(search_terms)
                            },
                            "distance": 1.0 - (matches / len(search_terms))  # Lower is better
                        })
                        
                except Exception as e:
                    continue
            
            # Sort by match score
            results.sort(key=lambda x: x["distance"])
            results = results[:n_results]
            
            response_time = time.time() - start_time
            
            return BaselineResult(
                system_name="simple_search",
                query=query_text,
                results=results,
                response_time=response_time,
                metadata={
                    "search_terms": search_terms,
                    "files_searched": len(list(self.data_dir.glob("*.txt"))),
                    "search_method": "grep_simulation"
                }
            )
            
        except Exception as e:
            return BaselineResult(
                system_name="simple_search",
                query=query_text,
                results=[],
                response_time=time.time() - start_time,
                metadata={"error": str(e)}
            )
    
    def _extract_snippet(self, content: str, search_terms: List[str], snippet_length: int = 200) -> str:
        """Extract relevant snippet around search terms"""
        content_lower = content.lower()
        
        # Find first occurrence of any search term
        first_match_pos = len(content)
        for term in search_terms:
            pos = content_lower.find(term)
            if pos != -1 and pos < first_match_pos:
                first_match_pos = pos
        
        if first_match_pos == len(content):
            # No matches found, return beginning
            return content[:snippet_length] + "..."
        
        # Extract snippet around match
        start = max(0, first_match_pos - snippet_length // 2)
        end = min(len(content), first_match_pos + snippet_length // 2)
        
        snippet = content[start:end]
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
            
        return snippet

class BasicRAGBaseline:
    """Standard RAG implementation using vector retrieval + LLM generation"""
    
    def __init__(self, vector_endpoint: str = "http://localhost:8001", llm_endpoint: str = "http://localhost:11434"):
        self.vector_endpoint = vector_endpoint
        self.llm_endpoint = llm_endpoint
        self.client = chromadb.HttpClient(host="localhost", port=8001)
        
    def setup(self, documents: List[Dict[str, Any]]):
        """Setup vector store for RAG"""
        try:
            collection = self.client.get_or_create_collection(
                name="baseline_rag",
                metadata={"description": "Baseline RAG collection"}
            )
            
            texts = [doc["content"] for doc in documents]
            metadatas = [{"filename": doc["filename"], "author": doc["author"]} for doc in documents]
            ids = [f"rag_doc_{i}" for i in range(len(documents))]
            
            collection.add(
                documents=texts,
                metadatas=metadatas,
                ids=ids
            )
            
            return True
        except Exception as e:
            print(f"BasicRAGBaseline setup failed: {e}")
            return False
    
    def query(self, query_text: str, n_results: int = 3) -> BaselineResult:
        """Execute RAG query: retrieve + generate"""
        start_time = time.time()
        
        try:
            # Step 1: Retrieve relevant documents
            collection = self.client.get_collection("baseline_rag")
            retrieval_results = collection.query(
                query_texts=[query_text],
                n_results=n_results
            )
            
            # Step 2: Prepare context for LLM
            context_docs = []
            if retrieval_results["documents"] and retrieval_results["documents"][0]:
                for i, doc in enumerate(retrieval_results["documents"][0]):
                    metadata = retrieval_results["metadatas"][0][i] if retrieval_results["metadatas"] else {}
                    context_docs.append(f"Document {i+1} ({metadata.get('filename', 'unknown')}):\n{doc}\n")
            
            context = "\n".join(context_docs)
            
            # Step 3: Generate response using LLM
            llm_response = self._generate_response(query_text, context)
            
            # Format results
            results = []
            if retrieval_results["documents"] and retrieval_results["documents"][0]:
                for i, doc in enumerate(retrieval_results["documents"][0]):
                    results.append({
                        "text": doc,
                        "metadata": retrieval_results["metadatas"][0][i] if retrieval_results["metadatas"] else {},
                        "distance": retrieval_results["distances"][0][i] if retrieval_results["distances"] else None
                    })
            
            response_time = time.time() - start_time
            
            return BaselineResult(
                system_name="basic_rag",
                query=query_text,
                results=results,
                response_time=response_time,
                metadata={
                    "context_length": len(context),
                    "llm_response": llm_response,
                    "retrieval_count": len(results),
                    "search_method": "vector_retrieval_plus_generation"
                }
            )
            
        except Exception as e:
            return BaselineResult(
                system_name="basic_rag",
                query=query_text,
                results=[],
                response_time=time.time() - start_time,
                metadata={"error": str(e)}
            )
    
    def _generate_response(self, query: str, context: str) -> str:
        """Generate response using local LLM"""
        try:
            prompt = f"""Based on the following context documents, answer the question: {query}

Context:
{context}

Answer:"""

            response = requests.post(
                f"{self.llm_endpoint}/api/generate",
                json={
                    "model": "gemma:2b",
                    "prompt": prompt,
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                return response.json().get("response", "No response generated")
            else:
                return f"LLM generation failed: {response.status_code}"
                
        except Exception as e:
            return f"LLM generation error: {e}"

class WikiSearchBaseline:
    """Simulates traditional wiki/confluence search behavior"""
    
    def __init__(self, data_directory: Path):
        self.data_dir = data_directory
        self.index = {}  # Simple inverted index
        
    def setup(self, documents: List[Dict[str, Any]]):
        """Build simple inverted index"""
        try:
            self.data_dir.mkdir(exist_ok=True)
            
            # Write documents and build index
            for i, doc in enumerate(documents):
                doc_id = f"wiki_doc_{i}"
                file_path = self.data_dir / f"{doc_id}.txt"
                
                with open(file_path, 'w', encoding='utf-8') as f:
                    f.write(f"Title: {doc['filename']}\n")
                    f.write(f"Author: {doc['author']}\n")
                    f.write("---\n")
                    f.write(doc["content"])
                
                # Build inverted index
                words = doc["content"].lower().split()
                for word in words:
                    if len(word) > 2:  # Skip short words
                        if word not in self.index:
                            self.index[word] = []
                        self.index[word].append({
                            "doc_id": doc_id,
                            "filename": doc["filename"],
                            "author": doc["author"]
                        })
            
            return True
        except Exception as e:
            print(f"WikiSearchBaseline setup failed: {e}")
            return False
    
    def query(self, query_text: str, n_results: int = 5) -> BaselineResult:
        """Execute wiki-style search"""
        start_time = time.time()
        
        try:
            query_words = [word.lower() for word in query_text.split() if len(word) > 2]
            doc_scores = {}
            
            # Calculate TF-IDF-like scores
            for word in query_words:
                if word in self.index:
                    for doc_info in self.index[word]:
                        doc_id = doc_info["doc_id"]
                        if doc_id not in doc_scores:
                            doc_scores[doc_id] = {
                                "score": 0,
                                "filename": doc_info["filename"],
                                "author": doc_info["author"]
                            }
                        doc_scores[doc_id]["score"] += 1
            
            # Sort and format results
            sorted_docs = sorted(doc_scores.items(), key=lambda x: x[1]["score"], reverse=True)
            results = []
            
            for doc_id, info in sorted_docs[:n_results]:
                file_path = self.data_dir / f"{doc_id}.txt"
                try:
                    with open(file_path, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    # Extract snippet
                    snippet = self._extract_wiki_snippet(content, query_words)
                    
                    results.append({
                        "text": snippet,
                        "metadata": {
                            "filename": info["filename"],
                            "author": info["author"],
                            "score": info["score"],
                            "match_type": "keyword_frequency"
                        },
                        "distance": 1.0 / (info["score"] + 1)  # Convert score to distance
                    })
                except Exception:
                    continue
            
            response_time = time.time() - start_time
            
            return BaselineResult(
                system_name="wiki_search",
                query=query_text,
                results=results,
                response_time=response_time,
                metadata={
                    "query_words": query_words,
                    "index_size": len(self.index),
                    "search_method": "inverted_index"
                }
            )
            
        except Exception as e:
            return BaselineResult(
                system_name="wiki_search",
                query=query_text,
                results=[],
                response_time=time.time() - start_time,
                metadata={"error": str(e)}
            )
    
    def _extract_wiki_snippet(self, content: str, query_words: List[str], snippet_length: int = 250) -> str:
        """Extract wiki-style snippet with highlighted terms"""
        content_lower = content.lower()
        
        # Find best match location
        best_pos = 0
        max_matches = 0
        
        # Sliding window to find area with most query word matches
        window_size = snippet_length
        for i in range(0, max(1, len(content) - window_size), 50):
            window = content_lower[i:i + window_size]
            matches = sum(1 for word in query_words if word in window)
            if matches > max_matches:
                max_matches = matches
                best_pos = i
        
        # Extract snippet
        start = max(0, best_pos)
        end = min(len(content), start + snippet_length)
        snippet = content[start:end]
        
        if start > 0:
            snippet = "..." + snippet
        if end < len(content):
            snippet = snippet + "..."
            
        return snippet

# Factory function to create baseline systems
def create_baseline_system(system_name: str, config: Dict[str, Any], data_dir: Path):
    """Factory function to create baseline systems"""
    
    if system_name == "vector_only":
        return VectorOnlyBaseline(config.get("endpoint", "http://localhost:8001"))
    elif system_name == "simple_search":
        return SimpleSearchBaseline(data_dir / "simple_search")
    elif system_name == "basic_rag":
        return BasicRAGBaseline(
            config.get("vector_endpoint", "http://localhost:8001"),
            config.get("llm_endpoint", "http://localhost:11434")
        )
    elif system_name == "wiki_search":
        return WikiSearchBaseline(data_dir / "wiki_search")
    else:
        raise ValueError(f"Unknown baseline system: {system_name}")

# Test function
async def test_baselines():
    """Test all baseline implementations"""
    
    # Sample test documents
    test_docs = [
        {
            "filename": "test_doc1.txt",
            "author": "Alice Smith", 
            "content": "This document discusses thermal design considerations for electronic systems. Temperature management is critical for reliability."
        },
        {
            "filename": "test_doc2.txt",
            "author": "Bob Johnson",
            "content": "Electrical power analysis shows that split rail design provides better efficiency. This decision was influenced by thermal constraints."
        }
    ]
    
    data_dir = Path("baseline_test_data")
    config = {"endpoint": "http://localhost:8001"}
    
    systems = ["vector_only", "simple_search", "basic_rag", "wiki_search"]
    test_query = "What are the thermal design considerations?"
    
    for system_name in systems:
        try:
            print(f"\nTesting {system_name}...")
            baseline = create_baseline_system(system_name, config, data_dir)
            
            # Setup
            setup_success = baseline.setup(test_docs)
            print(f"  Setup: {'Success' if setup_success else 'Failed'}")
            
            if setup_success:
                # Query
                result = baseline.query(test_query)
                print(f"  Query time: {result.response_time:.3f}s")
                print(f"  Results: {len(result.results)}")
                print(f"  Metadata: {result.metadata}")
                
        except Exception as e:
            print(f"  Error testing {system_name}: {e}")

if __name__ == "__main__":
    asyncio.run(test_baselines())