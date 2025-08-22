#!/usr/bin/env python3
"""
Direct test of nancy-memory MCP server functions
"""

import sys
import os
import json
import logging
import hashlib

# Add paths for imports
sys.path.append(os.path.join(os.path.dirname(__file__), 'mcp-servers', 'nancy-memory'))
sys.path.append(os.path.join(os.path.dirname(__file__)))

import requests

logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

def test_nancy_health():
    """Test Nancy health endpoint"""
    print("Testing Nancy health...")
    try:
        response = requests.get("http://localhost:8000/health", timeout=10)
        if response.status_code == 200:
            health_data = response.json()
            print("Nancy health:")
            print(json.dumps(health_data, indent=2))
            return health_data
        else:
            print(f"Nancy health check failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error checking Nancy health: {e}")
        return None

def test_direct_nancy_ingestion():
    """Test direct ingestion through Nancy's API"""
    print("\nTesting direct Nancy ingestion...")
    
    # Generate proper 64-character hex packet ID
    test_content = "This is a direct test of Nancy ingestion from nancy-memory MCP server integration testing."
    packet_id = hashlib.sha256(test_content.encode('utf-8')).hexdigest()
    
    # Test Knowledge Packet ingestion endpoint
    packet_data = {
        "packet_version": "1.0",
        "packet_id": packet_id,
        "timestamp": "2025-08-20T23:50:00Z",
        "source": {
            "mcp_server": "nancy-memory",
            "server_version": "1.0.0",
            "original_location": "test_direct.txt",
            "content_type": "document",
            "extraction_method": "direct_test"
        },
        "metadata": {
            "title": "Direct Test Document",
            "author": "Direct Test User",
            "created_at": "2025-08-20T23:50:00Z",
            "content_hash": packet_id,
            "file_size": len(test_content.encode('utf-8')),
            "tags": ["test", "direct_ingestion"],
            "classification": "internal",
            "language": "en"
        },
        "content": {
            "vector_data": {
                "chunks": [{
                    "chunk_id": "test_chunk_1",
                    "text": test_content,
                    "chunk_metadata": {
                        "chunk_index": 0,
                        "source_file": "test_direct.txt"
                    }
                }],
                "embedding_model": "BAAI/bge-small-en-v1.5",
                "chunk_strategy": "document_structure",
                "chunk_size": len(test_content),
                "chunk_overlap": 0
            }
        },
        "processing_hints": {
            "priority_brain": "vector",
            "semantic_weight": 0.8,
            "relationship_importance": 0.6,
            "requires_expert_routing": False,
            "content_classification": "technical",
            "indexing_priority": "medium"
        },
        "quality_metrics": {
            "extraction_confidence": 1.0,
            "content_completeness": 1.0,
            "text_quality_score": 0.9,
            "metadata_richness": 0.8,
            "processing_errors": []
        }
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/ingest/knowledge-packet",
            json=packet_data,
            timeout=30
        )
        
        if response.status_code == 200:
            result = response.json()
            print("Direct ingestion successful:")
            print(json.dumps(result, indent=2))
            return True
        else:
            print(f"Direct ingestion failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error during direct ingestion: {e}")
        return False

def test_nancy_query():
    """Test Nancy query endpoint"""
    print("\nTesting Nancy query...")
    
    query_data = {
        "query": "direct test nancy ingestion integration",
        "n_results": 5,
        "orchestrator": "intelligent"
    }
    
    try:
        response = requests.post(
            "http://localhost:8000/api/query",
            json=query_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print("Query successful:")
            print(json.dumps(result, indent=2))
            return True
        else:
            print(f"Query failed: {response.status_code}")
            print(f"Response: {response.text}")
            return False
    except Exception as e:
        print(f"Error during query: {e}")
        return False

def test_ingestion_status():
    """Check Nancy's ingestion status"""
    print("\nChecking Nancy ingestion status...")
    
    try:
        response = requests.get("http://localhost:8000/api/ingest/status", timeout=10)
        if response.status_code == 200:
            status_data = response.json()
            print("Ingestion status:")
            print(json.dumps(status_data, indent=2))
            return status_data
        else:
            print(f"Status check failed: {response.status_code}")
            return None
    except Exception as e:
        print(f"Error checking status: {e}")
        return None

def main():
    print("=" * 60)
    print("Nancy Memory Integration Test - Direct API Calls")
    print("=" * 60)
    
    # Test 1: Nancy health
    health_data = test_nancy_health()
    if not health_data:
        print("Nancy is not running or healthy. Stopping test.")
        return False
    
    # Test 2: Direct ingestion
    ingestion_success = test_direct_nancy_ingestion()
    
    # Wait for processing
    if ingestion_success:
        import time
        print("\nWaiting for Nancy to process the content...")
        time.sleep(3)
        
        # Test 3: Check status
        status_data = test_ingestion_status()
        
        # Test 4: Query
        query_success = test_nancy_query()
        
        print("\n" + "=" * 60)
        print("Test Results Summary")
        print("=" * 60)
        print(f"Ingestion: {'+ SUCCESS' if ingestion_success else '- FAILED'}")
        print(f"Query: {'+ SUCCESS' if query_success else '- FAILED'}")
        
        if status_data:
            mcp_metrics = status_data.get('mcp_metrics', {})
            packets_processed = mcp_metrics.get('packets_processed', 0)
            print(f"Packets processed by Nancy: {packets_processed}")
        
        return ingestion_success and query_success
    else:
        print("Ingestion failed, skipping other tests.")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)