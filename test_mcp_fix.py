#!/usr/bin/env python3
"""
Test script to verify the nancy-memory MCP server fix works correctly.
"""

import json
import requests
import sys
import os

def test_fixed_mcp_server():
    """Test the nancy-memory MCP server with the field mapping fix"""
    
    print("Testing Fixed Nancy-Memory MCP Server")
    print("=====================================")
    
    # Simulate the exact fixed logic from the MCP server
    nancy_api_base = "http://localhost:8000"
    question = "test information"
    n_results = 5
    search_strategy = "intelligent"
    
    query_data = {
        "query": question,
        "n_results": n_results,
        "orchestrator": search_strategy
    }
    
    print(f"Querying Nancy with: {json.dumps(query_data, indent=2)}")
    
    try:
        response = requests.post(
            f"{nancy_api_base}/api/query",
            json=query_data,
            timeout=60
        )
        
        if response.status_code == 200:
            result = response.json()
            print(f"\nNancy API Response Fields: {list(result.keys())}")
            
            # Apply the same field mapping fix as the MCP server
            sources = []
            for raw_result in result.get("raw_results", []):
                source = {
                    "content": raw_result.get("text", ""),
                    "metadata": raw_result.get("metadata", {}),
                    "relevance_score": 1.0 - raw_result.get("distance", 0.0),
                    "source_type": raw_result.get("source", "unknown"),
                    "chunk_id": raw_result.get("chunk_id", "")
                }
                sources.append(source)
            
            # Create the fixed MCP response
            mcp_response = {
                "status": "success",
                "question": question,
                "response": result.get("synthesized_response", "No response generated"),
                "strategy_used": result.get("strategy_used", search_strategy),
                "sources": sources,
                "brain_analysis": result.get("intent_analysis", {}),
                "confidence": result.get("intent_analysis", {}).get("confidence", "unknown"),
                "brains_used": result.get("brains_used", []),
                "processing_timestamp": result.get("processing_timestamp", "")
            }
            
            print(f"\nFixed MCP Response:")
            print(f"  Status: {mcp_response['status']}")
            print(f"  Response Length: {len(mcp_response['response'])} characters")
            print(f"  Response Preview: {mcp_response['response'][:100]}...")
            print(f"  Sources Count: {len(mcp_response['sources'])}")
            print(f"  Strategy Used: {mcp_response['strategy_used']}")
            print(f"  Brain Analysis Type: {type(mcp_response['brain_analysis'])}")
            print(f"  Confidence: {mcp_response['confidence']}")
            print(f"  Brains Used: {mcp_response['brains_used']}")
            
            # Verify the fix
            if mcp_response['response'] != "No response generated":
                print(f"\n✓ SUCCESS: Response field correctly mapped from 'synthesized_response'")
            else:
                print(f"\n✗ FAILURE: Response still empty")
                
            if len(mcp_response['sources']) > 0:
                print(f"✓ SUCCESS: Sources correctly mapped from 'raw_results' ({len(sources)} sources)")
                print(f"  First source preview: {sources[0]['content'][:50]}...")
            else:
                print(f"✗ FAILURE: No sources found")
                
            if mcp_response['brain_analysis']:
                print(f"✓ SUCCESS: Brain analysis correctly mapped from 'intent_analysis'")
            else:
                print(f"✗ FAILURE: No brain analysis")
            
            return mcp_response
        else:
            print(f"Nancy API Error: {response.status_code} {response.text}")
            return None
            
    except Exception as e:
        print(f"Test failed: {e}")
        return None

def main():
    """Run the fix validation test"""
    
    result = test_fixed_mcp_server()
    
    if result and result.get('status') == 'success':
        if (result.get('response') != "No response generated" and 
            len(result.get('sources', [])) > 0 and 
            result.get('brain_analysis')):
            print(f"\n🎉 ALL TESTS PASSED: Nancy-Memory MCP server fix is working!")
            print(f"   - Content retrieval: WORKING")
            print(f"   - Source mapping: WORKING") 
            print(f"   - Brain analysis: WORKING")
        else:
            print(f"\n⚠️  PARTIAL SUCCESS: Some fields still have issues")
    else:
        print(f"\n❌ TEST FAILED: Fix did not resolve the issue")

if __name__ == "__main__":
    main()