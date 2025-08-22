#!/usr/bin/env python3
"""
Test the nancy-memory MCP server fix against live Nancy API
"""

import sys
import os
import json
import requests
import time

# Add the nancy-memory MCP server to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'mcp-servers', 'nancy-memory'))

def test_live_nancy_orchestrators():
    """Test all orchestrator types against live Nancy API"""
    
    print("Testing Nancy MCP Server Fix Against Live Nancy API")
    print("=" * 55)
    
    # Import the fixed MCP server
    try:
        from server import NancyMemoryMCP
        print("Successfully imported fixed NancyMemoryMCP")
    except ImportError as e:
        print(f"Failed to import NancyMemoryMCP: {e}")
        return False
    
    # Create MCP server instance
    mcp_server = NancyMemoryMCP("http://localhost:8000")
    
    # Test queries for each orchestrator
    test_cases = [
        ("intelligent", "What information is available?"),
        ("langchain", "Show me system status"),
        ("enhanced", "List available data")
    ]
    
    results = []
    
    for orchestrator, query in test_cases:
        print(f"\nTesting {orchestrator.upper()} orchestrator...")
        
        try:
            # Make direct API call to Nancy
            query_data = {
                "query": query,
                "n_results": 3,
                "orchestrator": orchestrator
            }
            
            response = requests.post(
                "http://localhost:8000/api/query",
                json=query_data,
                timeout=30
            )
            
            if response.status_code != 200:
                print(f"  API call failed: {response.status_code} - {response.text}")
                results.append({"orchestrator": orchestrator, "status": "api_error"})
                continue
            
            # Parse the response
            try:
                nancy_result = response.json()
                print(f"  Nancy API response keys: {list(nancy_result.keys())}")
            except ValueError:
                print(f"  Invalid JSON response from Nancy")
                results.append({"orchestrator": orchestrator, "status": "json_error"})
                continue
            
            # Test the fixed MCP server detection and extraction
            detected_type = mcp_server._detect_orchestrator_type(nancy_result)
            print(f"  Detected orchestrator type: {detected_type}")
            
            # Extract data using the fixed methods
            extracted_data = mcp_server._extract_response_data(nancy_result, detected_type)
            
            # Validate the extraction
            response_text = extracted_data.get("response", "")
            sources = extracted_data.get("sources", [])
            strategy = extracted_data.get("strategy_used", "")
            
            print(f"  Response length: {len(response_text)} characters")
            print(f"  Sources found: {len(sources)}")
            print(f"  Strategy used: {strategy}")
            
            # Check if we got a meaningful response
            if response_text and response_text != "No response generated":
                print(f"  SUCCESS: Got meaningful response from {orchestrator}")
                print(f"  Response preview: {response_text[:100]}...")
                
                results.append({
                    "orchestrator": orchestrator,
                    "requested": orchestrator,
                    "detected": detected_type,
                    "status": "success",
                    "response_length": len(response_text),
                    "sources_count": len(sources),
                    "has_content": bool(response_text.strip())
                })
            else:
                print(f"  WARNING: Empty or default response from {orchestrator}")
                results.append({
                    "orchestrator": orchestrator,
                    "requested": orchestrator,
                    "detected": detected_type,
                    "status": "empty_response",
                    "response_length": len(response_text),
                    "sources_count": len(sources)
                })
                
        except Exception as e:
            print(f"  ERROR testing {orchestrator}: {str(e)}")
            results.append({"orchestrator": orchestrator, "status": "error", "error": str(e)})
        
        # Rate limiting
        time.sleep(2)
    
    # Analyze results
    print(f"\n" + "=" * 55)
    print("LIVE TEST RESULTS SUMMARY:")
    
    successful_tests = [r for r in results if r["status"] == "success"]
    total_tests = len(results)
    
    print(f"Total orchestrators tested: {total_tests}")
    print(f"Successful extractions: {len(successful_tests)}")
    print(f"Success rate: {len(successful_tests)/total_tests*100:.1f}%")
    
    for result in results:
        orchestrator = result["orchestrator"]
        status = result["status"]
        
        if status == "success":
            detected = result.get("detected", "unknown")
            response_len = result.get("response_length", 0)
            print(f"  {orchestrator}: SUCCESS - detected as {detected}, {response_len} chars")
        else:
            print(f"  {orchestrator}: {status.upper()}")
    
    # Determine overall success
    if len(successful_tests) >= 2:  # At least 2 out of 3 should work
        print(f"\nOVERALL: LIVE TEST PASSED!")
        print("The nancy-memory MCP server fix is working with live Nancy API!")
        return True
    else:
        print(f"\nOVERALL: LIVE TEST FAILED!")
        print("The fix may need additional work for live scenarios.")
        return False

def main():
    """Run the live test"""
    
    # Check if Nancy is running
    try:
        response = requests.get("http://localhost:8000/health", timeout=5)
        if response.status_code != 200:
            print("Nancy API is not accessible. Please start Nancy with: docker-compose up -d")
            return 1
    except:
        print("Nancy API is not accessible. Please start Nancy with: docker-compose up -d")
        return 1
    
    if test_live_nancy_orchestrators():
        return 0
    else:
        return 1

if __name__ == "__main__":
    sys.exit(main())