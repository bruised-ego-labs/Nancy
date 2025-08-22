#!/usr/bin/env python3
"""
Test MCP parameter simulation to isolate the issue between MCP protocol and Nancy API
"""

import json
import requests
import hashlib
from datetime import datetime

NANCY_API_BASE = "http://localhost:8000"

def simulate_mcp_call_with_metadata_dict():
    """Test the case where metadata is passed as a dictionary like from MCP client"""
    
    # Simulate the exact parameters that would come from MCP client
    content = "Test message for MCP debugging - this should work now"
    content_type = "test"
    author = "Test Engineer MCP"
    filename = "mcp_debug_test.txt"
    metadata = {"debug": True, "test_run": "2025-08-20"}  # This is a dict
    
    # Replicate the nancy-memory server logic exactly
    try:
        # Check Nancy's current mode to determine ingestion strategy
        health_response = requests.get(f"{NANCY_API_BASE}/health", timeout=10)
        nancy_mode = "unknown"
        
        if health_response.status_code == 200:
            health_data = health_response.json()
            nancy_mode = health_data.get("nancy_core", {}).get("migration_mode", "unknown")
        
        if nancy_mode == "mcp":
            # Use Knowledge Packet ingestion for MCP mode
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
                    **(metadata or {})  # This is where metadata dict is merged
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
            
            print("=== MCP Parameter Simulation Test ===")
            print(f"Input parameters:")
            print(f"  content: {content[:50]}...")
            print(f"  content_type: {content_type}")
            print(f"  author: {author}")
            print(f"  filename: {filename}")
            print(f"  metadata: {metadata}")
            print(f"  metadata type: {type(metadata)}")
            print()
            
            print("Packet data being created:")
            print(f"  packet_version: {packet_data.get('packet_version', 'MISSING!')}")
            print(f"  packet keys: {list(packet_data.keys())}")
            print()
            
            # Test the metadata merge operation specifically
            test_metadata = {
                "title": filename_final,
                "author": author,
                "created_at": datetime.utcnow().isoformat() + "Z",
                "content_hash": content_hash,
                "file_size": len(content.encode('utf-8')),
                "tags": [content_type, "mcp_ingested"],
                "classification": "internal",
                "language": "en",
                **(metadata or {})
            }
            print(f"Merged metadata result: {test_metadata}")
            print(f"Merged metadata type: {type(test_metadata)}")
            print()
            
            response = requests.post(
                f"{NANCY_API_BASE}/api/ingest/knowledge-packet",
                json=packet_data,
                timeout=30
            )
            
            print(f"Response status: {response.status_code}")
            print(f"Response content: {response.text}")
            
            if response.status_code == 200:
                result = response.json()
                return {
                    "status": "success",
                    "message": f"Information stored via MCP parameter simulation",
                    "doc_id": result.get("packet_id"),
                    "details": f"Stored {len(content)} characters as {content_type}"
                }
            else:
                return {
                    "status": "error",
                    "message": f"Failed to store information: {response.text}",
                    "details": "Nancy ingestion endpoint returned an error"
                }
                
    except Exception as e:
        print(f"Exception in MCP simulation: {e}")
        return {
            "status": "error", 
            "message": f"Failed to store information: {str(e)}",
            "details": "Connection or processing error"
        }

def test_with_string_metadata():
    """Test the case where metadata might be passed as a string (JSON serialization issue)"""
    
    # This simulates if the MCP protocol is serializing the metadata parameter incorrectly
    content = "Test with string metadata"
    content_type = "test"
    author = "Test Engineer String"
    filename = "string_metadata_test.txt"
    metadata = '{"debug": true, "test_run": "2025-08-20"}'  # This is a string, not a dict
    
    print("\n=== String Metadata Test ===")
    print(f"Metadata as string: {metadata}")
    print(f"Metadata type: {type(metadata)}")
    
    # Try to parse it as JSON if it's a string
    try:
        if isinstance(metadata, str):
            metadata_parsed = json.loads(metadata)
            print(f"Parsed metadata: {metadata_parsed}")
            print(f"Parsed metadata type: {type(metadata_parsed)}")
        else:
            metadata_parsed = metadata
    except Exception as e:
        print(f"Failed to parse metadata as JSON: {e}")
        metadata_parsed = {}
    
    return metadata_parsed

def test_with_none_metadata():
    """Test the case where metadata is None"""
    
    content = "Test with None metadata"
    content_type = "test"
    author = "Test Engineer None"
    filename = "none_metadata_test.txt"
    metadata = None
    
    print("\n=== None Metadata Test ===")
    print(f"Metadata: {metadata}")
    print(f"Metadata type: {type(metadata)}")
    
    # Test the merge operation
    test_merge = {
        "title": filename,
        "author": author,
        "base": "field",
        **(metadata or {})
    }
    print(f"Merge result with None: {test_merge}")
    
    return True

if __name__ == "__main__":
    print("Testing MCP Parameter Handling\n")
    
    # Test 1: Normal dict metadata (should work)
    result1 = simulate_mcp_call_with_metadata_dict()
    print(f"\nDict metadata result: {json.dumps(result1, indent=2)}")
    
    # Test 2: String metadata (potential MCP serialization issue)
    result2 = test_with_string_metadata()
    print(f"String metadata parsing: {result2}")
    
    # Test 3: None metadata
    result3 = test_with_none_metadata()
    print(f"None metadata test: {result3}")
    
    print("\n" + "="*50)
    print("Summary:")
    print(f"Dict metadata test: {'PASSED' if result1.get('status') == 'success' else 'FAILED'}")
    print(f"String metadata parsing: {'PASSED' if result2 else 'FAILED'}")
    print(f"None metadata handling: {'PASSED' if result3 else 'FAILED'}")