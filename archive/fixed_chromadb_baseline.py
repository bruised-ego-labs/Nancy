#!/usr/bin/env python3
"""
Fixed ChromaDB Baseline Test

Uses the same ChromaDB Python client that Nancy uses, ensuring a fair comparison.
"""

import time
import chromadb
from typing import List, Dict, Any

class ProperChromaDBBaseline:
    """ChromaDB baseline using the same client library as Nancy"""
    
    def __init__(self):
        # Use same connection method as Nancy
        self.client = chromadb.HttpClient(host="localhost", port=8001)
        
    def test_connection(self):
        """Test if we can connect to ChromaDB"""
        try:
            # List collections to test connection
            collections = self.client.list_collections()
            print(f"ChromaDB connection successful. Found {len(collections)} collections:")
            for collection in collections:
                print(f"  - {collection.name}")
            return True
        except Exception as e:
            print(f"ChromaDB connection failed: {e}")
            return False
    
    def query_nancy_collection(self, query: str, n_results: int = 5):
        """Query the same collection Nancy uses"""
        start_time = time.time()
        
        try:
            # Try to get Nancy's collection
            collection = self.client.get_collection("nancy_documents")
            
            # Query using the same method Nancy uses
            results = collection.query(
                query_texts=[query],
                n_results=n_results
            )
            
            response_time = time.time() - start_time
            
            return {
                "success": True,
                "response_time": response_time,
                "results_count": len(results["documents"][0]) if results["documents"] else 0,
                "documents": results["documents"][0] if results["documents"] else [],
                "metadatas": results["metadatas"][0] if results["metadatas"] else [],
                "distances": results["distances"][0] if results["distances"] else [],
                "raw_results": results
            }
            
        except Exception as e:
            response_time = time.time() - start_time
            return {
                "success": False,
                "error": str(e),
                "response_time": response_time
            }
    
    def compare_with_nancy(self, query: str):
        """Compare ChromaDB direct results with Nancy's results"""
        
        print(f"\n{'='*60}")
        print(f"COMPARING: {query}")
        print(f"{'='*60}")
        
        # Test ChromaDB direct
        print("1. ChromaDB Direct Query:")
        chroma_result = self.query_nancy_collection(query)
        
        if chroma_result["success"]:
            print(f"   ✓ Success: {chroma_result['results_count']} results in {chroma_result['response_time']:.3f}s")
            
            # Show top results
            for i, (doc, distance) in enumerate(zip(chroma_result["documents"][:3], chroma_result["distances"][:3])):
                print(f"   Result {i+1} (distance: {distance:.3f}): {doc[:100]}...")
        else:
            print(f"   ✗ Failed: {chroma_result['error']}")
        
        # Test Nancy for comparison
        print("\n2. Nancy Four-Brain Query:")
        try:
            import requests
            nancy_response = requests.post(
                "http://localhost:8000/api/query",
                json={"query": query, "n_results": 5, "use_enhanced": True},
                timeout=30
            )
            
            if nancy_response.status_code == 200:
                nancy_result = nancy_response.json()
                print(f"   ✓ Success: {len(nancy_result.get('results', []))} results")
                print(f"   Strategy: {nancy_result.get('strategy_used', 'unknown')}")
                
                # Show top results for comparison
                for i, result in enumerate(nancy_result.get("results", [])[:3]):
                    text = result.get("text", "")
                    distance = result.get("distance", "N/A")
                    print(f"   Result {i+1} (distance: {distance}): {text[:100]}...")
            else:
                print(f"   ✗ Nancy failed: HTTP {nancy_response.status_code}")
                
        except Exception as e:
            print(f"   ✗ Nancy failed: {e}")
        
        return chroma_result

def test_all_systems():
    """Test all systems to ensure functionality"""
    
    print("NANCY SYSTEM FUNCTIONALITY TEST")
    print("="*50)
    
    # Initialize ChromaDB baseline
    baseline = ProperChromaDBBaseline()
    
    # Test connection
    print("1. Testing ChromaDB Connection...")
    connection_ok = baseline.test_connection()
    
    if not connection_ok:
        print("❌ ChromaDB connection failed. Cannot proceed with comparison.")
        return False
    
    # Test queries
    test_queries = [
        "Who wrote the thermal analysis report?",
        "Why was aluminum chosen for the heat sink design?", 
        "Who is the primary expert on thermal design?",
        "How do thermal and electrical design decisions affect each other?"
    ]
    
    all_results = []
    
    for query in test_queries:
        result = baseline.compare_with_nancy(query)
        all_results.append({
            "query": query,
            "chromadb_direct": result
        })
    
    # Summary
    print(f"\n{'='*60}")
    print("SUMMARY")
    print(f"{'='*60}")
    
    chromadb_success_count = sum(1 for r in all_results if r["chromadb_direct"]["success"])
    print(f"ChromaDB Direct: {chromadb_success_count}/{len(test_queries)} queries successful")
    
    if chromadb_success_count > 0:
        avg_time = sum(r["chromadb_direct"]["response_time"] for r in all_results if r["chromadb_direct"]["success"]) / chromadb_success_count
        print(f"Average ChromaDB response time: {avg_time:.3f}s")
    
    return chromadb_success_count == len(test_queries)

if __name__ == "__main__":
    success = test_all_systems()
    if success:
        print("\n✅ All systems functional - ready for fair comparison!")
    else:
        print("\n❌ System issues detected - need to fix before comparison.")