#!/usr/bin/env python3
"""
Simple Baseline RAG System for Performance Comparison

This implements a basic RAG (Retrieval Augmented Generation) approach using:
- Simple text chunking
- Basic vector embeddings  
- Direct LLM query without multi-brain orchestration
"""

import os
import time
import json
import hashlib
from typing import List, Dict, Any
from pathlib import Path
import requests
import chromadb
from fastembed import TextEmbedding

class SimpleRAGBaseline:
    """Basic RAG implementation for comparison with Nancy's three-brain architecture"""
    
    def __init__(self, chunk_size: int = 500, chunk_overlap: int = 50):
        self.chunk_size = chunk_size
        self.chunk_overlap = chunk_overlap
        self.embedding_model = TextEmbedding(model_name="BAAI/bge-small-en-v1.5")
        self.chromadb_client = chromadb.HttpClient(host="localhost", port=8001)
        self.collection_name = "simple_rag_baseline"
        
        try:
            # Try to get existing collection
            self.collection = self.chromadb_client.get_collection(self.collection_name)
        except:
            # Create new collection if it doesn't exist
            self.collection = self.chromadb_client.create_collection(self.collection_name)
    
    def chunk_text(self, text: str, filename: str) -> List[Dict[str, str]]:
        """Simple text chunking without sophisticated overlap handling"""
        chunks = []
        words = text.split()
        
        for i in range(0, len(words), self.chunk_size - self.chunk_overlap):
            chunk_words = words[i:i + self.chunk_size]
            chunk_text = ' '.join(chunk_words)
            
            chunk_id = f"{filename}_chunk_{i//self.chunk_size}"
            chunks.append({
                "id": chunk_id,
                "text": chunk_text,
                "filename": filename,
                "chunk_index": i // self.chunk_size
            })
        
        return chunks
    
    def ingest_documents(self, data_dir: str = "benchmark_data"):
        """Ingest documents into the simple RAG system"""
        print("Ingesting documents into Simple RAG baseline...")
        
        all_chunks = []
        all_ids = []
        all_metadatas = []
        
        for file_path in Path(data_dir).glob("*.txt"):
            print(f"Processing {file_path.name}...")
            
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            chunks = self.chunk_text(content, file_path.name)
            
            for chunk in chunks:
                all_chunks.append(chunk["text"])
                all_ids.append(chunk["id"])
                all_metadatas.append({
                    "filename": chunk["filename"],
                    "chunk_index": chunk["chunk_index"]
                })
        
        # Generate embeddings
        print("Generating embeddings...")
        embeddings = list(self.embedding_model.embed(all_chunks))
        
        # Store in ChromaDB
        print("Storing in vector database...")
        self.collection.upsert(
            documents=all_chunks,
            metadatas=all_metadatas,
            ids=all_ids,
            embeddings=embeddings
        )
        
        print(f"Ingested {len(all_chunks)} chunks from {len(list(Path(data_dir).glob('*.txt')))} documents")
    
    def query(self, question: str, n_results: int = 5) -> Dict[str, Any]:
        """Simple RAG query without multi-brain orchestration"""
        start_time = time.time()
        
        # Generate query embedding
        query_embedding = list(self.embedding_model.embed([question]))[0]
        
        # Retrieve relevant chunks
        results = self.collection.query(
            query_embeddings=[query_embedding],
            n_results=n_results
        )
        
        # Simple context assembly (just concatenate top chunks)
        context_chunks = []
        for i, doc in enumerate(results['documents'][0]):
            filename = results['metadatas'][0][i]['filename']
            context_chunks.append(f"From {filename}: {doc}")
        
        context = '\n\n'.join(context_chunks)
        
        # Generate response using local LLM (if available) or return context-based response
        response = self._generate_response(question, context)
        
        query_time = time.time() - start_time
        
        return {
            "response": response,
            "context_used": context,
            "source_files": list(set([meta['filename'] for meta in results['metadatas'][0]])),
            "query_time": query_time,
            "num_chunks_retrieved": len(results['documents'][0])
        }
    
    def _generate_response(self, question: str, context: str) -> str:
        """Generate response using available LLM or fallback to context summary"""
        try:
            # Try to use Ollama if available
            response = requests.post(
                "http://localhost:11434/api/generate",
                json={
                    "model": "gemma2:2b",  # Use smaller model for speed
                    "prompt": f"Based on the following context, answer the question concisely:\n\nContext:\n{context}\n\nQuestion: {question}\n\nAnswer:",
                    "stream": False
                },
                timeout=30
            )
            
            if response.status_code == 200:
                result = response.json()
                return result.get('response', 'No response generated')
            else:
                # Fallback to simple context-based response
                return self._simple_context_response(question, context)
        
        except Exception as e:
            print(f"LLM generation failed: {e}")
            return self._simple_context_response(question, context)
    
    def _simple_context_response(self, question: str, context: str) -> str:
        """Fallback: simple context-based response without LLM"""
        # Very basic keyword matching and context extraction
        question_words = set(question.lower().split())
        
        best_match = ""
        best_score = 0
        
        for chunk in context.split('\n\n'):
            chunk_words = set(chunk.lower().split())
            overlap = len(question_words.intersection(chunk_words))
            if overlap > best_score:
                best_score = overlap
                best_match = chunk
        
        return f"Based on the documents: {best_match[:500]}..." if len(best_match) > 500 else f"Based on the documents: {best_match}"


