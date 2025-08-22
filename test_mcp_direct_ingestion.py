#!/usr/bin/env python3
"""
Test direct ingestion to Nancy API to isolate the issue
"""

import json
import requests
import hashlib
from datetime import datetime

NANCY_API_BASE = "http://localhost:8000"

def test_direct_knowledge_packet_ingestion():
    """Test posting a knowledge packet directly to Nancy API"""
    
    # Create the same packet that nancy-memory MCP server creates
    content = "This is a test message to validate the knowledge packet schema."
    filename = "test_validation_direct.txt"
    author = "Test Engineer Direct"
    content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    # Build content for different brains
    packet_content = {
        "vector_data": {
            "chunks": [{
                "chunk_id": f"{filename}_chunk_0",
                "text": content,
                "chunk_metadata": {
                    "chunk_index": 0,
                    "source_file": filename
                }
            }],
            "embedding_model": "BAAI/bge-small-en-v1.5",
            "chunk_strategy": "document_structure",
            "chunk_size": len(content),
            "chunk_overlap": 0
        }
    }
    
    packet_data = {
        "packet_version": "1.0",
        "packet_id": content_hash,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": {
            "mcp_server": "nancy-memory",
            "server_version": "1.0.0",
            "original_location": filename,
            "content_type": "document",
            "extraction_method": "mcp_direct_ingestion"
        },
        "metadata": {
            "title": filename,
            "author": author,
            "created_at": datetime.utcnow().isoformat() + "Z",
            "content_hash": content_hash,
            "file_size": len(content.encode('utf-8')),
            "tags": ["test", "mcp_ingested"],
            "classification": "internal",
            "language": "en"
        },
        "content": packet_content,
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
    
    print("Sending knowledge packet to Nancy API...")
    print(f"Packet ID: {packet_data['packet_id']}")
    print(f"Source: {packet_data['source']}")
    print()
    
    try:
        # Test Nancy health first
        health_response = requests.get(f"{NANCY_API_BASE}/health", timeout=10)
        print(f"Nancy health status: {health_response.status_code}")
        if health_response.status_code == 200:
            health_data = health_response.json()
            print(f"Nancy mode: {health_data.get('nancy_core', {}).get('migration_mode', 'unknown')}")
        print()
        
        # Send the knowledge packet
        response = requests.post(
            f"{NANCY_API_BASE}/api/ingest/knowledge-packet",
            json=packet_data,
            timeout=30
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        print(f"Response content: {response.text}")
        
        if response.status_code == 200:
            result = response.json()
            print("\nSUCCESS: Knowledge packet ingested successfully!")
            print(f"Result: {json.dumps(result, indent=2)}")
            return True
        else:
            print(f"\nFAILED: Knowledge packet ingestion failed")
            print(f"Status: {response.status_code}")
            print(f"Error: {response.text}")
            return False
            
    except Exception as e:
        print(f"EXCEPTION: {e}")
        return False

def test_query_after_ingestion():
    """Test querying after successful ingestion"""
    
    query_data = {
        "query": "test message validate schema",
        "n_results": 5,
        "orchestrator": "intelligent"
    }
    
    try:
        response = requests.post(
            f"{NANCY_API_BASE}/api/query",
            json=query_data,
            timeout=60
        )
        
        print(f"\nQuery response status: {response.status_code}")
        
        if response.status_code == 200:
            result = response.json()
            print("Query successful!")
            print(f"Response: {result.get('response', 'No response')}")
            print(f"Sources: {len(result.get('sources', []))} sources found")
            return True
        else:
            print(f"Query failed: {response.text}")
            return False
            
    except Exception as e:
        print(f"Query exception: {e}")
        return False

if __name__ == "__main__":
    print("Testing Direct Knowledge Packet Ingestion\n")
    
    # Test ingestion
    ingestion_success = test_direct_knowledge_packet_ingestion()
    
    # Test query if ingestion succeeded
    if ingestion_success:
        query_success = test_query_after_ingestion()
        
        print("\n" + "="*50)
        print("Summary:")
        print(f"Ingestion: {'PASSED' if ingestion_success else 'FAILED'}")
        print(f"Query: {'PASSED' if query_success else 'FAILED'}")
    else:
        print("\nSkipping query test due to ingestion failure")