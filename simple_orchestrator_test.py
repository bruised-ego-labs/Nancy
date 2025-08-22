#!/usr/bin/env python3
"""
Simple test of the nancy-memory MCP server orchestrator fix.
"""

import sys
import os

# Add the nancy-memory MCP server to path
sys.path.append(os.path.join(os.path.dirname(__file__), 'mcp-servers', 'nancy-memory'))

def test_orchestrator_detection():
    """Test orchestrator detection with sample responses"""
    
    print("Testing Nancy MCP Server Orchestrator Detection")
    print("=" * 50)
    
    # Import the NancyMemoryMCP class
    try:
        from server import NancyMemoryMCP
        print("Successfully imported NancyMemoryMCP")
    except ImportError as e:
        print(f"Failed to import NancyMemoryMCP: {e}")
        return False
    
    # Create MCP server instance
    mcp_server = NancyMemoryMCP("http://localhost:8000")
    
    # Test case 1: Intelligent orchestrator response
    intelligent_response = {
        "synthesized_response": "This is the synthesized response",
        "raw_results": [{"text": "sample content", "metadata": {}}],
        "intent_analysis": {"confidence": 0.8}
    }
    
    orchestrator_type = mcp_server._detect_orchestrator_type(intelligent_response)
    print(f"Intelligent response detected as: {orchestrator_type}")
    
    if orchestrator_type == "intelligent":
        extracted_data = mcp_server._extract_response_data(intelligent_response, orchestrator_type)
        print(f"  Response extracted: {len(extracted_data['response'])} chars")
        print(f"  Sources found: {len(extracted_data['sources'])}")
        print("  PASS: Intelligent orchestrator detection works")
    else:
        print("  FAIL: Intelligent orchestrator not detected correctly")
        return False
    
    # Test case 2: LangChain orchestrator response
    langchain_response = {
        "response": "This is the langchain response",
        "routing_info": {"selected_brain": "vector_brain", "confidence": 0.9}
    }
    
    orchestrator_type = mcp_server._detect_orchestrator_type(langchain_response)
    print(f"LangChain response detected as: {orchestrator_type}")
    
    if orchestrator_type == "langchain":
        extracted_data = mcp_server._extract_response_data(langchain_response, orchestrator_type)
        print(f"  Response extracted: {len(extracted_data['response'])} chars")
        print("  PASS: LangChain orchestrator detection works")
    else:
        print("  FAIL: LangChain orchestrator not detected correctly")
        return False
    
    # Test case 3: Enhanced orchestrator response
    enhanced_response = {
        "strategy_used": "relationship_first",
        "results": [{"content": "enhanced content", "metadata": {}}]
    }
    
    orchestrator_type = mcp_server._detect_orchestrator_type(enhanced_response)
    print(f"Enhanced response detected as: {orchestrator_type}")
    
    if orchestrator_type == "enhanced":
        extracted_data = mcp_server._extract_response_data(enhanced_response, orchestrator_type)
        print(f"  Response extracted: {len(extracted_data['response'])} chars")
        print("  PASS: Enhanced orchestrator detection works")
    else:
        print("  FAIL: Enhanced orchestrator not detected correctly")
        return False
    
    # Test case 4: Unknown format
    unknown_response = {"weird_field": "unexpected"}
    
    orchestrator_type = mcp_server._detect_orchestrator_type(unknown_response)
    print(f"Unknown response detected as: {orchestrator_type}")
    
    if orchestrator_type == "unknown":
        extracted_data = mcp_server._extract_response_data(unknown_response, orchestrator_type)
        print(f"  Fallback response: {extracted_data['response']}")
        print("  PASS: Unknown format fallback works")
    else:
        print("  FAIL: Unknown format not handled correctly")
        return False
    
    print("\nAll orchestrator detection tests PASSED!")
    return True

def main():
    """Run the test"""
    if test_orchestrator_detection():
        print("\nOrchestrator fix validation SUCCESSFUL!")
        return 0
    else:
        print("\nOrchestrator fix validation FAILED!")
        return 1

if __name__ == "__main__":
    sys.exit(main())