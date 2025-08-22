#!/usr/bin/env python3
"""
Test the fixed MCP server logic with string metadata handling
"""

import json
import logging
from typing import Dict, Any, Optional

# Configure logging
logging.basicConfig(level=logging.INFO, format='%(asctime)s - %(name)s - %(levelname)s - %(message)s')
logger = logging.getLogger("fixed-mcp-test")

def simulate_fixed_ingest_information(
    content: str,
    content_type: str = "text",
    author: str = "AI Assistant", 
    filename: Optional[str] = None,
    metadata: Optional[Dict[str, Any]] = None
) -> Dict[str, Any]:
    """
    Simulate the FIXED ingest_information function with string metadata handling
    """
    
    logger.info(f"Fixed simulate_ingest_information called with:")
    logger.info(f"  content: {content[:50]}...")
    logger.info(f"  content_type: {content_type}")
    logger.info(f"  author: {author}")
    logger.info(f"  filename: {filename}")
    logger.info(f"  metadata: {metadata}")
    logger.info(f"  metadata type: {type(metadata)}")
    
    # Handle metadata parameter - MCP protocol may pass it as JSON string
    if isinstance(metadata, str):
        try:
            metadata = json.loads(metadata)
            logger.info(f"Parsed metadata string to dict: {metadata}")
        except (json.JSONDecodeError, TypeError) as e:
            logger.warning(f"Failed to parse metadata string '{metadata}': {e}")
            metadata = {}
    elif metadata is None:
        metadata = {}
    elif not isinstance(metadata, dict):
        logger.warning(f"Unexpected metadata type {type(metadata)}, using empty dict")
        metadata = {}
    
    # Test the metadata handling that happens in the real MCP server
    try:
        # This is the critical line where metadata gets merged in the real server
        final_metadata = {
            "title": filename or "default.txt",
            "author": author,
            "base_field": "test",
            **(metadata or {})  # This should now work with the fixed metadata
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
            "message": "Fixed parameter handling test passed",
            "metadata_result": final_metadata
        }
        
    except Exception as e:
        logger.error(f"Parameter handling failed: {e}")
        return {
            "status": "error",
            "message": f"Parameter handling failed: {e}",
            "details": "Exception in metadata processing"
        }

def test_fixed_mcp_parameter_handling():
    """Test the fixed MCP server parameter handling"""
    
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
            "name": "String metadata (now should work)",
            "params": {
                "content": "Test content 2", 
                "content_type": "test",
                "author": "Test Author 2",
                "filename": "test2.txt",
                "metadata": '{"key": "value", "number": 42}'
            }
        },
        {
            "name": "Invalid JSON string metadata",
            "params": {
                "content": "Test content 3",
                "content_type": "test",
                "author": "Test Author 3",
                "filename": "test3.txt",
                "metadata": "invalid json {"
            }
        },
        {
            "name": "None metadata",
            "params": {
                "content": "Test content 4",
                "content_type": "test", 
                "author": "Test Author 4",
                "filename": "test4.txt",
                "metadata": None
            }
        },
        {
            "name": "Empty string metadata",
            "params": {
                "content": "Test content 5",
                "content_type": "test",
                "author": "Test Author 5",
                "filename": "test5.txt",
                "metadata": ""
            }
        }
    ]
    
    results = []
    
    for i, test_case in enumerate(test_cases):
        print(f"\n=== Test Case {i+1}: {test_case['name']} ===")
        params = test_case['params']
        
        try:
            result = simulate_fixed_ingest_information(**params)
            print(f"Result: {result['status']}")
            if result['status'] == 'success':
                print(f"Metadata result: {result['metadata_result']}")
            else:
                print(f"Error: {result['message']}")
            results.append(result['status'] == 'success')
            
        except Exception as e:
            print(f"Exception: {e}")
            results.append(False)
    
    return results

if __name__ == "__main__":
    print("Fixed MCP Server Parameter Test\n")
    
    # Test the fixed parameter handling
    results = test_fixed_mcp_parameter_handling()
    
    print("\n" + "="*50)
    print("Summary:")
    for i, result in enumerate(results, 1):
        print(f"Test {i}: {'PASSED' if result else 'FAILED'}")
    
    all_passed = all(results)
    print(f"\nOverall: {'ALL TESTS PASSED' if all_passed else 'SOME TESTS FAILED'}")
    
    if all_passed:
        print("\nThe fix should resolve the MCP protocol metadata issue!")
        print("The nancy-memory MCP server can now handle string metadata from MCP protocol.")