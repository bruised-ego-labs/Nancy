#!/usr/bin/env python3
"""
Debug script to isolate nancy-memory MCP server query issues.
Tests the direct API calls that the MCP server makes to Nancy.
"""

import json
import requests
import sys
import os

def test_nancy_query_direct():
    """Test Nancy's direct query API exactly as the MCP server calls it"""
    
    nancy_api_base = "http://localhost:8000"
    
    print("=== Testing Nancy Direct Query API ===")
    
    # Test the exact query data structure used by the MCP server
    query_data = {
        "query": "test information",
        "n_results": 5,
        "orchestrator": "intelligent"
    }
    
    print(f"Query data: {json.dumps(query_data, indent=2)}")
    print()
    
    try:
        response = requests.post(
            f"{nancy_api_base}/api/query",
            json=query_data,
            timeout=60
        )
        
        print(f"Response status: {response.status_code}")
        print(f"Response headers: {dict(response.headers)}")
        
        if response.status_code == 200:
            result = response.json()
            print(f"Response keys: {list(result.keys())}")
            
            # Check the specific fields the MCP server looks for
            print(f"\nMCP Server Field Analysis:")
            print(f"  response: {result.get('response', 'MISSING')[:100]}...")
            print(f"  strategy_used: {result.get('strategy_used', 'MISSING')}")
            print(f"  sources: {len(result.get('sources', []))} sources")
            print(f"  brain_analysis: {type(result.get('brain_analysis', 'MISSING'))}")
            print(f"  confidence: {result.get('confidence', 'MISSING')}")
            
            # Show the full response structure for comparison
            print(f"\nFull response structure:")
            for key, value in result.items():
                if key == 'raw_results':
                    print(f"  {key}: {len(value)} results")
                elif key == 'synthesized_response':
                    print(f"  {key}: {len(value)} characters")
                else:
                    print(f"  {key}: {value}")
            
            return True
        else:
            print(f"Error response: {response.text}")
            return False
            
    except Exception as e:
        print(f"Request failed: {e}")
        return False

def test_mcp_server_query_simulation():
    """Simulate exactly what the MCP server does in query_memory"""
    
    print("\n=== Simulating MCP Server Query Logic ===")
    
    nancy_api_base = "http://localhost:8000"
    
    # Exact parameters from MCP server
    question = "test information"
    n_results = 5
    search_strategy = "intelligent"
    
    # Exact query_data construction from MCP server
    query_data = {
        "query": question,
        "n_results": n_results,
        "orchestrator": search_strategy
    }
    
    print(f"Simulating MCP query with data: {json.dumps(query_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{nancy_api_base}/api/query",
            json=query_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            
            # Exact MCP server response construction
            mcp_response = {
                "status": "success",
                "question": question,
                "response": result.get("response", "No response generated"),
                "strategy_used": result.get("strategy_used", search_strategy),
                "sources": result.get("sources", []),
                "brain_analysis": result.get("brain_analysis", {}),
                "confidence": result.get("confidence", "unknown")
            }
            
            print(f"\nMCP Response would be:")
            print(json.dumps(mcp_response, indent=2))
            
            # Check for the specific issue
            if mcp_response["response"] == "No response generated":
                print(f"\n❌ ISSUE FOUND: Nancy API returned no 'response' field")
                print(f"Available fields: {list(result.keys())}")
            else:
                print(f"\n✅ Response field looks good: {len(mcp_response['response'])} characters")
            
            return mcp_response
        else:
            print(f"HTTP Error: {response.status_code} {response.text}")
            return None
            
    except Exception as e:
        print(f"Simulation failed: {e}")
        return None

def main():
    """Run all debug tests"""
    
    print("Nancy-Memory MCP Server Query Debug")
    print("===================================")
    
    # Test 1: Direct Nancy API
    if test_nancy_query_direct():
        print("\n✅ Nancy direct API test passed")
    else:
        print("\n❌ Nancy direct API test failed")
        return
    
    # Test 2: MCP simulation
    mcp_result = test_mcp_server_query_simulation()
    if mcp_result:
        print("\n✅ MCP simulation completed")
        
        # Check for specific issues
        if mcp_result.get("response") == "No response generated":
            print("\n🔍 DIAGNOSIS: The issue is that Nancy's API returns 'synthesized_response'")
            print("   but the MCP server looks for 'response'. Field name mismatch!")
        elif not mcp_result.get("sources"):
            print("\n🔍 DIAGNOSIS: No sources returned")
        elif not mcp_result.get("brain_analysis"):
            print("\n🔍 DIAGNOSIS: No brain_analysis returned")
        else:
            print("\n🔍 DIAGNOSIS: MCP response looks correct, issue may be elsewhere")
    else:
        print("\n❌ MCP simulation failed")

if __name__ == "__main__":
    main()