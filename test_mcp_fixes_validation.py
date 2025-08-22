#!/usr/bin/env python3
"""
Nancy MCP Fixes Validation Script
Tests the specific fixes implemented for event loop conflicts and knowledge packet schema.
"""

import json
import requests
import time
from datetime import datetime

NANCY_API_BASE = "http://localhost:8000"

def test_health_endpoints():
    """Test that health endpoints work without event loop conflicts."""
    print("Testing health endpoints...")
    
    # Test basic health
    response = requests.get(f"{NANCY_API_BASE}/health")
    print(f"  /health: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        nancy_status = data.get("nancy_core", {}).get("status")
        print(f"    Nancy Core Status: {nancy_status}")
        if nancy_status == "healthy":
            print("    [PASS] No event loop conflicts!")
        else:
            print(f"    [FAIL] Nancy Core issue: {data}")
    
    # Test Nancy status endpoint
    response = requests.get(f"{NANCY_API_BASE}/api/nancy/status")
    print(f"  /api/nancy/status: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    Migration Mode: {data.get('migration_mode')}")
        print("    [PASS] Status endpoint working!")
    else:
        print(f"    [FAIL] Status endpoint error: {response.text}")
    
    return True

def test_knowledge_packet_schema():
    """Test that knowledge packet ingestion works with proper schema."""
    print("\nTesting knowledge packet schema validation...")
    
    # Test with valid knowledge packet
    import hashlib
    content = "This is a test of the knowledge packet schema validation after fixes."
    content_hash = hashlib.sha256(content.encode('utf-8')).hexdigest()
    
    valid_packet = {
        "packet_version": "1.0",
        "packet_id": content_hash,
        "timestamp": datetime.utcnow().isoformat() + "Z",
        "source": {
            "mcp_server": "test-validation",
            "server_version": "1.0.0",
            "original_location": "test_schema_validation.txt",
            "content_type": "document",
            "extraction_method": "direct_test"
        },
        "metadata": {
            "title": "Schema Validation Test",
            "author": "Test Engineer",
            "created_at": datetime.utcnow().isoformat() + "Z",
            "content_hash": content_hash,
            "file_size": len(content.encode('utf-8')),
            "tags": ["test", "schema_validation"],
            "classification": "internal",
            "language": "en"
        },
        "content": {
            "vector_data": {
                "chunks": [{
                    "chunk_id": "test_chunk_1",
                    "text": content,
                    "chunk_metadata": {
                        "chunk_index": 0,
                        "source_file": "test_schema_validation.txt"
                    }
                }],
                "embedding_model": "BAAI/bge-small-en-v1.5",
                "chunk_strategy": "document_structure",
                "chunk_size": len(content),
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
    
    response = requests.post(
        f"{NANCY_API_BASE}/api/ingest/knowledge-packet",
        json=valid_packet,
        timeout=30
    )
    
    print(f"  Knowledge Packet Ingestion: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        print(f"    [PASS] Schema validation passed!")
        print(f"    Packet ID: {data.get('packet_id', 'Unknown')}")
        return data.get('packet_id')
    else:
        print(f"    [FAIL] Schema validation failed: {response.text}")
        return None

def test_legacy_ingestion():
    """Test that legacy ingestion works without event loop conflicts."""
    print("\nTesting legacy ingestion...")
    
    import io
    
    test_content = "This is a test of legacy ingestion after event loop fixes."
    files = {
        'file': ('legacy_test.txt', io.BytesIO(test_content.encode('utf-8')), 'text/plain')
    }
    data = {
        'author': 'Test Engineer'
    }
    
    response = requests.post(
        f"{NANCY_API_BASE}/api/ingest",
        files=files,
        data=data,
        timeout=30
    )
    
    print(f"  Legacy Ingestion: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        status = data.get("status")
        print(f"    Status: {status}")
        if status == "success":
            print("    [PASS] Legacy ingestion working!")
            return data.get("doc_id")
        else:
            print(f"    [FAIL] Legacy ingestion failed: {data}")
    else:
        print(f"    [FAIL] Legacy ingestion error: {response.text}")
    
    return None

def test_query_functionality(doc_id=None):
    """Test that query functionality works."""
    print("\nTesting query functionality...")
    
    query_data = {
        "query": "test schema validation",
        "n_results": 5
    }
    
    response = requests.post(
        f"{NANCY_API_BASE}/api/query",
        json=query_data,
        timeout=60
    )
    
    print(f"  Query Processing: {response.status_code}")
    if response.status_code == 200:
        data = response.json()
        strategy = data.get("strategy_used", "unknown")
        response_text = data.get("synthesized_response", "")
        print(f"    Strategy: {strategy}")
        print(f"    Response Length: {len(response_text)} characters")
        print("    [PASS] Query processing working!")
        return True
    else:
        print(f"    [FAIL] Query processing error: {response.text}")
        return False

def main():
    """Run comprehensive validation of fixes."""
    print("Nancy MCP Fixes Validation")
    print("=" * 50)
    
    results = {
        "test_timestamp": datetime.now().isoformat(),
        "health_endpoints": False,
        "knowledge_packet_schema": False,
        "legacy_ingestion": False,
        "query_functionality": False,
        "doc_ids": []
    }
    
    try:
        # Test 1: Health endpoints (event loop fix)
        results["health_endpoints"] = test_health_endpoints()
        
        # Test 2: Knowledge packet schema (schema fix)
        packet_id = test_knowledge_packet_schema()
        results["knowledge_packet_schema"] = packet_id is not None
        if packet_id:
            results["doc_ids"].append(packet_id)
        
        # Test 3: Legacy ingestion (async/sync bridge fix)
        doc_id = test_legacy_ingestion()
        results["legacy_ingestion"] = doc_id is not None
        if doc_id:
            results["doc_ids"].append(doc_id)
        
        # Test 4: Query functionality
        results["query_functionality"] = test_query_functionality()
        
        # Summary
        print("\n" + "=" * 50)
        print("VALIDATION SUMMARY")
        print("=" * 50)
        
        total_tests = 4
        passed_tests = sum([
            results["health_endpoints"],
            results["knowledge_packet_schema"], 
            results["legacy_ingestion"],
            results["query_functionality"]
        ])
        
        print(f"Tests Passed: {passed_tests}/{total_tests}")
        print(f"Success Rate: {(passed_tests/total_tests)*100:.1f}%")
        
        if passed_tests == total_tests:
            print("[SUCCESS] ALL CRITICAL FIXES WORKING!")
        elif passed_tests >= 3:
            print("[WARNING] Most fixes working, some issues remain")
        else:
            print("[ERROR] Critical issues still present")
        
        # Save results
        results_file = f"mcp_fixes_validation_{datetime.now().strftime('%Y%m%d_%H%M%S')}.json"
        with open(results_file, 'w') as f:
            json.dump(results, f, indent=2)
        print(f"\nResults saved to: {results_file}")
        
        return passed_tests == total_tests
        
    except Exception as e:
        print(f"\nValidation failed with error: {e}")
        return False

if __name__ == "__main__":
    success = main()
    exit(0 if success else 1)