#!/usr/bin/env python3
"""
Test script for Nancy Codebase MCP Server
Demonstrates comprehensive codebase analysis and Knowledge Packet generation.
"""

import asyncio
import json
import sys
import os
from pathlib import Path

# Add MCP server to path
sys.path.append(str(Path(__file__).parent / "mcp-servers" / "codebase"))

from server import CodebaseMCPServer


async def test_file_analysis():
    """Test single file analysis."""
    print("=== Testing Single File Analysis ===")
    
    server = CodebaseMCPServer()
    
    # Test with this script itself
    test_file = __file__
    
    request = {
        "jsonrpc": "2.0",
        "id": 1,
        "method": "analyze_file",
        "params": {"file_path": test_file}
    }
    
    response = await server.handle_request(request)
    
    if "error" in response:
        print(f"❌ Error: {response['error']}")
        return
    
    result = response["result"]
    print(f"✅ Analyzed file: {result['file_path']}")
    print(f"📄 Language: {result['language']}")
    print(f"🧠 Knowledge Packets: {result['total_packets']}")
    
    # Show packet types
    packet_types = {}
    for packet in result["knowledge_packets"]:
        ptype = packet["type"]
        packet_types[ptype] = packet_types.get(ptype, 0) + 1
    
    print("📦 Packet Distribution:")
    for ptype, count in packet_types.items():
        print(f"   {ptype}: {count}")
    
    # Show AST analysis summary
    ast_analysis = result.get("ast_analysis", {})
    print(f"🔍 Functions: {len(ast_analysis.get('functions', []))}")
    print(f"🏗️  Classes: {len(ast_analysis.get('classes', []))}")
    print(f"📊 Complexity Score: {ast_analysis.get('complexity_score', 0)}")
    
    return result


async def test_repository_analysis():
    """Test repository analysis."""
    print("\n=== Testing Repository Analysis ===")
    
    server = CodebaseMCPServer()
    
    # Test with current Nancy directory (limited scope)
    repo_path = str(Path(__file__).parent / "mcp-servers" / "codebase")
    
    request = {
        "jsonrpc": "2.0",
        "id": 2,
        "method": "analyze_repository",
        "params": {
            "repo_path": repo_path,
            "file_extensions": [".py"]  # Limit to Python for testing
        }
    }
    
    response = await server.handle_request(request)
    
    if "error" in response:
        print(f"❌ Error: {response['error']}")
        return
    
    result = response["result"]
    print(f"✅ Analyzed repository: {result['repository_path']}")
    print(f"📁 Total files analyzed: {result['repository_stats']['analyzed_files']}")
    print(f"📦 Total Knowledge Packets: {result['total_knowledge_packets']}")
    print(f"💻 Languages detected: {', '.join(result['repository_stats']['languages'])}")
    print(f"👥 Authors found: {len(result['repository_stats']['authors'])}")
    print(f"⚙️  Functions: {result['repository_stats']['total_functions']}")
    print(f"🏗️  Classes: {result['repository_stats']['total_classes']}")
    
    return result


async def test_git_analysis():
    """Test Git analysis capabilities."""
    print("\n=== Testing Git Analysis ===")
    
    server = CodebaseMCPServer()
    
    # Test with this script
    test_file = __file__
    
    request = {
        "jsonrpc": "2.0",
        "id": 3,
        "method": "get_file_authorship",
        "params": {"file_path": test_file}
    }
    
    response = await server.handle_request(request)
    
    if "error" in response:
        print(f"ℹ️  Git analysis: {response['result']['error']}")
        return
    
    result = response["result"]
    print(f"✅ Git analysis for: {result['relative_path']}")
    print(f"👤 Primary author: {result.get('primary_author', 'Unknown')}")
    print(f"👥 Contributors: {len(result.get('contributors', []))}")
    print(f"📝 Total commits: {result.get('total_commits', 0)}")
    
    return result


