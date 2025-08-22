#!/usr/bin/env python3
"""
Minimal MCP server test to isolate the parameter passing issue
"""

import json
import logging
from typing import Dict, Any, Optional

# Configure logging to see what's happening
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("minimal-mcp-test")

def test_mcp_parameter_handling():
    """Test how MCP server handles parameters in isolation"""
    
    # These are the exact parameters that should be passed to ingest_information
    test_cases = [
        {
            "name": "Normal dict metadata",
            "params": {
                "content": "Test content 1",
                "content_type": "test",
                "author": "Test Author 1",
                "filename": "test1.txt",
                "metadata": {"key": "value", "number": 42}
            }
        },
        {
            "name": "String metadata (potential serialization issue)",
            "params": {
                "content": "Test content 2", 
                "content_type": "test",
                "author": "Test Author 2",
                "filename": "test2.txt",
                "metadata": '{"key": "value", "number": 42}'
            }
        },
        {
            "name": "None metadata",
            "params": {
                "content": "Test content 3",
                "content_type": "test", 
                "author": "Test Author 3",
                "filename": "test3.txt",
                "metadata": None
            }
        },
        {
            "name": "Missing metadata",
            "params": {
                "content": "Test content 4",
                "content_type": "test",
                "author": "Test Author 4", 
                "filename": "test4.txt"
                # metadata not provided
            }
        }
    ]
    
    for i, test_case in enumerate(test_cases):
        print(f"\n=== Test Case {i+1}: {test_case['name']} ===")
        params = test_case['params']
        
        try:
            # Simulate what the MCP server's ingest_information function does
            result = simulate_ingest_information(**params)
            print(f"Result: {result}")
            
        except Exception as e:
            print(f"Exception: {e}")
            import traceback
            traceback.print_exc()

def simulate_ingest_information(
    content: str,
    content_type: str = "text",
    author: str = "AI Assistant", 
    filename: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Simulate the ingest_information function to test parameter handling
    """
    
    logger.info(f"simulate_ingest_information called with:")
    logger.info(f"  content: {content[:50]}...")
    logger.info(f"  content_type: {content_type}")
    logger.info(f"  author: {author}")
    logger.info(f"  filename: {filename}")
    logger.info(f"  metadata: {metadata}")
    logger.info(f"  metadata type: {type(metadata)}")
    
    # Test the metadata handling that happens in the real MCP server
    try:
        # This is the critical line where metadata gets merged in the real server
        final_metadata = {
            "title": filename or "default.txt",
            "author": author,
            "base_field": "test",
            **(metadata or {})  # This line could fail if metadata is wrong type
        }
        
        logger.info(f"Metadata merge successful: {final_metadata}")
        
        # Test JSON serialization (this happens when sending to Nancy API)
        try:
            json_test = json.dumps(final_metadata)
            logger.info(f"JSON serialization successful: {len(json_test)} chars")
        except Exception as json_e:
            logger.error(f"JSON serialization failed: {json_e}")
            raise
        
        return {
            "status": "success",
            "message": "Parameter handling test passed",
            "metadata_result": final_metadata
        }
        
    except Exception as e:
        logger.error(f"Parameter handling failed: {e}")
        return {
            "status": "error",
            "message": f"Parameter handling failed: {e}",
            "details": "Exception in metadata processing"
        }

def test_json_serialization_edge_cases():
    """Test JSON serialization edge cases that might occur in MCP protocol"""
    
    print("\n=== JSON Serialization Edge Cases ===")
    
    test_objects = [
        {"name": "Normal dict", "obj": {"key": "value", "num": 42}},
        {"name": "JSON string", "obj": '{"key": "value", "num": 42}'},
        {"name": "None", "obj": None},
        {"name": "Empty dict", "obj": {}},
        {"name": "Nested dict", "obj": {"outer": {"inner": "value"}}},
        {"name": "List values", "obj": {"tags": ["tag1", "tag2"], "numbers": [1, 2, 3]}},
        {"name": "Boolean values", "obj": {"debug": True, "enabled": False}},
    ]
    
    for test in test_objects:
        try:
            # Test serialization
            serialized = json.dumps(test["obj"])
            # Test deserialization  
            deserialized = json.loads(serialized)
            print(f"{test['name']}: ✓ {deserialized}")
        except Exception as e:
            print(f"{test['name']}: ✗ {e}")

if __name__ == "__main__":
    print("Minimal MCP Server Parameter Test\n")
    
    # Test parameter handling
    test_mcp_parameter_handling()
    
    # Test JSON serialization
    test_json_serialization_edge_cases()
    
    print("\n" + "="*50)
    print("If all tests pass, the issue is likely in the MCP protocol communication layer")
    print("between Claude Code (MCP client) and the nancy-memory MCP server.")