class PerformanceComparison:
    """Compare Nancy three-brain architecture vs simple RAG baseline"""
    
    def __init__(self):
        self.nancy_endpoint = "http://localhost:8000"
        self.simple_rag = SimpleRAGBaseline()
        
    def setup_baseline(self):
        """Setup the simple RAG baseline system"""
        print("Setting up Simple RAG baseline...")
        self.simple_rag.ingest_documents()
        print("Simple RAG baseline ready!")
    
    def get_test_queries(self) -> List[Dict[str, Any]]:
        """Test queries focusing on different complexity levels"""
        return [
            {
                "id": "simple_lookup",
                "query": "What is the thermal analysis about?",
                "category": "basic_lookup",
                "complexity": 1,
                "expected_advantage": "none"
            },
            {
                "id": "author_attribution", 
                "query": "Who wrote the thermal analysis report?",
                "category": "metadata_lookup",
                "complexity": 2,
                "expected_advantage": "nancy_metadata"
            },
            {
                "id": "cross_document",
                "query": "How do the thermal constraints affect the mechanical design?",
                "category": "relationship_analysis",
                "complexity": 3,
                "expected_advantage": "nancy_relationships"
            },
            {
                "id": "decision_tracking",
                "query": "What decisions were made regarding the heat sink design?",
                "category": "decision_analysis", 
                "complexity": 4,
                "expected_advantage": "nancy_graph_brain"
            },
            {
                "id": "expert_identification",
                "query": "Who is the expert on thermal-electrical interfaces?",
                "category": "expertise_mapping",
                "complexity": 4,
                "expected_advantage": "nancy_graph_brain"
            }
        ]
    
    def query_nancy(self, question: str) -> Dict[str, Any]:
        """Query Nancy three-brain system"""
        try:
            start_time = time.time()
            response = requests.post(
                f"{self.nancy_endpoint}/api/query",
                json={"query": question},
                timeout=60
            )
            query_time = time.time() - start_time
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "success": True,
                    "response": result.get("response", ""),
                    "sources": result.get("sources", []),
                    "query_time": query_time,
                    "metadata": result.get("metadata", {})
                }
            else:
                return {
                    "success": False,
                    "error": f"HTTP {response.status_code}",
                    "query_time": query_time
                }
        
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "query_time": 0
            }
    
    def run_comparison(self) -> Dict[str, Any]:
        """Run complete performance comparison"""
        print("Running Nancy vs Simple RAG Performance Comparison")
        print("=" * 60)
        
        results = {
            "timestamp": time.strftime("%Y%m%d_%H%M%S"),
            "test_queries": [],
            "summary": {}
        }
        
        queries = self.get_test_queries()
        nancy_times = []
        baseline_times = []
        nancy_successes = 0
        baseline_successes = 0
        
        for query_info in queries:
            print(f"\nTesting: {query_info['query']}")
            print(f"Category: {query_info['category']} (Complexity: {query_info['complexity']})")
            
            # Test Nancy
            print("  Querying Nancy...")
            nancy_result = self.query_nancy(query_info['query'])
            
            # Test Simple RAG
            print("  Querying Simple RAG...")
            baseline_result = self.simple_rag.query(query_info['query'])
            
            # Record results
            test_result = {
                "query_info": query_info,
                "nancy_result": nancy_result,
                "baseline_result": {
                    "success": True,
                    "response": baseline_result["response"],
                    "sources": baseline_result["source_files"],
                    "query_time": baseline_result["query_time"],
                    "num_chunks": baseline_result["num_chunks_retrieved"]
                },
                "performance_comparison": {
                    "nancy_faster": nancy_result.get("query_time", 999) < baseline_result["query_time"],
                    "time_difference": baseline_result["query_time"] - nancy_result.get("query_time", 999)
                }
            }
            
            results["test_queries"].append(test_result)
            
            # Track metrics
            if nancy_result["success"]:
                nancy_times.append(nancy_result["query_time"])
                nancy_successes += 1
            
            baseline_times.append(baseline_result["query_time"])
            baseline_successes += 1
            
            print(f"  Nancy: {nancy_result['query_time']:.2f}s ({'Success' if nancy_result['success'] else 'Failed'})")
            print(f"  Simple RAG: {baseline_result['query_time']:.2f}s (Success)")
        
        # Calculate summary statistics
        avg_nancy_time = sum(nancy_times) / len(nancy_times) if nancy_times else 0
        avg_baseline_time = sum(baseline_times) / len(baseline_times) if baseline_times else 0
        
        results["summary"] = {
            "total_queries": len(queries),
            "nancy_success_rate": nancy_successes / len(queries),
            "baseline_success_rate": baseline_successes / len(queries), 
            "avg_nancy_time": avg_nancy_time,
            "avg_baseline_time": avg_baseline_time,
            "nancy_faster_count": sum(1 for r in results["test_queries"] if r["performance_comparison"]["nancy_faster"]),
            "speed_advantage": "nancy" if avg_nancy_time < avg_baseline_time else "baseline"
        }
        
        return results
    
    def save_results(self, results: Dict[str, Any], filename: str = None):
        """Save comparison results to file"""
        if filename is None:
            filename = f"performance_comparison_{results['timestamp']}.json"
        
        with open(filename, 'w', encoding='utf-8') as f:
            json.dump(results, f, indent=2, ensure_ascii=False)
        
        print(f"\nResults saved to: {filename}")
    
    def print_summary(self, results: Dict[str, Any]):
        """Print human-readable summary of comparison"""
        summary = results["summary"]
        
        print("\n" + "=" * 60)
        print("PERFORMANCE COMPARISON SUMMARY")
        print("=" * 60)
        print(f"Total Queries Tested: {summary['total_queries']}")
        print(f"Nancy Success Rate: {summary['nancy_success_rate']:.1%}")
        print(f"Simple RAG Success Rate: {summary['baseline_success_rate']:.1%}")
        print()
        print(f"Average Response Times:")
        print(f"  Nancy Three-Brain: {summary['avg_nancy_time']:.2f}s")
        print(f"  Simple RAG: {summary['avg_baseline_time']:.2f}s")
        print(f"  Faster System: {summary['speed_advantage'].title()}")
        print()
        print(f"Nancy Faster on {summary['nancy_faster_count']}/{summary['total_queries']} queries")
        
        print("\nQuery-by-Query Performance:")
        for result in results["test_queries"]:
            query = result["query_info"]["query"][:50] + "..." if len(result["query_info"]["query"]) > 50 else result["query_info"]["query"]
            nancy_time = result["nancy_result"].get("query_time", 999)
            baseline_time = result["baseline_result"]["query_time"] 
            faster = "Nancy" if nancy_time < baseline_time else "Simple RAG"
            
            print(f"  '{query}': Nancy {nancy_time:.2f}s vs Simple RAG {baseline_time:.2f}s → {faster} faster")


if __name__ == "__main__":
    comparison = PerformanceComparison()
    
    # Setup baseline system
    comparison.setup_baseline()
    
    # Run comparison
    results = comparison.run_comparison()
    
    # Save and display results
    comparison.save_results(results)
    comparison.print_summary(results)