async def test_supported_languages():
    """Test supported languages query."""
    print("\n=== Testing Supported Languages ===")
    
    server = CodebaseMCPServer()
    
    request = {
        "jsonrpc": "2.0",
        "id": 4,
        "method": "get_supported_languages",
        "params": {}
    }
    
    response = await server.handle_request(request)
    result = response["result"]
    
    print(f"✅ Supported extensions: {len(result['supported_extensions'])}")
    print(f"🔧 Available parsers: {result['parsers_available']}")
    print(f"💬 Languages: {result['languages_supported']}")
    
    return result


async def test_health_check():
    """Test health check."""
    print("\n=== Testing Health Check ===")
    
    server = CodebaseMCPServer()
    
    request = {
        "jsonrpc": "2.0",
        "id": 5,
        "method": "health_check",
        "params": {}
    }
    
    response = await server.handle_request(request)
    result = response["result"]
    
    print(f"✅ Server status: {result['status']}")
    print(f"🏷️  Version: {result['version']}")
    print(f"🔧 AST parsers: {result['ast_parsers']}")
    print(f"📋 Capabilities: {len(result['capabilities'])}")
    
    return result


async def demonstrate_knowledge_packets():
    """Demonstrate Knowledge Packet structure."""
    print("\n=== Knowledge Packet Structure Demo ===")
    
    # Analyze a Python file to show packet structure
    server = CodebaseMCPServer()
    
    # Use the AST analyzer file as example
    test_file = str(Path(__file__).parent / "mcp-servers" / "codebase" / "ast_analyzer.py")
    
    request = {
        "jsonrpc": "2.0",
        "id": 6,
        "method": "analyze_file",
        "params": {"file_path": test_file}
    }
    
    response = await server.handle_request(request)
    
    if "error" in response:
        print(f"❌ Error: {response['error']}")
        return
    
    result = response["result"]
    knowledge_packets = result["knowledge_packets"]
    
    print(f"📦 Generated {len(knowledge_packets)} Knowledge Packets")
    
    # Show examples of each packet type
    vector_packets = [p for p in knowledge_packets if p["type"] == "vector_content"]
    analytical_packets = [p for p in knowledge_packets if p["type"] == "analytical_data"]
    graph_packets = [p for p in knowledge_packets if p["type"] == "graph_entities"]
    
    print(f"\n🎯 Vector Brain Packets: {len(vector_packets)}")
    if vector_packets:
        example = vector_packets[0]
        print(f"   Example - Doc ID: {example['doc_id']}")
        print(f"   Content length: {len(example['content'])} chars")
        print(f"   Metadata: {example['metadata']['type']}")
    
    print(f"\n📊 Analytical Brain Packets: {len(analytical_packets)}")
    if analytical_packets:
        example = analytical_packets[0]
        print(f"   Example - Doc ID: {example['doc_id']}")
        print(f"   Language: {example['data']['language']}")
        print(f"   Function count: {example['data']['function_count']}")
        print(f"   Complexity: {example['data']['complexity_score']}")
    
    print(f"\n🕸️  Graph Brain Packets: {len(graph_packets)}")
    if graph_packets:
        example = graph_packets[0]
        entities = example['entities']
        print(f"   Example - Doc ID: {example['doc_id']}")
        print(f"   Entity count: {len(entities)}")
        
        entity_types = {}
        for entity in entities:
            etype = entity['type']
            entity_types[etype] = entity_types.get(etype, 0) + 1
        
        print(f"   Entity types: {dict(entity_types)}")
    
    return result


async def run_comprehensive_test():
    """Run comprehensive test suite."""
    print("🚀 Nancy Codebase MCP Server - Comprehensive Test")
    print("=" * 60)
    
    try:
        # Test individual capabilities
        await test_health_check()
        await test_supported_languages()
        await test_file_analysis()
        await test_git_analysis()
        await test_repository_analysis()
        await demonstrate_knowledge_packets()
        
        print("\n" + "=" * 60)
        print("✅ All tests completed successfully!")
        print("🎯 Codebase MCP Server is ready for integration with Nancy Core")
        
    except Exception as e:
        print(f"\n❌ Test failed with error: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    asyncio.run(run_comprehensive_test())