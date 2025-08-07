#!/usr/bin/env python3
"""
Simple ChromaDB functionality test without Unicode issues
"""

import time
import chromadb
import requests

def test_chromadb_vs_nancy():
    """Test ChromaDB direct vs Nancy with the same query"""
    
    print("CHROMADB vs NANCY COMPARISON")
    print("="*50)
    
    # Initialize ChromaDB client (same as Nancy uses)
    client = chromadb.HttpClient(host="localhost", port=8001)
    
    # Test connection
    try:
        collections = client.list_collections()
        print(f"ChromaDB connected. Found {len(collections)} collections:")
        for collection in collections:
            print(f"  - {collection.name}")
    except Exception as e:
        print(f"ChromaDB connection failed: {e}")
        return
    
    # Get Nancy's collection
    try:
        collection = client.get_collection("nancy_documents")
        print(f"Successfully accessed 'nancy_documents' collection")
    except Exception as e:
        print(f"Cannot access nancy_documents collection: {e}")
        return
    
    # Test query
    query = "Who wrote the thermal analysis report?"
    print(f"\nTesting query: {query}")
    print("-" * 50)
    
    # 1. ChromaDB Direct
    print("1. ChromaDB Direct:")
    start_time = time.time()
    try:
        results = collection.query(
            query_texts=[query],
            n_results=5
        )
        response_time = time.time() - start_time
        
        num_results = len(results["documents"][0]) if results["documents"] else 0
        print(f"   SUCCESS: {num_results} results in {response_time:.3f}s")
        
        # Show results
        if num_results > 0:
            for i, (doc, distance) in enumerate(zip(results["documents"][0][:3], results["distances"][0][:3])):
                print(f"   Result {i+1} (dist: {distance:.3f}): {doc[:80]}...")
                
    except Exception as e:
        print(f"   FAILED: {e}")
    
    # 2. Nancy Four-Brain
    print("\n2. Nancy Four-Brain:")
    start_time = time.time()
    try:
        response = requests.post(
            "http://localhost:8000/api/query",
            json={"query": query, "n_results": 5, "use_enhanced": True},
            timeout=30
        )
        response_time = time.time() - start_time
        
        if response.status_code == 200:
            nancy_result = response.json()
            num_results = len(nancy_result.get("results", []))
            strategy = nancy_result.get("strategy_used", "unknown")
            print(f"   SUCCESS: {num_results} results in {response_time:.3f}s")
            print(f"   Strategy: {strategy}")
            
            # Show results
            for i, result in enumerate(nancy_result.get("results", [])[:3]):
                text = result.get("text", "")
                distance = result.get("distance", "N/A") 
                filename = result.get("document_metadata", {}).get("filename", "unknown")
                print(f"   Result {i+1} (dist: {distance}, file: {filename}): {text[:60]}...")
        else:
            print(f"   FAILED: HTTP {response.status_code}")
            
    except Exception as e:
        print(f"   FAILED: {e}")
    
    print("\n" + "="*50)
    print("CONCLUSION:")
    print("Both systems should now be functional for fair comparison")

if __name__ == "__main__":
    test_chromadb_vs_nancy()