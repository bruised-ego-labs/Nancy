#!/usr/bin/env python3
"""
Debug the nancy-memory MCP server request to see the exact issue
"""

import json
import requests
import hashlib
from datetime import datetime

NANCY_API_BASE = "http://localhost:8000"

def debug_mcp_server_request():
    """Debug what the MCP server is actually sending"""
    
    # Exactly replicate what the nancy-memory server does
    content = "This is a test message to validate the knowledge packet schema."
    content_type = "test"
    author = "Test Engineer"
    filename = "test_validation.txt"
    metadata = None
    
    try:
        # Check Nancy's current mode to determine ingestion strategy
        health_response = requests.get(f"{NANCY_API_BASE}/health", timeout=10)
        nancy_mode = "unknown"
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            nancy_mode = health_data.get("nancy_core", {}).get("migration_mode", "unknown")
            print(f"Nancy mode detected: {nancy_mode}")
        
        if nancy_mode == "mcp":
            # Use Knowledge Packet ingestion for MCP mode
            # Create proper knowledge packet matching schema
            filename_final = filename or f"memory_{content_type}_{len(content)}.txt"
            content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
            
            # Build content for different brains
            packet_content = {
                "vector_data": {
                    "chunks": [{
                        "chunk_id": f"{filename_final}_chunk_0",
                        "text": content,
                        "chunk_metadata": {
                            "chunk_index": 0,
                            "source_file": filename_final
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
                    "original_location": filename_final,
                    "content_type": "document",
                    "extraction_method": "mcp_direct_ingestion"
                },
                "metadata": {
                    "title": filename_final,
                    "author": author,
                    "created_at": datetime.utcnow().isoformat() + "Z",
                    "content_hash": content_hash,
                    "file_size": len(content.encode('utf-8')),
                    "tags": [content_type, "mcp_ingested"],
                    "classification": "internal",
                    "language": "en",
                    **(metadata or {})
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
            
            print("Packet data being sent:")
            print(json.dumps(packet_data, indent=2))
            print()
            
            print("Sending request to Nancy API...")
            response = requests.post(
                f"{NANCY_API_BASE}/api/ingest/knowledge-packet",
                json=packet_data,
                timeout=30
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                print(f"SUCCESS - Stored: {content[:50]}...")
                
                # Handle different response formats
                doc_id = result.get("packet_id") or result.get("doc_id")
                ingestion_mode = "Knowledge Packet"
                
                return {
                    "status": "success",
                    "message": f"Information stored in Nancy's persistent memory via {ingestion_mode} ingestion",
                    "doc_id": doc_id,
                    "nancy_mode": nancy_mode,
                    "details": f"Stored {len(content)} characters as {content_type}"
                }
            else:
                print(f"FAILED - Nancy ingestion failed: {response.status_code} {response.text}")
                return {
                    "status": "error",
                    "message": f"Failed to store information: {response.text}",
                    "details": "Nancy ingestion endpoint returned an error"
                }
                
    except Exception as e:
        print(f"EXCEPTION - Ingestion error: {e}")
        return {
            "status": "error", 
            "message": f"Failed to store information: {str(e)}",
            "details": "Connection or processing error"
        }

def test_with_requests_session():
    """Test with a requests session to see if there are connection issues"""
    
    session = requests.Session()
    session.headers.update({
        'Content-Type': 'application/json',
        'Accept': 'application/json'
    })
    
    # Create minimal packet
    content = "Test with session"
    content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    packet_data = {
        "packet_version": "1.0",
        "packet_id": content_hash,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": {
            "mcp_server": "nancy-memory",
            "server_version": "1.0.0",
            "original_location": "session_test.txt",
            "content_type": "document"
        },
        "metadata": {
            "title": "Session Test"
        },
        "content": {}
    }
    
    print("\nTesting with requests session...")
    print(f"Headers: {dict(session.headers)}")
    
    try:
        response = session.post(
            f"{NANCY_API_BASE}/api/ingest/knowledge-packet",
            json=packet_data,
            timeout=30
        )
        
        print(f"Session response status: {response.status_code}")
        print(f"Session response: {response.text}")
        
        return response.status_code == 200
        
    except Exception as e:
        print(f"Session exception: {e}")
        return False

if __name__ == "__main__":
    print("Debugging Nancy Memory MCP Server Request\n")
    
    # Test the exact MCP server logic
    result = debug_mcp_server_request()
    print(f"\nMCP server simulation result: {json.dumps(result, indent=2)}")
    
    # Test with session
    session_success = test_with_requests_session()
    print(f"\nSession test: {'PASSED' if session_success else 'FAILED'}")